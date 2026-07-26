#!/usr/bin/env python3
"""Validate a ROADMAP.md against the doc-driven workflow grammar.

Spec: docs/specs/workflow/04-prd-to-milestones.md.
Stdlib only, Python 3.9+. Exit 0 on pass; exit 1 with one
"path:line: message" per violation on stderr.
"""
import sys
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

MILESTONE_STATES = {
    "planning-pending", "planned", "in-progress", "paused",
    "review-ready", "remediating", "accepted",
}
MIDFLIGHT = {"in-progress", "paused", "review-ready", "remediating"}
FUTURE_OK = {"planning-pending", "planned"}
FEATURE_STATUS = re.compile(
    r"^(todo|WIP|done|blocked\([a-z0-9][a-z0-9-]*\)|failed\(.+\))$")
M_HEAD = re.compile(r"^## (MS-[0-9]{3}) — (.+)$")
F_HEAD = re.compile(r"^### (FEAT-[0-9]{3}) — (.+)$")
KEY = re.compile(r"^- ([A-Z][A-Za-z ]*): ?(.*?)\s*$")
EV_KEY = re.compile(r"^  - ([A-Z][A-Za-z ]*): (.*?)\s*$")
NEAR_MISS = re.compile(r"^#{1,6} (MS|FEAT|M|F)-?[0-9]+\b")
COVERS = re.compile(r"^PRD-([0-9]{3}) REQ-([0-9]{3})(?:, PRD-([0-9]{3}) REQ-([0-9]{3}))*$")
CITATION = re.compile(r"PRD-([0-9]{3}) REQ-([0-9]{3})")
RETIRED_MS = re.compile(r"^MS-([0-9]{3})(?:, MS-([0-9]{3}))*$")
MS_TOKEN = re.compile(r"MS-([0-9]{3})")
PLACEHOLDERS = {"tbd", "todo"}

SUMMARY_REQ = ("Current milestone", "Milestone state", "Active feature", "Next action")
FEATURE_REQ = ("Status", "Description", "Acceptance", "Test intent")
EVIDENCE_REQ = ("Base", "Commits", "Tests", "Reviewer", "Verdict", "Findings")
MILESTONE_REQ = ("State", "Goal", "Covers")
KNOWN_KEYS = set(SUMMARY_REQ) | set(FEATURE_REQ) | set(MILESTONE_REQ) | {"Learning", "Evidence", "Retired milestones"}
ACCEPT_VERDICTS = {"approve", "approve-with-findings"}
FINDINGS = re.compile(
    r"^(none|[^;]+: (fixed|refuted\(.+?\))(; [^;]+: (fixed|refuted\(.+?\)))*)$")
LEARNING = re.compile(r"^docs/learnings/ALI-\d{3}\.md$")
STATUS_HEADING = "## Current Workflow Status"


@dataclass
class Node:
    id: str
    title: str
    line: int
    keys: Dict[str, Tuple[str, int]] = field(default_factory=dict)


@dataclass
class Feature(Node):
    evidence: Dict[str, Tuple[str, int]] = field(default_factory=dict)


@dataclass
class Milestone(Node):
    features: List[Feature] = field(default_factory=list)


def parse(lines):
    errors = []
    summary = None
    milestones = []
    cur = None
    cur_m = None
    in_evidence = False
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if line == STATUS_HEADING:
            if summary is not None:
                errors.append((n, "duplicate '## Current Workflow Status' section"))
                cur, cur_m, in_evidence = None, None, False
                continue
            summary = Node("summary", "Current Workflow Status", n)
            cur, cur_m, in_evidence = summary, None, False
            continue
        m = M_HEAD.match(line)
        if m:
            cur_m = Milestone(m.group(1), m.group(2), n)
            milestones.append(cur_m)
            cur, in_evidence = cur_m, False
            continue
        f = F_HEAD.match(line)
        if f:
            if cur_m is None:
                errors.append((n, "feature %s outside any milestone" % f.group(1)))
                cur = None
                continue
            feat = Feature(f.group(1), f.group(2), n)
            cur_m.features.append(feat)
            cur, in_evidence = feat, False
            continue
        nm = NEAR_MISS.match(line)
        if nm:
            kind = "milestone" if nm.group(1) in ("MS", "M") else "feature"
            expected = "## MS-NNN — <title>" if kind == "milestone" else "### FEAT-NNN — <title>"
            errors.append((n, "malformed %s heading, expected '%s' (three digits, em dash)" % (kind, expected)))
            cur, in_evidence = None, False
            if kind == "milestone":
                cur_m = None
            continue
        if line.startswith("## "):
            cur, cur_m, in_evidence = None, None, False
            continue
        if raw.startswith("  "):
            ev = EV_KEY.match(raw.rstrip())
            if ev and isinstance(cur, Feature) and in_evidence:
                k, v = ev.group(1), ev.group(2)
                if k in cur.evidence:
                    errors.append((n, "duplicate evidence key '%s'" % k))
                else:
                    cur.evidence[k] = (v, n)
                continue
        k = KEY.match(line)
        if k and cur is not None:
            key, val = k.group(1), k.group(2)
            in_evidence = key == "Evidence"
            if key in cur.keys:
                # Known keys: duplicates are errors. Unknown keys: first occurrence stored, later ignored.
                if key in KNOWN_KEYS:
                    errors.append((n, "duplicate key '%s'" % key))
            else:
                cur.keys[key] = (val, n)
            continue
    return summary, milestones, errors


def check_summary(lines, summary, errs):
    first = next((l for l in lines if l.startswith("## ")), None)
    if summary is None or first != STATUS_HEADING:
        errs.append((1, "first section must be '%s'" % STATUS_HEADING))
        return
    for req in SUMMARY_REQ:
        if req not in summary.keys:
            errs.append((summary.line, "missing required key '%s'" % req))
    if "Next action" in summary.keys:
        val, n = summary.keys["Next action"]
        if val.strip() in ("", "TBD", "TODO"):
            errs.append((n, "Next action is empty or a placeholder"))


def check_vocab(summary, milestones, errs):
    if summary is not None and "Milestone state" in summary.keys:
        val, n = summary.keys["Milestone state"]
        if val != "none" and val not in MILESTONE_STATES:
            errs.append((n, "illegal milestone state '%s'" % val))
    seen_m = {}
    seen_f = {}
    for m in milestones:
        if m.id in seen_m:
            errs.append((m.line, "duplicate milestone ID %s" % m.id))
        seen_m[m.id] = m
        if "State" not in m.keys:
            errs.append((m.line, "milestone %s missing 'State'" % m.id))
        else:
            val, n = m.keys["State"]
            if val not in MILESTONE_STATES:
                errs.append((n, "illegal milestone state '%s'" % val))
        if "Goal" not in m.keys:
            errs.append((m.line, "milestone %s missing 'Goal'" % m.id))
        else:
            val, n = m.keys["Goal"]
            if not val.strip():
                errs.append((n, "Goal is empty"))
            elif val.strip().lower() in PLACEHOLDERS:
                errs.append((n, "Goal is a placeholder"))
        if "Covers" not in m.keys:
            errs.append((m.line, "milestone %s missing 'Covers'" % m.id))
        else:
            val, n = m.keys["Covers"]
            if not COVERS.match(val):
                errs.append((n, "Covers must be 'PRD-NNN REQ-NNN, ...' (three digits each)"))
            else:
                for c in CITATION.finditer(val):
                    if c.group(1) == "000" or c.group(2) == "000":
                        errs.append((n, "illegal 000 in citation '%s'" % c.group(0)))
        for f in m.features:
            if f.id in seen_f:
                errs.append((f.line, "duplicate feature ID %s" % f.id))
            seen_f[f.id] = f
            if f.id.endswith("-000"):
                errs.append((f.line, "illegal feature number 000"))
            for req in FEATURE_REQ:
                if req not in f.keys:
                    errs.append((f.line, "feature %s missing '%s'" % (f.id, req)))
            if "Status" in f.keys:
                val, n = f.keys["Status"]
                if not FEATURE_STATUS.match(val):
                    errs.append((n, "illegal feature status '%s'" % val))


def ref_id(value):
    return value.split(" — ")[0].strip() if value != "none" else "none"


def check_citations(milestones, errs):
    seen = {}
    for m in milestones:
        val, n = m.keys.get("Covers", ("", m.line))
        for c in CITATION.finditer(val):
            key = c.group(0)
            if key in seen:
                errs.append((n, "REQ cited more than once: '%s' (first at line %d)" % (key, seen[key])))
            else:
                seen[key] = n


def check_ms_numbering(summary, milestones, errs):
    def num(tok):
        return int(tok.split("-")[1])
    live = {}
    for m in milestones:
        if m.id.endswith("-000"):
            errs.append((m.line, "illegal milestone number 000"))
        live.setdefault(num(m.id), m)
    retired = []
    if summary is not None and "Retired milestones" in summary.keys:
        val, n = summary.keys["Retired milestones"]
        if not RETIRED_MS.match(val):
            errs.append((n, "malformed Retired milestones line, expected 'MS-NNN, ...'"))
        else:
            retired = [int(t.group(1)) for t in MS_TOKEN.finditer(val)]
            if 0 in retired:
                errs.append((n, "illegal milestone number 000"))
            if retired != sorted(set(retired)):
                errs.append((n, "Retired milestones must be ascending without duplicates"))
            collide = set(retired) & set(live)
            if collide:
                errs.append((n, "retired milestone IDs collide with live sections: %s" % sorted(collide)))
    union = sorted((set(live) | set(retired)) - {0})
    if union and union != list(range(1, union[-1] + 1)):
        errs.append((min(m.line for m in milestones) if milestones else 1, "live and retired milestones must cover MS-001..MS-%03d with no gaps" % union[-1]))


def check_agreement(summary, milestones, errs):
    if summary is None:
        return
    need = ("Current milestone", "Milestone state", "Active feature")
    if any(k not in summary.keys for k in need):
        return  # missing keys already reported by check_summary
    (cm_raw, cm_line) = summary.keys["Current milestone"]
    (ms, ms_line) = summary.keys["Milestone state"]
    (af_raw, af_line) = summary.keys["Active feature"]
    cm, af = ref_id(cm_raw), ref_id(af_raw)

    if cm == "none":
        if ms != "none" or af != "none":
            errs.append((cm_line, "illegal summary tuple: current milestone is none but state/feature are not"))
        for m in milestones:
            state = m.keys.get("State", ("", m.line))[0]
            if state in MIDFLIGHT:
                errs.append((m.line, "milestone %s is mid-flight but current milestone is none" % m.id))
        return

    if ms == "none":
        errs.append((ms_line, "illegal summary tuple: milestone state none with a current milestone"))
        return
    if ms in ("planning-pending", "planned", "review-ready", "accepted") and af != "none":
        errs.append((af_line, "illegal summary tuple: active feature set in state '%s'" % ms))

    target = next((m for m in milestones if m.id == cm), None)
    if target is None:
        errs.append((cm_line, "current milestone %s has no section" % cm))
        return
    state = target.keys.get("State", ("", target.line))[0]
    if state != ms:
        errs.append((target.line, "milestone %s state '%s' does not match summary '%s'" % (cm, state, ms)))

    if af != "none":
        feat = next((f for f in target.features if f.id == af), None)
        if feat is None:
            errs.append((af_line, "active feature %s not found under %s" % (af, cm)))
        elif feat.keys.get("Status", ("", 0))[0] != "WIP":
            errs.append((feat.line, "active feature %s is not WIP" % af))

    idx = milestones.index(target)
    for m in milestones[:idx]:
        if m.keys.get("State", ("", m.line))[0] != "accepted":
            errs.append((m.line, "milestone %s before the current milestone must be accepted" % m.id))
    for m in milestones[idx + 1:]:
        if m.keys.get("State", ("", m.line))[0] not in FUTURE_OK:
            errs.append((m.line, "milestone %s after the current milestone must be planning-pending or planned" % m.id))


def check_features(milestones, errs):
    wip_lines = []
    for m in milestones:
        state = m.keys.get("State", ("", m.line))[0]
        phase = 0  # 0=done prefix, 1=one mid-flight slot used, 2=todo tail
        for f in m.features:
            status = f.keys.get("Status", ("", f.line))[0]
            n = f.keys.get("Status", ("", f.line))[1]
            base = status.split("(")[0]
            if base == "WIP":
                wip_lines.append(n)
            if state in ("review-ready", "accepted") and status != "done":
                errs.append((n, "feature %s in %s milestone must be done" % (f.id, state)))
            if status == "done":
                if phase != 0:
                    errs.append((n, "feature %s done out of order" % f.id))
                for req in EVIDENCE_REQ:
                    if req not in f.evidence:
                        errs.append((f.line, "feature %s missing evidence field '%s'" % (f.id, req)))
                if "Tests" in f.evidence:
                    val, tn = f.evidence["Tests"]
                    if not val.startswith("pass"):
                        errs.append((tn, "Tests must begin 'pass', got '%s'" % val))
                if "Verdict" in f.evidence:
                    val, vn = f.evidence["Verdict"]
                    if val not in ACCEPT_VERDICTS:
                        errs.append((vn, "Verdict must be approve or approve-with-findings"))
                if "Findings" in f.evidence:
                    val, fn = f.evidence["Findings"]
                    if not FINDINGS.match(val):
                        errs.append((fn, "Findings must be 'none' or list each blocking finding as fixed/refuted(...)"))
            elif base in ("WIP", "blocked", "failed"):
                if phase >= 1:
                    if phase == 2:
                        errs.append((n, "feature %s out of order: mid-flight feature after todo" % f.id))
                    else:
                        errs.append((n, "feature %s out of order: second mid-flight feature" % f.id))
                phase = 1
                if base == "failed":
                    val = f.keys.get("Learning", ("", 0))[0]
                    if not LEARNING.match(val):
                        errs.append((f.line, "failed feature %s must carry Learning: docs/learnings/ALI-NNN.md" % f.id))
            elif status == "todo":
                phase = 2
    if len(wip_lines) > 1:
        for n in wip_lines[1:]:
            errs.append((n, "more than one WIP feature in the file"))


def validate(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    summary, milestones, errs = parse(lines)
    check_summary(lines, summary, errs)
    check_vocab(summary, milestones, errs)
    check_citations(milestones, errs)
    check_ms_numbering(summary, milestones, errs)
    check_agreement(summary, milestones, errs)
    check_features(milestones, errs)
    return ["%s:%d: %s" % (path, n, msg) for n, msg in sorted(errs)]


def main():
    if len(sys.argv) != 2:
        print("usage: validate_roadmap.py <ROADMAP.md>", file=sys.stderr)
        return 2
    errors = validate(sys.argv[1])
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
