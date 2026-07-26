#!/usr/bin/env python3
"""Reviewer gate for execute-milestone (spec 07, Decision 2).

Invokes `workflow-review <base> <head>` from PATH, applies the transport
policy (one retry; second failure pauses), and maps verdicts to exits:
0 approve / approve-with-findings with no blocking finding
1 reject or any blocking finding (JSON echoed either way)
3 transport failure after retry (pause the milestone)
2 usage error
"""
import json
import os
import subprocess
import sys

VERDICTS = {"approve", "approve-with-findings", "reject"}


def attempt(base, head, timeout):
    try:
        r = subprocess.run(["workflow-review", base, head],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout after %ss" % timeout
    except OSError as e:
        return None, "cannot invoke workflow-review: %s" % e
    if r.returncode != 0:
        return None, "exit %d: %s" % (r.returncode, r.stderr.strip()[:200])
    try:
        data = json.loads(r.stdout)
    except ValueError:
        return None, "malformed JSON on stdout"
    if not isinstance(data, dict) or data.get("verdict") not in VERDICTS:
        return None, "missing or illegal verdict"
    if not isinstance(data.get("findings", []), list):
        return None, "findings is not a list"
    return data, None


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: review_gate.py <base> <head>\n")
        return 2
    timeout = float(os.environ.get("WORKFLOW_REVIEW_TIMEOUT", "300"))
    data, reason = attempt(argv[1], argv[2], timeout)
    if data is None:
        sys.stderr.write("review_gate: transport failure (%s); retrying once\n" % reason)
        data, reason = attempt(argv[1], argv[2], timeout)
    if data is None:
        sys.stderr.write("review_gate: transport failure after retry (%s); pause the milestone, feature stays WIP\n" % reason)
        return 3
    sys.stdout.write(json.dumps(data) + "\n")
    blocking = [f for f in data.get("findings", []) if isinstance(f, dict) and f.get("severity") == "blocking"]
    if data["verdict"] == "reject" or blocking:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
