---
name: long-running-jobs
description: Launch, watch, resume, stop, and finish shell jobs that outlive one tool call, through a persisted run record (run ID, lock, readiness, heartbeat, exit result). Use when a shell command is expected to run longer than about two minutes or must run in the background, when checking on or stopping such a job, and at session start when `.runs/` holds unfinished runs.
---

# Long-running jobs

Every job runs under `scripts/job.py`, a stdlib-only supervisor that owns the run record. The record is the only source of truth about a run: identity, readiness, progress freshness, and exit result live in `.runs/<name>/<run-id>/state.json`, and the log in `log.txt` beside it. Process listings, `pgrep`, and memory of "what I started earlier" carry no authority.

All commands below are `python3 <skill-directory>/scripts/job.py <command>`; `--help` lists every flag. Run them from the project root so `.runs/` lands in one place, or pass `--root DIR` consistently.

## Steps

1. **Reconcile first.** When `.runs/` exists, run `reconcile`. It validates each unfinished run by recorded pid plus process start time, marks dead ones `lost`, and frees their locks. Add `--kill-stale` only to stop runs that are both validated as ours and past their stall threshold. Done: every unfinished run has a live, validated process.
2. **Start.** `start --name NAME [--ready-regex RE] [--phase-regex RE] [--stall-after SEC] [--output PATH]... -- CMD ARGS...`. It takes the per-name lock, writes the record, detaches a supervisor, and prints the run ID, state path, and log path. Declare every artifact the job must produce with `--output`; `finish` checks them. Tell the human user the run ID and log path. Done: `start` printed a run ID.
3. **Verify readiness before reporting "on track".** `wait RUN-ID --until ready --timeout SEC`. Ready means a log line matched `--ready-regex`, or, without one, the first log output appeared. Until then the report is "started, not yet ready". Done: `ready_at` is set.
4. **Watch.** `wait RUN-ID --timeout SEC` blocks until the run ends; exit code 124 means "still running", so poll again. Keep each wait under the shell tool's timeout; longer waits go through the harness's background or monitor facility. Every check prints `phase`, `since_progress_s`, and `stalled`; relay phase and freshness to the human user. A stalled run means: read the log tail, then either `kill RUN-ID` and restart with a larger `--stall-after` (jobs with sparse output need one), or let it continue if the log explains the silence. Done: status is terminal (`succeeded`, `failed`, `killed`, `lost`).
5. **Finish.** `finish RUN-ID` requires status `succeeded`, checks every declared output exists and is non-empty, confirms the lock is released, and stamps `verified_at`. Report exit code, output paths, and log path. Done: `finish` exited 0. Any other exit means the job is not done: report the problems it printed together with the log tail.

## Rules

- Identity is pid plus recorded process start time; a pid alone, a process name, or a `pgrep` hit never identifies a run.
- One live run per name. A second `start` with the same name fails while the lock's owner is alive; `reconcile` clears locks whose owner is gone.
- Stop a run only through `kill RUN-ID` or `reconcile --kill-stale`, which validate identity before signalling the process group.
- Keep `.runs/` out of version control: add it to `.gitignore` when the entry is missing.

## Record fields

| field | meaning |
|---|---|
| `status` | `starting` → `running` → one of `succeeded`, `failed`, `killed`, `lost` |
| `pid`, `pgid`, `pid_start` | the job's identity; `supervisor_pid` is the detached watcher |
| `ready_at` | first `--ready-regex` match, or first output without one |
| `phase` | last `--phase-regex` match (group 1 when the pattern has one) |
| `progress_at` | last time the log grew; drives `since_progress_s` and `stalled` |
| `alive_at` | supervisor heartbeat, refreshed every 2 s |
| `exit_code`, `ended_at` | recorded by the supervisor when the job exits |
| `outputs`, `verified_at`, `problems` | declared artifacts and the result of `finish` |
