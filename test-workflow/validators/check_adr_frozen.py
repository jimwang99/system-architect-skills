#!/usr/bin/env python3
"""Git-aware immutability check for frozen ADRs.

Spec: docs/specs/workflow/02-write-adr.md. Fail-closed: a worktree file
with frozen status must have a provable proposed->frozen lineage in a
non-shallow clone; otherwise exit 1.
"""
import os
import re
import subprocess
import sys

FROZEN = {"accepted", "rejected", "superseded"}
_HASH = re.compile(r"^[0-9a-f]{40}$")


def git(cwd, *args):
    return subprocess.run(("git",) + args, cwd=cwd, capture_output=True, text=True)


def split_frontmatter(text):
    """Return (status, body) — body is everything below the closing '---'."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    status = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return status, "\n".join(lines[i + 1:])
        if line.startswith("status: "):
            status = line[len("status: "):].strip()
    return status, ""


def fail(msg):
    print(msg, file=sys.stderr)
    return 1


def main():
    if len(sys.argv) != 2:
        print("usage: check_adr_frozen.py <adr-file>", file=sys.stderr)
        return 2
    # realpath so path and --show-toplevel live in the same namespace: git resolves
    # symlinks in --show-toplevel (e.g. macOS /var -> /private/var), and a raw abspath
    # would produce a garbage relative path that git can't match, failing closed wrongly.
    path = os.path.realpath(sys.argv[1])
    directory = os.path.dirname(path)
    top = git(directory, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        print("%s: not inside a git repository" % path, file=sys.stderr)
        return 2
    root = os.path.realpath(top.stdout.strip())
    rel = os.path.relpath(path, root)
    with open(path, encoding="utf-8") as fh:
        wt_status, wt_body = split_frontmatter(fh.read())
    # Shallowness fails closed for EVERY status: the worktree frontmatter is
    # untrusted input (a defrosted file self-reports proposed), and truncated
    # history can neither prove nor rule out a freeze point.
    shallow = git(root, "rev-parse", "--is-shallow-repository")
    if shallow.stdout.strip() == "true":
        return fail("%s: shallow clone — freeze lineage unprovable, failing closed" % path)
    log = git(root, "log", "--follow", "-M40", "--format=%H", "--name-only", "--", rel)
    if log.returncode != 0 or not log.stdout.strip():
        if wt_status in FROZEN:
            return fail("%s: no history for file — failing closed" % path)
        return 0  # brand-new or uncommitted draft; nothing frozen yet
    entries = []  # (commit, historical_name), newest first — parsing unchanged
    commit = None
    for line in log.stdout.splitlines():
        s = line.strip()
        if not s:
            continue
        if _HASH.match(s):
            commit = s
        elif commit is not None:
            entries.append((commit, s))
            commit = None
    freeze = None
    saw_proposed = False
    for commit, name in reversed(entries):  # oldest -> newest
        show = git(root, "show", "%s:%s" % (commit, name))
        if show.returncode != 0:
            continue
        status, body = split_frontmatter(show.stdout)
        if freeze is None and status == "proposed":
            saw_proposed = True  # only ancestors strictly before the freeze point count
        if status in FROZEN and freeze is None:
            freeze = (commit, name, body)
    if freeze is None:
        if wt_status in FROZEN:
            return fail("%s: status is frozen but no freeze point found in history — failing closed" % path)
        return 0
    if not saw_proposed:
        return fail("%s: no proposed ancestor before the freeze point — failing closed (imported or rewritten history)" % path)
    if wt_status not in FROZEN:
        return fail("%s: worktree status is %r but a freeze point exists at %s — frozen records never return to proposed, failing closed"
                    % (path, wt_status, freeze[0][:7]))
    _, _, frozen_body = freeze
    if frozen_body.rstrip("\n") != wt_body.rstrip("\n"):
        f_lines = frozen_body.rstrip("\n").splitlines()
        w_lines = wt_body.rstrip("\n").splitlines()
        for i in range(max(len(f_lines), len(w_lines))):
            a = f_lines[i] if i < len(f_lines) else "<absent>"
            b = w_lines[i] if i < len(w_lines) else "<absent>"
            if a != b:
                return fail("%s: frozen body modified at body line %d: %r -> %r" % (path, i + 1, a, b))
        return fail("%s: frozen body modified" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
