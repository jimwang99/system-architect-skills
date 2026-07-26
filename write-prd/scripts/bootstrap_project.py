#!/usr/bin/env python3
"""Bootstrap classifier/applier for write-prd (spec 03): state table over AGENTS.md and CLAUDE.md."""
import os, subprocess, sys

CANONICAL_SECTION = (
    "## Doc-driven workflow\n"
    "\n"
    "Before any workflow task, read and follow\n"
    "@~/.agents/skills/system-architect-skills/WORKFLOW.md.\n"
)
SECTION_HEADING = "## Doc-driven workflow"
REF_SUBSTR = "@~/.agents/skills/system-architect-skills/WORKFLOW.md"
CLAUDE_LINE = "@AGENTS.md"
DEFAULT_WORKFLOW = os.path.expanduser("~/.agents/skills/system-architect-skills/WORKFLOW.md")

def repo_root():
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return os.path.realpath(r.stdout.strip()) if r.returncode == 0 else None

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def classify_agents(root):
    p = os.path.join(root, "AGENTS.md")
    if os.path.islink(p):
        return "symlink", "stop", None
    if os.path.lexists(p) and not os.path.isfile(p):
        return "non-regular", "stop", None
    if not os.path.exists(p):
        return "absent", "create", CANONICAL_SECTION
    text = read(p)
    if SECTION_HEADING in text:
        if REF_SUBSTR in text:
            return "section intact", "no-op", None
        return "section malformed (reference line missing or altered)", "stop", None
    sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    return "section absent", "append", text + sep + CANONICAL_SECTION

def classify_claude(root):
    p = os.path.join(root, "CLAUDE.md")
    a = os.path.join(root, "AGENTS.md")
    if os.path.islink(p):
        if os.path.realpath(p) == os.path.realpath(a):
            return "symlink to AGENTS.md", "no-op", None
        return "symlink elsewhere", "stop", None
    if os.path.lexists(p) and not os.path.isfile(p):
        return "non-regular", "stop", None
    if not os.path.exists(p):
        return "absent", "create", CLAUDE_LINE + "\n"
    text = read(p)
    if any(line.strip() == CLAUDE_LINE for line in text.splitlines()):
        return "reference present", "no-op", None
    sep = "" if text.endswith("\n") else "\n"
    return "reference absent", "append", text + sep + CLAUDE_LINE + "\n"

def main(argv):
    args = list(argv[1:])
    workflow = DEFAULT_WORKFLOW
    if "--workflow-path" in args:
        i = args.index("--workflow-path")
        try:
            workflow = args[i + 1]
        except IndexError:
            sys.stderr.write("--workflow-path requires a value\n")
            return 2
        del args[i:i + 2]
    if args not in (["plan"], ["apply"]):
        sys.stderr.write("usage: bootstrap_project.py {plan|apply} [--workflow-path <p>]\n")
        return 2
    root = repo_root()
    if root is None:
        sys.stderr.write("not a git repository; run git init yourself, then re-run\n")
        return 1
    if not os.path.isfile(workflow):
        sys.stderr.write("%s: missing; the skill installation is broken, refusing to install a dangling reference\n" % workflow)
        return 1
    print("target root: %s" % root)
    plans = [("AGENTS.md",) + classify_agents(root), ("CLAUDE.md",) + classify_claude(root)]
    stops = [p for p in plans if p[2] == "stop"]
    writes = [p for p in plans if p[2] in ("create", "append")]
    for name, state, action, _ in plans:
        print("%s: %s -> %s" % (name, state, action))
    if stops:
        for name, state, _, _ in stops:
            sys.stderr.write("%s: %s; resolve by hand, nothing written\n" % (name, state))
        return 1
    if not writes:
        return 0
    if args == ["plan"]:
        return 3
    originals = {}
    try:
        for name, _, action, content in writes:
            p = os.path.join(root, name)
            originals[p] = read(p) if os.path.exists(p) else None
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
    except OSError as e:
        for p, orig in originals.items():
            try:
                if orig is None:
                    if os.path.exists(p):
                        os.remove(p)
                else:
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(orig)
            except OSError:
                pass
        sys.stderr.write("write failed (%s); rolled back\n" % e)
        return 1
    return 3

if __name__ == "__main__":
    sys.exit(main(sys.argv))
