#!/usr/bin/env python3
"""Validate an ADR file against the write-adr grammar.

Spec: docs/specs/workflow/02-write-adr.md.
Stdlib only, Python 3.9+. Exit 0 pass; 1 violations ("path:line: message"
on stderr); 2 usage/environment errors.
"""
import os
import re
import sys

STATUSES = {"proposed", "accepted", "rejected", "superseded"}
FROZEN = {"accepted", "rejected", "superseded"}
DRAFT_RE = re.compile(r"^adr-draft-([a-z0-9][a-z0-9-]*)\.md$")
NUM_RE = re.compile(r"^adr-(\d{3})-([a-z0-9][a-z0-9-]*)\.md$")
REJ_RE = re.compile(r"^adr-rejected-([a-z0-9][a-z0-9-]*)\.md$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
KEY_RE = re.compile(r"^([a-z][a-z-]*): (.+?)\s*$")
NORMATIVE_KEYS = {"status", "created", "decided", "resolves", "supersedes", "superseded-by"}


def parse_frontmatter(lines):
    """Return (keys, body_start_index, errors). keys: name -> (value, line_no)."""
    errors = []
    keys = {}
    if not lines or lines[0].strip() != "---":
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
    elif not DATE_RE.match(keys["created"][0]):
        errs.append((keys["created"][1], "created is not an ISO date"))
    if status == "proposed":
        if "decided" in keys:
            errs.append((keys["decided"][1], "decided is illegal on proposed records"))
    else:
        if "decided" not in keys:
            errs.append((sline, "decided is required once status is '%s'" % status))
        elif not DATE_RE.match(keys["decided"][0]):
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


def validate(path):
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        return ["%s:1: unreadable: %s" % (path, exc)]
    keys, body_start, errs = parse_frontmatter(lines)
    if not any(msg.startswith("file must start") for _, msg in errs):
        check_meta(path, keys, errs)
    return ["%s:%d: %s" % (path, n, msg) for n, msg in sorted(errs)]


def main():
    if len(sys.argv) != 2:
        print("usage: validate_adr.py <adr-file>", file=sys.stderr)
        return 2
    errors = validate(sys.argv[1])
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
