---
name: academia-research
description: Research an academic topic or compare a body of publications using primary sources. Use for literature reviews, research-landscape maps, paper comparisons, and evidence-based state-of-the-art questions; not for extracting or summarizing one supplied paper.
---

# Academic Research

## Outcome

Match the work to the request:

- For a focused literature question, inspect the decisive sources and answer in the requested format.
- For a field survey or literature review, produce a coherent Markdown report whose important claims are traceable to inspected sources.

The user's scope, format, and output location take priority. If format and location are unspecified, answer a focused question in chat; for a survey, write one `[topic].md` report in the working directory and create no auxiliary files.

## 1. Define Scope

Turn the request into explicit research questions and boundaries. For a focused comparison of named works, use the requested comparison axes, verify the latest canonical versions and correction or retraction status, and skip review protocol and broad discovery unless the answer needs more context. For a survey or current-state question, record an exact search cutoff date.

State reasonable assumptions. Ask one concise question only when unresolved ambiguity would materially change source selection or the answer; a large field or a small evidence base alone is not a reason to stop.

For a survey, use `narrative review` by default. Use `systematic review` or `scoping review` only when the work follows a reproducible protocol with named databases, queries, search dates, inclusion and exclusion criteria, and a documented screening process.

For a broad survey, define representative coverage before searching. If the user names several areas, treat them as required coverage and plan the split internally.

Scope is complete when the research questions and boundaries are clear; for a survey, the coverage limits, review type, and cutoff date must also be clear.

## 2. Build the Evidence Base

For a focused question, start with the named or decisive original sources and expand only to resolve a discrepancy or support a broader claim.

For a survey, choose sources and search systems appropriate to the field. Use scholarly indexes for discovery, then inspect canonical publisher pages, venue proceedings, repositories, standards, datasets, and original studies. Build query families from domain terms, synonyms, acronyms, methods, outcomes, and exclusions.

Seed discovery with relevant reviews and known anchor papers. Follow important references backward and citations forward. Search for related work, independent replications, negative or conflicting results, critiques, corrections, and retractions.

Rank sources by relevance and evidence quality. Stay within the user's date and source boundaries; use older foundational work only as clearly marked context when needed. Include the strongest current evidence, and use newest-first searches only to scan the research frontier. Prefer the final peer-reviewed publication, deduplicate its preprint, and label work that remains a preprint.

Use secondary sources for orientation or synthesis and trace concrete methods and results to the original work. Treat institutional or vendor material as evidence of what that organization reports. Use informal discussion only to discover stronger sources.

For a broad survey, track each research question and theme in a coverage matrix. Source counts guide workload, not quality or stopping. Stop when every matrix item has supporting or conflicting evidence, or an explicit evidence gap, and one final independent search or citation pass changes neither the included evidence nor the conclusions.

## 3. Verify Claims

Keep an evidence record for every source that may drive a conclusion or comparison:

- Exact title, authors or organization, year, venue and publication status, DOI or stable canonical URL.
- Claim supported and its location in the source, such as a section, page, table, figure, or appendix.
- Study design, data, evaluation conditions, main result, stated limitations, and independent replication status when relevant.

Inspect the full text and any available relevant supplement before reporting technical or quantitative detail. If only an abstract is accessible, label the source `abstract-only` and report only what the abstract supports. Search snippets are discovery aids, not evidence.

Cite each material factual claim near the claim. For every number, capture the dataset and version, split, metric and units, evaluation protocol, model or system version, sample size and uncertainty when reported, relevant hardware or compute conditions, and source location. Mark missing conditions as `not reported` or `not applicable`; do not estimate them.

Compare results only when their conditions are compatible. Otherwise present them separately and explain the mismatch. Use `state of the art` only for a named task and protocol at the stated cutoff date, and distinguish author-reported results from independent reproduction.

## 4. Scale with Delegation

Use parallel agents when a broad scope has independent branches. Give each agent its boundaries, known sources, and the evidence-record fields above. Require exact source links and support locations, not prose alone.

Treat delegated findings as leads. The synthesizing agent reopens every source behind a key conclusion, quantitative claim, or comparison row. Agreement between agents is not source verification.

For a focused question, work directly unless delegation adds clear value.

## 5. Synthesize

Organize the answer around the research questions, methods, or competing explanations rather than paper-by-paper summaries. Put conflicting evidence beside the claim it challenges. Separate sourced findings from your inference, and label conclusion strength as `convergent`, `single-study`, `preliminary`, `disputed`, or `no direct evidence` when that distinction helps.

Use comparison tables only for aligned evidence. Include technical implementation, reproducibility, policy, clinical, or business analysis only when requested or material to the research question. Time-stamp market, pricing, funding, deployment, and adoption claims.

For the default survey report, use this compact structure and omit conditional sections that add no supported value:

```markdown
# [Topic]

## TL;DR
[Direct answer, scope and cutoff, main evidence, confidence, and key limitation]

## Scope and Method
[Research questions, review type, searches, selection rules, and coverage limits]

## Findings
[Subsections organized by research question or theme]

## Comparison
[Conditional: only aligned methods or results]

## Evidence Limits and Open Questions
[Conflicts, bias, missing evidence, and unresolved questions]

## References
[Every cited source; no uncited entries]
```

In a survey report, references must include exact title, authors or organization, year, venue or status, and DOI or stable canonical URL.

## 6. Quality Gate

Apply the relevant checks to a focused answer and every check to a survey report. Finish only when:

- Every research question is answered or marked as an evidence gap.
- Every material claim is cited near the claim, and every cited source was inspected to the depth the claim requires.
- Bibliographic metadata, publication status, source links, and support locations are verified for conclusion-driving evidence.
- Numerical comparisons use compatible conditions or state why comparison is unsafe.
- Foundational context, current evidence, and material counterevidence are represented where relevant and within the stated boundaries.
- For a survey, the method, cutoff date, uncertainty, inference, and coverage limits are explicit.
- The report contains no invented sources, uncited reference entries, or unsupported claims.
