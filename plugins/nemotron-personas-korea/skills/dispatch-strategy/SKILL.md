---
name: dispatch-strategy
description: Caller-side dispatch strategy for the `nemotron-personas-korea:persona-respondent` subagent — which mode (one-per-dispatch / inline batch / file-read batch), how many parallel subagents, and the announce-before-launch format. TRIGGER when planning persona-respondent dispatches, sizing fan-out for Nemotron persona survey calls, batching personas for closed-form Likert/binary/multi-choice work, or any time the user requests Korean persona survey runs through subagents. Also TRIGGER when the user says "use the agent" in the context of persona work, or asks about parallel dispatch / concurrency / batch size for persona-respondent.
---

# Dispatching `persona-respondent`

Before each Agent-tool call to `nemotron-personas-korea:persona-respondent`, the caller picks two things — **dispatch mode** and **concurrency** — and announces both in one line so the user can override before launch.

## Lane 1: dispatch mode

| Mode | When |
|---|---|
| **one-per-dispatch** | N ≤ 3, OR interview-depth / free-text / opinion-projection (character fidelity matters; the "stay strictly in character" guarantee is strongest here). |
| **inline batch** (`### Persona i=NN` blocks in the dispatch prompt) | Only when per-persona prompt < 1 KB AND total batch < 5 KB. Bad fit for Korean: 3 KB CJK costs ~29 s/dispatch s_emit and collapses concurrency to ~1× regardless of cap. |
| **file-read batch** (`READ_PERSONA_BATCH <abs-path>` on line 1) | Default for closed-form Likert / binary / multi-choice at N ≥ 5, especially with large CJK content. ~50-byte dispatch + agent reads from disk → real concurrency. Protocol is documented in the agent file. |

Validated batch size: **10 personas per agent** for closed-form work.

## Lane 2: concurrency (parallel subagents)

Cap: ~4 in-flight, global across agent types in the Claude Code harness.

| N | subagents × personas-each |
|---|---|
| 1–3 | N × 1 |
| 4–10 | 1 × N |
| 11–40 | ⌈N/10⌉ × 10 (may saturate cap) |
| 41–400 | ⌈N/10⌉ × 10, waved through cap=4 |
| >1000 | direct API, only if the user has opted in (see Defaults) |

## Defaults

- **Always persona-respondent for persona role-play.** Don't fork to `general-purpose` for "closed-form factual" cases. The ~6–12% per-dispatch throughput delta (GP ~1.20 s vs persona-respondent ~1.85 s) isn't worth the per-dispatch decision tax or the silent fidelity loss when GP gets misclassified for a question that turns out to project opinion. Reserve GP for non-persona tasks (code search, planning, data inspection).
- **MAX subscription via Agent over direct API.** Default to Agent tool dispatches against the Claude Code MAX session. Only use `AsyncAnthropic` / direct API when the user explicitly opts in for the run. The OTPM math from the cross-project parallelism lesson caps Agent concurrency — it is not an automatic signal to switch to the API.

## Announce format

One line, before launch:

> N=10, file-read batch, 1 subagent × 10 personas (cap not exercised).

For fan-out:

> N=80, file-read batch, 8 subagents × 10 personas, waves through cap=4 (~3× speedup vs serial).

Skip only for trivial N=1 single dispatches.

## Further reading

For the empirical model behind the cap and batch-size choices (~4 in-flight global cap, ~29 s/dispatch s_emit penalty on 3 KB CJK prompts, validated batch-of-10 + fan-out-of-10 → 3–6× speedup on closed-form survey work), see `~/.claude/rules/lessons/claude-code-agent-tool-parallelism.md` and the `agent-tool-throughput` skill when installed.
