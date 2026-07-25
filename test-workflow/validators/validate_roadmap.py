#!/usr/bin/env python3
"""Validate a ROADMAP.md against the doc-driven workflow grammar.

Spec: docs/specs/workflow/01-testing-and-conformance.md.
Stdlib only, Python 3.9+. Exit 0 on pass; exit 1 with one
"path:line: message" per violation on stderr.
"""
import sys
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

MILESTONE_STATES = {
    "planning-pending", "planned", "in-progress", "paused",
    "review-ready", "remediating", "accepted",
}
MIDFLIGHT = {"in-progress", "paused", "review-ready", "remediating"}
FUTURE_OK = {"planning-pending", "planned"}
FEATURE_STATUS = re.compile(
    r"^(todo|WIP|done|blocked\([a-z0-9][a-z0-9-]*\)|failed\(.+\))$")
M_HEAD = re.compile(r"^## (M\d{2}) — (.+)$")
F_HEAD = re.compile(r"^### (F\d{2}) — (.+)$")
KEY = re.compile(r"^- ([A-Z][A-Za-z ]*): (.*?)\s*$")
EV_KEY = re.compile(r"^  - ([A-Z][A-Za-z ]*): (.*?)\s*$")

SUMMARY_REQ = ("Current milestone", "Milestone state", "Active feature", "Next action")
FEATURE_REQ = ("Status", "Description", "Acceptance", "Test intent")
EVIDENCE_REQ = ("Base", "Commits", "Tests", "Reviewer", "Verdict", "Findings")
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
        for f in m.features:
            if f.id in seen_f:
                errs.append((f.line, "duplicate feature ID %s" % f.id))
            seen_f[f.id] = f
            for req in FEATURE_REQ:
                if req not in f.keys:
                    errs.append((f.line, "feature %s missing '%s'" % (f.id, req)))
            if "Status" in f.keys:
                val, n = f.keys["Status"]
                if not FEATURE_STATUS.match(val):
                    errs.append((n, "illegal feature status '%s'" % val))


def validate(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    summary, milestones, errs = parse(lines)
    check_summary(lines, summary, errs)
    check_vocab(summary, milestones, errs)
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
