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

**No hard cap ≤24** (measured 2026-05-30; was ~4 on older Claude Code versions — re-measure, never trust a remembered cap). Main-session Agent dispatch is **launch-rate-bound, not cap-bound**: the ~1.8 s/dispatch emit is the bottleneck, and `wall ≈ N·1.8 s + W`. Useful parallelism = Little's law `L = W / 1.8 s`. Dispatch in ONE continuous stream — don't batch-and-wait (barriers waste time).

| Work | per-dispatch W | fan out up to (≈ W/1.8 s) |
|---|---|---|
| closed-form, batch-of-10 | ~10–15 s | ~8 dispatches at once |
| long free-text / self-image, one-per | ~45 s | ~25 at once |

| N | subagents × personas-each |
|---|---|
| 1–3 | N × 1 (one-per) |
| 4–10 | 1 × N closed-form; or N × 1 for free-text |
| 11–80 | ⌈N/10⌉ × 10 closed-form, all launched at once (≤~8 batches run concurrently) |
| 81–400 | ⌈N/10⌉ × 10, streamed (extra batches queue behind the launch emit, NOT a cap) |
| >1000 | direct API, only if the user has opted in (see Defaults) |

Beyond `L`, extra fan-out adds no parallelism (early agents finish before late ones launch), only context bloat. ⚠️ MAX-subscription rate limits may throttle below `L` at high fan-out — untested; if dispatches stall at ~20–25 concurrent, that's the real ceiling. The **dynamic-workflow runtime is a SEPARATE path**, hard-capped at `min(16, cores−2)` (=6 on an 8-core box) — don't confuse it with the no-cap Agent path.

## Defaults

- **Always persona-respondent for persona role-play.** Don't fork to `general-purpose` for "closed-form factual" cases. The ~6–12% per-dispatch throughput delta (GP ~1.20 s vs persona-respondent ~1.85 s) isn't worth the per-dispatch decision tax or the silent fidelity loss when GP gets misclassified for a question that turns out to project opinion. Reserve GP for non-persona tasks (code search, planning, data inspection).
- **MAX subscription via Agent over direct API.** Default to Agent tool dispatches against the Claude Code MAX session. Only use `AsyncAnthropic` / direct API when the user explicitly opts in for the run. The OTPM math from the cross-project parallelism lesson caps Agent concurrency — it is not an automatic signal to switch to the API.

## Announce format

One line, before launch:

> N=10, file-read batch, 1 dispatch × 10 personas (single dispatch, no fan-out needed).

For fan-out:

> N=80, file-read batch, 8 dispatches × 10 personas, all launched at once (no cap ≤24; bottleneck is the ~1.8 s/dispatch launch emit).

Skip only for trivial N=1 single dispatches.

## Further reading

For the empirical model behind the concurrency and batch-size choices (NO hard cap ≤24 as of 2026-05-30 — launch-rate-bound via Little's law `L = W/1.8 s`; ~29 s/dispatch s_emit penalty on 3 KB CJK prompts; validated batch-of-10; dynamic-workflow runtime separately capped at `cores−2`), see `~/.claude/rules/lessons/claude-code-agent-tool-parallelism.md` and the `agent-tool-throughput` skill when installed. The cap has moved 4× across versions — always re-measure, never quote from memory.
