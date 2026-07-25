#!/usr/bin/env python3
"""Session transaction for write-prd (spec 03): manifest, preflight, preview, approve, abandon."""
import json, os, subprocess, sys

def git(root, *args):
    r = subprocess.run(["git"] + list(args), cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

def repo_root():
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return os.path.realpath(r.stdout.strip())

def manifest_path(root):
    _, out, _ = git(root, "rev-parse", "--git-dir")
    gd = out.strip()
    if not os.path.isabs(gd):
        gd = os.path.join(root, gd)
    return os.path.join(gd, "session-tx.json")

def load(root):
    p = manifest_path(root)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def save(root, m):
    with open(manifest_path(root), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1)

def rel(root, path):
    return os.path.relpath(os.path.realpath(os.path.abspath(path)), root)

def is_tracked(root, r):
    _, out, _ = git(root, "ls-files", "--", r)
    return out.strip() != ""

def cmd_begin(root):
    if load(root) is not None:
        sys.stderr.write("session already active; approve or abandon it first (session_tx.py status)\n")
        return 1
    save(root, {"entries": []})
    print("session begun")
    return 0

def cmd_track(root, paths):
    m = load(root)
    if m is None:
        sys.stderr.write("no active session; run begin first\n")
        return 1
    known = {e["path"] for e in m["entries"]}
    for p in paths:
        r = rel(root, p)
        if r in known:
            continue
        if is_tracked(root, r):
            _, out, _ = git(root, "status", "--porcelain", "--", r)
            if out.strip():
                sys.stderr.write("%s: has pre-existing changes; refusing to track\n" % r)
                return 1
            m["entries"].append({"path": r, "mode": "tracked"})
        else:
            if os.path.lexists(os.path.join(root, r)):
                sys.stderr.write("%s: exists but is untracked; refusing to track\n" % r)
                return 1
            m["entries"].append({"path": r, "mode": "created"})
        known.add(r)
    save(root, m)
    return 0

def cmd_preview(root):
    m = load(root)
    if m is None:
        sys.stderr.write("no active session\n")
        return 1
    for e in m["entries"]:
        p = os.path.join(root, e["path"])
        if e["mode"] == "created":
            print("=== new file: %s ===" % e["path"])
            if os.path.exists(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    sys.stdout.write(f.read())
            else:
                print("(not yet written)")
        else:
            print("=== %s ===" % e["path"])
            _, out, _ = git(root, "diff", "--", e["path"])
            sys.stdout.write(out if out else "(unchanged)\n")
    return 0

def cmd_approve(root, msg):
    m = load(root)
    if m is None:
        sys.stderr.write("no active session\n")
        return 1
    _, staged, _ = git(root, "diff", "--cached", "--name-only")
    manifest_paths = {e["path"] for e in m["entries"]}
    outside = [s for s in staged.strip().splitlines() if s and s not in manifest_paths]
    if outside:
        sys.stderr.write("staged changes outside the session manifest: %s; resolve before approving\n" % ", ".join(outside))
        return 1
    if manifest_paths:
        code, _, err = git(root, "add", "-A", "--", *sorted(manifest_paths))
        if code != 0:
            sys.stderr.write(err)
            return 1
    code, _, err = git(root, "commit", "-m", msg)
    if code != 0:
        sys.stderr.write(err)
        return 1
    os.remove(manifest_path(root))
    print("committed %d path(s)" % len(manifest_paths))
    return 0

def cmd_abandon(root):
    m = load(root)
    if m is None:
        sys.stderr.write("no active session\n")
        return 1
    for e in m["entries"]:
        p = os.path.join(root, e["path"])
        if e["mode"] == "created":
            if os.path.lexists(p):
                os.remove(p)
        else:
            git(root, "checkout", "--", e["path"])
    os.remove(manifest_path(root))
    print("abandoned; %d path(s) rolled back" % len(m["entries"]))
    return 0

def cmd_status(root):
    m = load(root)
    if m is None:
        print("no active session")
        return 0
    for e in m["entries"]:
        print("%s %s" % (e["mode"], e["path"]))
    return 0

def main(argv):
    root = repo_root()
    if root is None:
        sys.stderr.write("not inside a git repository\n")
        return 2
    if len(argv) < 2:
        sys.stderr.write("usage: session_tx.py {begin|track <path>...|preview|approve -m <msg>|abandon|status}\n")
        return 2
    cmd = argv[1]
    if cmd == "begin":
        return cmd_begin(root)
    if cmd == "track":
        if len(argv) < 3:
            sys.stderr.write("track requires at least one path\n")
            return 2
        return cmd_track(root, argv[2:])
    if cmd == "preview":
        return cmd_preview(root)
    if cmd == "approve":
        if len(argv) != 4 or argv[2] != "-m":
            sys.stderr.write("usage: session_tx.py approve -m <msg>\n")
            return 2
        return cmd_approve(root, argv[3])
    if cmd == "abandon":
        return cmd_abandon(root)
    if cmd == "status":
        return cmd_status(root)
    sys.stderr.write("unknown subcommand: %s\n" % cmd)
    return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv))
