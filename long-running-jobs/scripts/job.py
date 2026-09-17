#!/usr/bin/env python3
"""Supervise a long-running shell job through a persisted run record.

Layout: <root>/<name>/<run-id>/{state.json,log.txt}; per-name lock at <root>/<name>/lock/.
stdlib only, Python 3.9+: it must work before any project venv exists.
"""
import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_ROOT = ".runs"
TICK_S = 2
STARTING_GRACE_S = 10
TERMINAL = {"succeeded", "failed", "killed", "lost"}
EXIT_TIMEOUT = 124  # same code as coreutils `timeout`, so a caller can tell "still running" from "failed"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def seconds_since(stamp: Optional[str]) -> Optional[int]:
    if not stamp:
        return None
    then = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return int((datetime.now(timezone.utc) - then).total_seconds())


def die(msg: str, code: int = 2) -> None:
    print(json.dumps({"error": msg}), file=sys.stderr)
    sys.exit(code)


# ---------- record ----------

def load(run_dir: Path) -> dict:
    return json.loads((run_dir / "state.json").read_text())


def save(run_dir: Path, state: dict) -> None:
    # Write-then-rename so a reader never sees a half-written record.
    tmp = run_dir / "state.json.tmp"
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, run_dir / "state.json")


def find_run(root: Path, run_id: str) -> Path:
    matches = [p for p in root.glob(f"*/{run_id}") if (p / "state.json").exists()]
    if not matches:
        die(f"no run {run_id} under {root}")
    return matches[0]


def all_runs(root: Path):
    for name_dir in sorted(root.iterdir()) if root.exists() else []:
        if not name_dir.is_dir():
            continue
        for run_dir in sorted(name_dir.iterdir()):
            if run_dir.name != "lock" and (run_dir / "state.json").exists():
                yield run_dir


# ---------- process identity ----------

def proc_start(pid: int) -> Optional[str]:
    """Kernel-reported start time. pid + start time is the run's identity, so a reused pid never matches."""
    try:
        out = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True)
    except OSError:
        return None
    return out.stdout.strip() or None


def validated_alive(state: dict) -> bool:
    pid = state.get("pid")
    return pid is not None and proc_start(pid) == state.get("pid_start")


# ---------- lock ----------

def lock_dir(root: Path, name: str) -> Path:
    return root / name / "lock"


def acquire_lock(root: Path, name: str, run_id: str) -> Optional[str]:
    """Return None on success, else the run id that holds the lock ("?" if unreadable)."""
    ld = lock_dir(root, name)
    try:
        ld.mkdir(parents=True)  # mkdir is atomic on POSIX, which makes it the lock primitive
    except FileExistsError:
        owner = ld / "owner"
        return owner.read_text().strip() if owner.exists() else "?"
    (ld / "owner").write_text(run_id)
    return None


def release_lock(root: Path, name: str, run_id: str) -> None:
    ld = lock_dir(root, name)
    owner = ld / "owner"
    if owner.exists() and owner.read_text().strip() == run_id:
        owner.unlink()
        ld.rmdir()


def lock_held_by(root: Path, name: str, run_id: str) -> bool:
    owner = lock_dir(root, name) / "owner"
    return owner.exists() and owner.read_text().strip() == run_id


# ---------- derived view ----------

def derive(state: dict) -> dict:
    d = dict(state)
    live = state["status"] in ("starting", "running")
    d["since_progress_s"] = seconds_since(state.get("progress_at") or state.get("started_at"))
    d["alive_validated"] = validated_alive(state) if live else False
    d["stalled"] = bool(
        state["status"] == "running" and d["since_progress_s"] is not None
        and d["since_progress_s"] > state["stall_after_s"]
    )
    return d


def finish_record(run_dir: Path, state: dict, root: Path) -> dict:
    save(run_dir, state)
    release_lock(root, state["name"], state["run_id"])
    return state


def reconcile_run(run_dir: Path, root: Path, kill_stale: bool = False) -> dict:
    """Bring one record in line with reality: dead process -> lost; optionally kill a validated stalled run."""
    state = load(run_dir)
    if state["status"] in TERMINAL:
        release_lock(root, state["name"], state["run_id"])  # supervisor may have died between save and release
        return state
    if state["status"] == "starting" and (seconds_since(state["started_at"]) or 0) < STARTING_GRACE_S:
        return state
    if not validated_alive(state):
        time.sleep(0.5)  # the supervisor may be mid-way through recording the exit
        state = load(run_dir)
        if state["status"] not in TERMINAL:
            state.update(status="lost", ended_at=now_iso(), note="process gone without a recorded exit")
        return finish_record(run_dir, state, root)
    if kill_stale and derive(state)["stalled"]:
        return kill_run(run_dir, root, reason="stalled")
    return state


def kill_run(run_dir: Path, root: Path, reason: str) -> dict:
    state = load(run_dir)
    if state["status"] in TERMINAL:
        return state
    if not validated_alive(state):
        return reconcile_run(run_dir, root)
    pgid = state["pgid"]
    for sig, grace in ((signal.SIGTERM, 10), (signal.SIGKILL, 3)):
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            break
        deadline = time.time() + grace
        while time.time() < deadline and validated_alive(state):
            time.sleep(0.2)
        if not validated_alive(state):
            break
    # Let the supervisor record the exit first, then stamp the reason on top.
    for _ in range(10):
        state = load(run_dir)
        if state["status"] in TERMINAL:
            break
        time.sleep(0.5)
    state.update(status="killed", kill_reason=reason, ended_at=state.get("ended_at") or now_iso())
    return finish_record(run_dir, state, root)


# ---------- commands ----------

def cmd_start(a) -> None:
    if not a.cmd:
        die("no command given after --")
    root = Path(a.root).resolve()
    run_id = f"{a.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
    owner = acquire_lock(root, a.name, run_id)
    if owner:
        owner_dir = next(iter(root.glob(f"{a.name}/{owner}")), None)
        if owner_dir and (owner_dir / "state.json").exists():
            owner_state = reconcile_run(owner_dir, root)
            if owner_state["status"] not in TERMINAL:
                die(f"'{a.name}' is already running as {owner}; wait, kill, or reconcile first")
        else:
            # Lock with no readable owner: nothing can validate it, so it is dead weight.
            ld = lock_dir(root, a.name)
            if (ld / "owner").exists():
                (ld / "owner").unlink()
            ld.rmdir()
        if acquire_lock(root, a.name, run_id):
            die(f"could not take the lock for '{a.name}'")
    run_dir = root / a.name / run_id
    run_dir.mkdir(parents=True)
    cwd = os.getcwd()
    state = {
        "run_id": run_id,
        "name": a.name,
        "cmd": a.cmd,
        "cwd": cwd,
        "log": str(run_dir / "log.txt"),
        "outputs": [str(Path(p).resolve()) for p in a.output],
        "ready_regex": a.ready_regex,
        "phase_regex": a.phase_regex,
        "stall_after_s": a.stall_after,
        "status": "starting",
        "started_at": now_iso(),
        "pid": None, "pgid": None, "pid_start": None, "supervisor_pid": None,
        "ready_at": None, "phase": None, "progress_at": None, "alive_at": None,
        "exit_code": None, "ended_at": None, "verified_at": None,
    }
    save(run_dir, state)
    (run_dir / "log.txt").touch()
    # Detached supervisor: it must outlive the shell call and the agent session that started it.
    subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "_supervise", str(run_dir), "--root", str(root)],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True, cwd=cwd,
    )
    print(json.dumps({"run_id": run_id, "state": str(run_dir / "state.json"), "log": state["log"]}))


def cmd_supervise(a) -> None:
    run_dir = Path(a.run_dir)
    root = Path(a.root)
    state = load(run_dir)
    log_path = run_dir / "log.txt"
    try:
        with open(log_path, "ab") as log:
            child = subprocess.Popen(
                state["cmd"], cwd=state["cwd"], stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
            )
    except OSError as e:
        state.update(status="failed", exit_code=127, ended_at=now_iso(), note=f"launch failed: {e}")
        finish_record(run_dir, state, root)
        return
    state.update(pid=child.pid, pgid=child.pid, pid_start=proc_start(child.pid),
                 supervisor_pid=os.getpid(), status="running", alive_at=now_iso())
    save(run_dir, state)
    ready_re = re.compile(state["ready_regex"]) if state["ready_regex"] else None
    phase_re = re.compile(state["phase_regex"]) if state["phase_regex"] else None
    offset = 0
    pending = ""  # partial last line, so a match never straddles two reads
    while True:
        rc = child.poll()
        size = log_path.stat().st_size
        if size > offset:
            with open(log_path, "rb") as f:
                f.seek(offset)
                pending += f.read(size - offset).decode("utf-8", "replace")
            offset = size
            state["progress_at"] = now_iso()
            lines = pending.split("\n")
            pending = lines.pop()
            if rc is not None and pending:
                lines.append(pending)
                pending = ""
            for line in lines:
                if phase_re:
                    m = phase_re.search(line)
                    if m:
                        state["phase"] = (m.group(1) if m.groups() else m.group(0)).strip()
                if not state["ready_at"] and (ready_re is None or ready_re.search(line)):
                    state["ready_at"] = now_iso()
        state["alive_at"] = now_iso()
        if rc is not None:
            state.update(exit_code=rc, status="succeeded" if rc == 0 else "failed", ended_at=now_iso())
            finish_record(run_dir, state, root)
            return
        save(run_dir, state)
        time.sleep(TICK_S)


def cmd_status(a) -> None:
    root = Path(a.root).resolve()
    if a.run_id:
        runs = [find_run(root, a.run_id)]
    else:
        runs = [r for r in all_runs(root) if a.all or load(r)["status"] not in TERMINAL]
    for run_dir in runs:
        print(json.dumps(derive(reconcile_run(run_dir, root))))


def cmd_wait(a) -> None:
    root = Path(a.root).resolve()
    run_dir = find_run(root, a.run_id)
    deadline = time.time() + a.timeout if a.timeout else None
    while True:
        state = reconcile_run(run_dir, root)
        done = state["status"] in TERMINAL
        if done or (a.until == "ready" and state.get("ready_at")):
            break
        if deadline and time.time() >= deadline:
            print(json.dumps(derive(state)))
            sys.exit(EXIT_TIMEOUT)
        time.sleep(TICK_S)
    print(json.dumps(derive(state)))
    ok = state["status"] == "succeeded" or (a.until == "ready" and bool(state.get("ready_at")))
    sys.exit(0 if ok else 1)


def cmd_reconcile(a) -> None:
    root = Path(a.root).resolve()
    for run_dir in all_runs(root):
        before = load(run_dir)["status"]
        state = reconcile_run(run_dir, root, kill_stale=a.kill_stale)
        if before not in TERMINAL or a.all:
            print(json.dumps({"run_id": state["run_id"], "was": before, "now": state["status"],
                              "stalled": derive(state)["stalled"]}))


def cmd_kill(a) -> None:
    root = Path(a.root).resolve()
    state = kill_run(find_run(root, a.run_id), root, reason=a.reason)
    print(json.dumps(derive(state)))


def cmd_finish(a) -> None:
    root = Path(a.root).resolve()
    run_dir = find_run(root, a.run_id)
    state = reconcile_run(run_dir, root)
    problems = []
    if state["status"] != "succeeded":
        problems.append(f"status is {state['status']} (exit_code={state.get('exit_code')})")
    for p in state["outputs"]:
        path = Path(p)
        if not path.exists():
            problems.append(f"missing output: {p}")
        elif path.is_file() and path.stat().st_size == 0:
            problems.append(f"empty output: {p}")
    if lock_held_by(root, state["name"], state["run_id"]):
        problems.append("lock still held")
    state["verified_at"] = now_iso() if not problems else None
    state["problems"] = problems
    save(run_dir, state)
    print(json.dumps({"run_id": state["run_id"], "status": state["status"], "exit_code": state.get("exit_code"),
                      "outputs": state["outputs"], "log": state["log"], "verified": not problems,
                      "problems": problems}))
    sys.exit(0 if not problems else 1)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    def add_root(sp):
        sp.add_argument("--root", default=DEFAULT_ROOT, help=f"run records directory (default {DEFAULT_ROOT})")

    s = sub.add_parser("start", help="launch CMD under a detached supervisor; prints the run id")
    add_root(s)
    s.add_argument("--name", required=True, help="job name; one live run per name")
    s.add_argument("--ready-regex", help="log line pattern that marks readiness (default: first output)")
    s.add_argument("--phase-regex", help="log line pattern whose match (group 1 if any) becomes the phase")
    s.add_argument("--stall-after", type=int, default=600, help="seconds without log growth before 'stalled'")
    s.add_argument("--output", action="append", default=[], help="expected output path; repeatable")
    s.add_argument("cmd", nargs=argparse.REMAINDER, help="-- CMD ARGS...")
    s.set_defaults(fn=cmd_start)

    s = sub.add_parser("_supervise")
    add_root(s)
    s.add_argument("run_dir")
    s.set_defaults(fn=cmd_supervise)

    s = sub.add_parser("status", help="one JSON line per run (unfinished runs by default)")
    add_root(s)
    s.add_argument("run_id", nargs="?")
    s.add_argument("--all", action="store_true", help="include finished runs")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("wait", help="block until ready or done; exit 0 ok, 1 failed, 124 timeout")
    add_root(s)
    s.add_argument("run_id")
    s.add_argument("--until", choices=("ready", "done"), default="done")
    s.add_argument("--timeout", type=int, help="seconds; keep it under the shell tool's own timeout")
    s.set_defaults(fn=cmd_wait)

    s = sub.add_parser("reconcile", help="mark dead runs lost, free their locks; --kill-stale stops validated stalled runs")
    add_root(s)
    s.add_argument("--kill-stale", action="store_true")
    s.add_argument("--all", action="store_true", help="also list runs that were already finished")
    s.set_defaults(fn=cmd_reconcile)

    s = sub.add_parser("kill", help="stop a run after validating its identity")
    add_root(s)
    s.add_argument("run_id")
    s.add_argument("--reason", default="requested")
    s.set_defaults(fn=cmd_kill)

    s = sub.add_parser("finish", help="verify exit status and declared outputs; exit 0 only when all pass")
    add_root(s)
    s.add_argument("run_id")
    s.set_defaults(fn=cmd_finish)

    a = p.parse_args()
    if a.command == "start" and a.cmd and a.cmd[0] == "--":
        a.cmd = a.cmd[1:]
    a.fn(a)


if __name__ == "__main__":
    main()
