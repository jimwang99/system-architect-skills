# Workflow Testing Status

## Verified versions

| Date | Claude Code | Codex CLI | Superpowers | Scenario sets passed |
|---|---|---|---|---|
| 2026-07-25 | 2.1.193 | 0.145.0 | 6.2.0 | act-learn-improve/01 (toy, tier 2, Claude Code only; RED + 2×GREEN at b5479c7); write-adr/01-06 (tier 2, Claude Code only; fresh RED + tier-1 gates + 2×GREEN sweep at d3215f9; scenario dispatches use a fixed neutral description — see the sweeps 1–3 CORRECTION in results/write-adr.md); write-prd/01-08 (tier 2, Claude Code only) |

## Rerun triggers

Dependency upgrades (Claude Code, Codex CLI, or Superpowers) rerun adapter conformance, recovery, explicit-ignition, and empty-human-session scenarios before support is claimed (umbrella spec, Verification Contract).
