#!/usr/bin/env python3
"""Validate an ADR file against the write-adr grammar.

Spec: docs/specs/workflow/02-write-adr.md.
Stdlib only, Python 3.9+. Exit 0 pass; 1 violations ("path:line: message"
on stderr); 2 usage/environment errors.
"""
import datetime
import os
import re
import sys

STATUSES = {"proposed", "accepted", "rejected", "superseded"}
DRAFT_RE = re.compile(r"^adr-draft-([a-z0-9][a-z0-9-]*)\.md$")
NUM_RE = re.compile(r"^adr-(\d{3})-([a-z0-9][a-z0-9-]*)\.md$")
REJ_RE = re.compile(r"^adr-rejected-([a-z0-9][a-z0-9-]*)\.md$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$", re.ASCII)
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def iso_date(value):
    """Lexical YYYY-MM-DD (the regex) AND a real calendar date (fromisoformat).
    The regex stays authoritative for form: on Python 3.11+ fromisoformat alone
    also accepts compact (20260228) and ISO-week (2026-W09-6) forms."""
    if not DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


KEY_RE = re.compile(r"^([a-z][a-z-]*): (.+?)\s*$")
NORMATIVE_KEYS = {"status", "created", "decided", "resolves", "supersedes", "superseded-by"}


def parse_frontmatter(lines):
    """Return (keys, body_start_index, errors). keys: name -> (value, line_no)."""
    errors = []
    keys = {}
    if not lines or lines[0] != "---":
        errors.append((1, "file must start with '---' frontmatter delimiter"))
        return keys, 0, errors
    i = 1
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            return keys, i + 1, errors
        m = KEY_RE.match(line)
        n = i + 1
        if not m:
            errors.append((n, "frontmatter line is not 'key: value'"))
        else:
            key, val = m.group(1), m.group(2)
            if key in keys and key in NORMATIVE_KEYS:
                errors.append((n, "duplicate key '%s'" % key))
            elif key not in NORMATIVE_KEYS and not key.startswith("x-"):
                errors.append((n, "unknown key '%s' (extensions need the x- prefix)" % key))
            elif key not in keys:
                keys[key] = (val, n)
        i += 1
    errors.append((len(lines), "frontmatter never closed with '---'"))
    return keys, len(lines), errors


def check_meta(path, keys, errs):
    name = os.path.basename(path)
    status = keys.get("status", ("", 0))[0]
    if "status" not in keys:
        errs.append((1, "missing required key 'status'"))
        return
    sline = keys["status"][1]
    if status not in STATUSES:
        errs.append((sline, "illegal status '%s'" % status))
        return
    is_draft, is_num, is_rej = DRAFT_RE.match(name), NUM_RE.match(name), REJ_RE.match(name)
    if status == "proposed" and not is_draft:
        errs.append((sline, "status proposed requires filename adr-draft-<slug>.md"))
    if status in ("accepted", "superseded") and not is_num:
        errs.append((sline, "status %s requires filename adr-NNN-<slug>.md" % status))
    if status == "rejected" and not is_rej:
        errs.append((sline, "status rejected requires filename adr-rejected-<slug>.md"))
    if not (is_draft or is_num or is_rej):
        errs.append((1, "filename matches no ADR naming pattern"))
    if "created" not in keys:
        errs.append((1, "missing required key 'created'"))
    elif not iso_date(keys["created"][0]):
        errs.append((keys["created"][1], "created is not an ISO date"))
    if status == "proposed":
        if "decided" in keys:
            errs.append((keys["decided"][1], "decided is illegal on proposed records"))
    else:
        if "decided" not in keys:
            errs.append((sline, "decided is required once status is '%s'" % status))
        elif not iso_date(keys["decided"][0]):
            errs.append((keys["decided"][1], "decided is not an ISO date"))
    if status == "superseded" and "superseded-by" not in keys:
        errs.append((sline, "status superseded requires superseded-by"))
    if status != "superseded" and "superseded-by" in keys:
        errs.append((keys["superseded-by"][1], "superseded-by is legal only with status superseded"))
    if "resolves" in keys and not SLUG_RE.match(keys["resolves"][0]):
        errs.append((keys["resolves"][1], "resolves is not a kebab-case slug"))
    if is_num:
        num = is_num.group(1)
        directory = os.path.dirname(os.path.abspath(path))
        twins = [f for f in os.listdir(directory)
                 if NUM_RE.match(f) and NUM_RE.match(f).group(1) == num]
        if len(twins) > 1:
            errs.append((1, "number %s is not unique in directory (%s)" % (num, ", ".join(sorted(twins)))))


H1_RE = re.compile(r"^# .+$")
SECTION_ORDER = ["## Context", "## Decision", "## Alternatives Considered", "## Consequences"]
ALT_RE = re.compile(r"^- \*\*.+\*\* — .+$")
NONE_ALT_RE = re.compile(r"^- None — .+$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,})")


def mask_fences(body):
    """Blank fence-interior and fence-delimiter lines for STRUCTURAL recognition only.

    Decision 5 of the review-fix design: a fenced block is content, not structure.
    Heading and bullet checks read the masked copy; non-emptiness reads the original
    lines, so a section whose only content is a code block is still non-empty."""
    masked = []
    fence = 0  # opening backtick-run length, 0 = outside a fence
    for l in body:
        m = FENCE_RE.match(l)
        if fence == 0:
            if m:
                fence = len(m.group(1))
                masked.append("")
            else:
                masked.append(l)
        else:
            masked.append("")
            s = l.strip()
            if s and set(s) == {"`"} and len(s) >= fence:
                fence = 0
    return masked


def check_body(lines, body_start, errs):
    body = lines[body_start:]
    masked = mask_fences(body)
    offset = body_start + 1  # 1-based line number of body[0]
    h1s = [i for i, l in enumerate(masked) if H1_RE.match(l)]
    if len(h1s) != 1:
        errs.append((offset, "body must contain exactly one H1 title"))
    positions = {}
    for i, l in enumerate(masked):
        if l.strip() in SECTION_ORDER:
            if l.strip() in positions:
                errs.append((offset + i, "duplicate section: '%s' appears twice" % l.strip()))
            positions[l.strip()] = i
    for name in SECTION_ORDER:
        if name not in positions:
            errs.append((offset, "missing section '%s'" % name))
    present = [positions[n] for n in SECTION_ORDER if n in positions]
    if present != sorted(present):
        errs.append((offset, "sections out of order (mandated: Context, Decision, Alternatives Considered, Consequences)"))
    if len(h1s) == 1 and positions:
        first_section = min(positions.values())
        if h1s[0] > first_section:
            errs.append((offset + h1s[0], "H1 title must precede all sections"))
    if len(positions) == len(SECTION_ORDER) and present == sorted(present):
        bounds = present + [len(body)]
        for idx, name in enumerate(SECTION_ORDER):
            content = [l for l in body[bounds[idx] + 1:bounds[idx + 1]] if l.strip()]
            if name == "## Alternatives Considered":
                bullets = [(i, l) for i, l in enumerate(masked[bounds[idx] + 1:bounds[idx + 1]], bounds[idx] + 1) if l.startswith("- ")]
                if not bullets:
                    errs.append((offset + bounds[idx], "Alternatives Considered needs at least one alternative or an explicit '- None — <reason>'"))
                for i, l in bullets:
                    if not (ALT_RE.match(l) or NONE_ALT_RE.match(l)):
                        errs.append((offset + i, "alternative bullet lacks an inline rejection reason ('- **…** — …')"))
            elif not content:
                errs.append((offset + bounds[idx], "section '%s' must be non-empty" % name))


def check_pointers(path, keys, errs):
    directory = os.path.dirname(os.path.abspath(path))
    name = os.path.basename(path)
    status = keys.get("status", ("", 0))[0]

    def counterpart(key):
        val, n = keys[key]
        if not NUM_RE.match(val):
            errs.append((n, "%s does not match the numbered filename grammar" % key))
            return None
        target = os.path.join(directory, val)
        if not os.path.exists(target):
            errs.append((n, "%s counterpart '%s' does not exist" % (key, val)))
            return None
        try:
            with open(target, encoding="utf-8") as fh:
                tkeys, _, _ = parse_frontmatter(fh.read().splitlines())
        except (OSError, UnicodeDecodeError):
            errs.append((n, "%s counterpart '%s' is unreadable" % (key, val)))
            return None
        return val, n, tkeys

    if "supersedes" in keys:
        got = counterpart("supersedes")
        if got:
            val, n, tkeys = got
            tstatus = tkeys.get("status", ("", 0))[0]
            if status == "proposed" and tstatus != "accepted":
                errs.append((n, "a proposed successor's supersedes target must be accepted, got '%s'" % tstatus))
            if status in ("accepted", "superseded"):
                if tstatus != "superseded":
                    errs.append((n, "supersedes target must be superseded, got '%s'" % tstatus))
                elif tkeys.get("superseded-by", ("", 0))[0] != name:
                    errs.append((n, "supersedes target's superseded-by does not name this file"))
    if "superseded-by" in keys:
        got = counterpart("superseded-by")
        if got:
            val, n, tkeys = got
            tstatus = tkeys.get("status", ("", 0))[0]
            if tstatus not in ("accepted", "superseded"):
                errs.append((n, "superseded-by target must be accepted or superseded, got '%s'" % tstatus))
            elif tkeys.get("supersedes", ("", 0))[0] != name:
                errs.append((n, "superseded-by target's supersedes does not name this file"))


def validate(path):
    with open(path, encoding="utf-8") as fh:  # OSError propagates: environment, not a violation
        try:
            lines = fh.read().splitlines()
        except UnicodeDecodeError as exc:
            return ["%s:1: unreadable: %s" % (path, exc)]
    keys, body_start, errs = parse_frontmatter(lines)
    if not any(msg.startswith("file must start") for _, msg in errs):
        check_meta(path, keys, errs)
        check_body(lines, body_start, errs)
        check_pointers(path, keys, errs)
    return ["%s:%d: %s" % (path, n, msg) for n, msg in sorted(errs)]


def main():
    if len(sys.argv) != 2:
        print("usage: validate_adr.py <adr-file>", file=sys.stderr)
        return 2
    try:
        errors = validate(sys.argv[1])
    except OSError as exc:
        print("%s: %s" % (sys.argv[1], exc.strerror or exc), file=sys.stderr)
        return 2
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
