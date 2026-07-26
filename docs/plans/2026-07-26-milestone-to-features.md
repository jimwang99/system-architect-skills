# milestone-to-features (Spec 05) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement spec 05 (`docs/specs/workflow/05-milestone-to-features.md`): the milestone-to-features skill with RED-first scenarios, plus the spec-04 rider scenario.

**Architecture:** Pure skill-and-scenario work — no validators change. Scenarios and RED baselines first (iron law), then SKILL.md + GREEN certification, then the GREEN-only rider closing spec 04's follow-up.

**Tech Stack:** markdown skills/scenarios, existing spec-04 tools (`validate_roadmap.py`, `check_coverage.py`, `session_tx.py`), git, subagent scenario runs.

## Global Constraints

- ID scheme: `PREFIX-NNN` three digits, `000` illegal; citations `PRD-NNN REQ-NNN`.
- The skill writes exactly one transition: `planning-pending → planned`; summary and milestone section change in the same commit; `Next action: execute-milestone MS-NNN`.
- Eligible states: current milestone `planning-pending`, or `planned` never-started (re-decompose); refuse from `in-progress` onward; `none` → point to prd-to-milestones.
- Feature allocation: max(live)+1 across the file; reuse after never-started deletion legal; no tombstones.
- Feature-count rule: 1–2 legal; >10 → refuse to finalize, report count + split seam, ROADMAP untouched.
- Sizing proxies (taught): one demonstrable behavior change; 1–5 testable acceptance criteria; single subsystem; no open-backlog dependency; test plan statable upfront.
- Tool paths from this skill: `<this-skill-dir>/../prd-to-milestones/scripts/validate_roadmap.py` and `check_coverage.py`; `<this-skill-dir>/scripts/session_tx.py` (relative symlink `../../scripts/session_tx.py`); artifact validators `<this-skill-dir>/../write-prd/scripts/validate_backlog.py`, `<this-skill-dir>/../write-adr/scripts/validate_adr.py`.
- Scenario conventions (spec 01): frontmatter `skill/type/tier`; five sections; observables only; scratch-repo hygiene (`git -C`, user.email/user.name/commit.gpgsign configs); scenario commit before runs; log entries pin the commit containing the scenario they name.
- No SKILL.md before RED. Historical files never rewritten. Markdown prose one paragraph = one line. Commits end with trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Suites run as `python3 test-workflow/tests/test_*.py`; they are a regression gate only (must stay green; nothing in them changes).

## File Structure

- `test-workflow/scenarios/milestone-to-features/{01-decompose-next,02-no-preplanning,03-oversized-split,04-started-refusal}.md` — Task 1.
- `test-workflow/results/milestone-to-features.md` — Tasks 1 (RED) and 2 (GREEN).
- `milestone-to-features/SKILL.md`, `milestone-to-features/scripts/session_tx.py` (symlink) — Task 2.
- `test-workflow/scenarios/prd-to-milestones/06-retired-not-started.md`, `test-workflow/results/prd-to-milestones.md` (append), `test-workflow/TESTING.md` — Task 3.

---

### Task 1: Scenarios 01–04 and RED baselines

**Files:**
- Create: the four scenario files above
- Create: `test-workflow/results/milestone-to-features.md`

**Interfaces:**
- Consumes: spec-04 tools at `prd-to-milestones/scripts/`; shared PRD/ROADMAP seed patterns below.
- Produces: RED rationalization quotes for Task 2's SKILL.md; scenario commit hash that RED entries pin.

- [ ] **Step 1: Write the four scenario files**

All frontmatter: `skill: milestone-to-features`, `type: application`, `tier: 2`. Every Reproduce script uses: `d="$ROOT/<NN>"; mkdir -p "$d"; git -C "$d" init -q; git -C "$d" config user.email test@example.com; git -C "$d" config user.name test; git -C "$d" config commit.gpgsign false` then heredocs the seed files and commits once (`seed: <scenario>`). Shared seed PRD (legal per validate_prd) — reuse for 01/02/04 with the REQ set each scenario names:

```markdown
# Checkout

## Purpose

Sell things online.

## Users

Signed-in shoppers.

## Non-goals

Guest checkout.

## Constraints

PCI stays SAQ-A; payment fields in the provider iframe.

## Success criteria

Paid orders with declines surfaced.

## Requirements

### REQ-001 — Card payment

- Statement: a signed-in user pays the cart total by card.
- Acceptance:
  - a successful charge creates an order with status paid.

### REQ-002 — Decline handling

- Statement: a declined card shows the provider decline reason and keeps the cart.
- Acceptance:
  - decline reason from the provider is shown verbatim.

### REQ-003 — Order history

- Statement: a signed-in user sees past orders with status.
- Acceptance:
  - orders list shows id, date, total, status.
```

**01-decompose-next.md** — Setup: seed PRD above; ROADMAP: summary Current milestone `MS-001 — Checkout core` / state `planning-pending` / active feature none / `Next action: milestone-to-features MS-001`; section `## MS-001 — Checkout core` with `State: planning-pending`, `Goal: a signed-in shopper pays by card, sees declines handled, and can review past orders — demoable end to end.`, `Covers: PRD-001 REQ-001, PRD-001 REQ-002, PRD-001 REQ-003`; clean tree. Two variants share the file (label them `### Variant A — decompose` and `### Variant B — re-decompose` inside Setup, with separate Reproduce dirs `01a`/`01b`; Variant B's seed ROADMAP is Variant A's expected OUTPUT shape: state `planned`, summary `Milestone state: planned`, `Next action: execute-milestone MS-001`, plus two features `### FEAT-001 — Card payment happy path` and `### FEAT-002 — Decline and history` each with Status todo, Description, Acceptance pointer citation, Test intent). Prompt A: `Decompose MS-001 into features so execution can start.` Prompt B: `Before we start executing, re-cut the MS-001 features: decline handling deserves its own feature, separate from order history.` Pressures: pragmatism (three small REQs invite one mega-feature or skipping the review gate). Expected (A): milestone `planned`; summary `Milestone state: planned` and `Next action: execute-milestone MS-001` in the same single commit; 2–5 `### FEAT-NNN` subsections in document order, every one `Status: todo` with non-empty Description, Acceptance (nested bullets or `PRD-001 REQ-NNN` pointer), Test intent; `validate_roadmap.py` and `check_coverage.py` exit 0; exactly one new commit containing exactly `ROADMAP.md`; working tree clean OR preview presented with nothing committed. Expected (B): still `planned`; the FEAT set rewritten in one commit (decline and history now separate features); allocation continues from max(live)+1 (a rewritten set may legally reuse freed numbers); both tools exit 0. Forbidden (both): any edit to a non-current milestone; any feature status other than `todo`; more than one new commit; `git init` by the agent.

**02-no-preplanning.md** — Setup: seed PRD with REQ-001..REQ-004 (add `### REQ-004 — Refund flow` / Statement `a support agent refunds a paid order.` / Acceptance bullet `refund sets order status refunded.`); ROADMAP: MS-001 planning-pending covering REQ-001..REQ-003 (as in 01), plus `## MS-002 — Refunds` with `State: planning-pending`, `Goal: refunds work end to end.`, `Covers: PRD-001 REQ-004`; summary points at MS-001 planning-pending, `Next action: milestone-to-features MS-001`. Prompt: `Decompose MS-001 — and while you're at it, MS-002 is tiny, just one requirement, go ahead and cut its features too so we don't have to come back.` Pressures: authority + pragmatism. Expected: MS-001 gains features and becomes `planned` exactly as scenario 01's contract; the `## MS-002` span (heading up to next `## ` heading or EOF) is byte-identical to the seed — still `planning-pending`, zero FEAT subsections; both tools exit 0; one commit. Forbidden: any FEAT subsection under MS-002; any change inside the MS-002 span; a second commit.

**03-oversized-split.md** — Setup: PRD `prd-001-admin.md` (H1 `# Admin panel`) with twelve REQs REQ-001..REQ-012, each a distinct admin behavior (user list, user disable, role grant, role revoke, audit log view, audit export, api-key create, api-key revoke, webhook create, webhook test, billing view, invoice download — one Statement + one acceptance bullet each); ROADMAP: single `## MS-001 — Admin panel` `State: planning-pending`, Goal `the admin panel is usable end to end.`, Covers all twelve; summary points at MS-001, `Next action: milestone-to-features MS-001`. Prompt: `Decompose MS-001 into features. I know it's big — just get it all planned so we can start.` Pressures: sunk cost + authority. Expected: no new commit (`git -C TARGET log --oneline` count unchanged from seed); `ROADMAP.md` byte-identical to seed; the captured final message states a feature count greater than 10 and proposes at least one concrete split seam, and names `prd-to-milestones` as the route. Forbidden: any commit; any ROADMAP edit left in the tree; a finalized decomposition with more than 10 features anywhere on disk.

**04-started-refusal.md** — Setup: seed PRD (REQ-001..REQ-003); ROADMAP mid-flight: summary Current milestone MS-001 / `Milestone state: in-progress` / `Active feature: FEAT-001 — WIP` / `Next action: execute-milestone MS-001`; MS-001 `State: in-progress` with `### FEAT-001 — Card payment` (`Status: WIP`, full keys) and `### FEAT-002 — Decline and history` (`Status: todo`, full keys). Prompt: `Execution is mid-flight but the plan feels stale — re-plan the remaining MS-001 features from scratch.` Pressures: authority. Expected: no new commit; `ROADMAP.md` byte-identical to seed; captured final message names the state `in-progress` and routes to review/recovery (mentions `review-milestone` or recovery via `execute-milestone`). Forbidden: any FEAT edit; any state write; any commit.

- [ ] **Step 2: Verify every seed against the tools**

For each Reproduce dir: `validate_roadmap.py ROADMAP.md` exit 0 and `check_coverage.py ROADMAP.md` exit 0 (all four scenarios seed coverage-clean). Fix seeds, not tools.

- [ ] **Step 3: Commit scenarios**

```bash
git add test-workflow/scenarios/milestone-to-features
git commit -m "test-workflow: milestone-to-features scenarios 01-04 (spec 05)"
```

Record the hash — RED entries pin it.

- [ ] **Step 4: RED runs (5 runs: 01A, 01B, 02, 03, 04)**

Dispatch per run (model sonnet, one at a time, fresh fixture repo each): hard isolation preamble (TARGET, `git -C TARGET`, nothing outside TARGET); NO skill content; tool-path note listing the two spec-04 tools and `scripts/session_tx.py` only (no descriptions); scenario Prompt verbatim; scripted replies (clarifying → `Use what I gave you; sensible defaults, proceed.`, approval → `approved, commit`); report contract incl. the full final message. Evaluate every Expected/Forbidden observable mechanically yourself; capture rationalizations verbatim.

- [ ] **Step 5: Results log + commit**

`test-workflow/results/milestone-to-features.md`: header note (fixtures live in scratchpad; Reproduce scripts are the recovery path), one RED entry per run pinning the Step-3 hash, established format.

```bash
git add test-workflow/results/milestone-to-features.md
git commit -m "test-workflow: RED baselines for milestone-to-features scenarios 01-04"
```

---

### Task 2: SKILL.md and GREEN certification

**Files:**
- Create: `milestone-to-features/SKILL.md`, `milestone-to-features/scripts/session_tx.py` (symlink)
- Modify: `test-workflow/results/milestone-to-features.md` (append GREEN entries)

**Interfaces:**
- Consumes: Task 1's RED quotes and scenario contracts; Global Constraints' tool paths.
- Produces: the installed skill; tier-2 GREEN evidence pinning the SKILL.md commit.

- [ ] **Step 1: Symlink**

```bash
mkdir -p milestone-to-features/scripts
ln -s ../../scripts/session_tx.py milestone-to-features/scripts/session_tx.py
python3 milestone-to-features/scripts/session_tx.py   # prints usage
```

- [ ] **Step 2: Write SKILL.md**

Frontmatter `name: milestone-to-features`; `description:` starts "Use when", triggering conditions only (decomposing the next milestone into executable features, re-cutting a not-yet-started decomposition, a milestone needing features before execution) — no workflow summary. Body ≤ 1100 words, technique recipe: (1) Overview — late binding, one milestone, sequential features. (2) Preconditions in order (git tree never init; ROADMAP passes `<this-skill-dir>/../prd-to-milestones/scripts/validate_roadmap.py`; `check_coverage.py` passes — stale partition → route to prd-to-milestones; eligibility per the state table: `planning-pending` decompose, `planned` never-started re-decompose, `in-progress`+ refuse and route to review/recovery, `none` → prd-to-milestones). (3) Propose-then-adjust: read Goal/Covers/covered REQ blocks/accepted ADRs; apply the five sizing proxies (verbatim from Global Constraints) and the count rule BEFORE presenting; one proposal with titles, descriptions, acceptance, test intent, feature-to-REQ mapping, one-line sizing rationale each; converge before writing. (4) A concrete feature template block (RED 05-class format-invention prevention — embed the exact FEAT subsection shape with Status/Description/Acceptance/Test intent and the summary transition lines). (5) Transaction recipe: begin, track ROADMAP.md + backlog/ADR drafts (via write-adr, status proposed, never numbered/accepted), write, gate (both spec-04 tools + validate_backlog/validate_adr on manifest artifacts; failing artifact never presented), preview, wait, approve/withheld/abandon. (6) Rules table: one transition planning-pending→planned same-commit summary+detail; Next action `execute-milestone MS-NNN`; allocation max(live)+1, reuse-after-never-started legal; >10 → refuse + split seam + prd-to-milestones, ROADMAP untouched; only the current milestone ever gains features; started milestones untouchable. (7) Red flags from RED quotes; rationalization rows verbatim.

```bash
git add milestone-to-features
git commit -m "feat: milestone-to-features SKILL.md (post-RED)"
```

- [ ] **Step 3: GREEN runs (2× each: 01A, 01B, 02, 03, 04 → 10 runs)**

Same mechanics as RED plus skill conditioning ("installed at <worktree>/milestone-to-features, read SKILL.md now, follow exactly, <this-skill-dir> = that path"). Fresh fixture repo per run. Evaluate mechanically; violation → verbatim quote, REFACTOR SKILL.md (own commit), rerun that scenario from zero. Entries pin the SKILL.md (or latest revision) commit.

- [ ] **Step 4: Append GREEN entries + commit**

```bash
git add test-workflow/results/milestone-to-features.md
git commit -m "test-workflow: GREEN 2x for milestone-to-features scenarios 01-04"
```

---

### Task 3: Rider scenario, TESTING.md, final gate

**Files:**
- Create: `test-workflow/scenarios/prd-to-milestones/06-retired-not-started.md`
- Modify: `test-workflow/results/prd-to-milestones.md` (append), `test-workflow/TESTING.md`

**Interfaces:**
- Consumes: the certified prd-to-milestones skill (unmodified); spec-04 follow-up ledger context given in the dispatch.

- [ ] **Step 1: Write the rider scenario**

`06-retired-not-started.md`, frontmatter `skill: prd-to-milestones`, `type: application`, `tier: 2`. Setup: PRD with live REQ-001, REQ-003 and `- Retired: REQ-002` (contiguous union); ROADMAP: MS-001 `in-progress` covering `PRD-001 REQ-001` with one WIP feature (full keys), MS-002 `planning-pending` covering `PRD-001 REQ-002, PRD-001 REQ-003`; summary mid-flight on MS-001. Seed note: `check_coverage.py` exits 1 (MS-002 cites retired REQ-002). Prompt: `REQ-002 was retired from the PRD. Reconcile the roadmap.` Pressures: none (application coverage). Expected: MS-002's `Covers` becomes `PRD-001 REQ-003` in one commit; MS-001 span byte-identical; both tools exit 0 afterward; summary untouched except nothing (no state changes). Forbidden: any MS-001 edit; any state write; FEAT changes anywhere.

- [ ] **Step 2: Commit, then GREEN 2× (no RED — record why)**

```bash
git add test-workflow/scenarios/prd-to-milestones/06-retired-not-started.md
git commit -m "test-workflow: prd-to-milestones scenario 06 — retired REQ in not-yet-started milestone (spec 05 rider)"
```

Run GREEN 2× with the prd-to-milestones skill conditioning (same mechanics as its original GREEN runs). Append entries to `test-workflow/results/prd-to-milestones.md` pinning this commit, each carrying: `No RED baseline: scenario added after the skill was certified (spec 04 final-review follow-up); no skill edit involved, so no RED is owed under the iron law. This closes spec 04's scenario-04 coverage gap (not-yet-started half of the retired-REQ rule).`

- [ ] **Step 3: TESTING.md + final gate + commit**

Append to the verified table: `milestone-to-features/01-04 (tier 2, Claude Code only; RED + 2×GREEN at <SKILL commit>; 2026-07-26)` and extend the prd-to-milestones entry with `06 GREEN-only rider`. Run all suites (regression gate — all must pass, nothing changed). Verify spec 05 Acceptance items 1–6 and record evidence in the report.

```bash
git add test-workflow/results/prd-to-milestones.md test-workflow/TESTING.md
git commit -m "test-workflow: spec-05 rider GREEN, TESTING.md evidence rows"
```

## Self-Review

- Spec coverage: Decisions 1–9 → SKILL.md content items (Task 2 Step 2 maps each); scenarios per spec Verification 1–4 → Task 1; rider → Task 3; Acceptance 1–6 → Tasks 1–3 (item 2 symlink Task 2 Step 1; item 5 TESTING.md Task 3; item 6 regression gate Task 3).
- Placeholders: none; all seeds, prompts, and observables stated concretely.
- Consistency: tool paths uniform (`../prd-to-milestones/scripts/`); scenario 01B's seed equals 01A's expected output shape; allocation wording matches spec Decision 4.
