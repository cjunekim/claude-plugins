---
name: dataset
description: Field semantics, schema quirks, sampling-relevant facts, and survey-instrument design lessons (Likert anchor wording, debias, distribution validation) for the `nvidia/Nemotron-Personas-Korea` HuggingFace dataset (1M synthetic Korean adults, calibrated to KOSIS / Supreme Court / NHIS marginals, CC BY 4.0). TRIGGER when code references `nvidia/Nemotron-Personas-Korea` or imports `datasets` for Korean persona work; or the user mentions Nemotron-Personas, the Korean personas dataset, persona role-play with Korean adults, synthetic Korean adult survey/interview research, or designing/interpreting Likert instruments for LLM-as-respondent surveys on this dataset. Includes a re-runnable inspection script (`scripts/inspect_dataset.py`), a portable persona-loader (`scripts/load_persona.py`), and a SHA-pinned snapshot of findings (`references/inspection-snapshot.md`).
---

# Nemotron-Personas-Korea

`nvidia/Nemotron-Personas-Korea` is 1,000,000 synthetic Korean adults (ages 19–99), calibrated to KOSIS / Supreme Court / NHIS marginals, CC BY 4.0. Each row is one persona with demographics, a compact one-sentence summary, and ten richer narrative fields.

## Before loading the dataset — confirm cache location

The dataset materializes **~5.76 GB on disk** (1.85 GB compressed parquet + 3.91 GB arrow cache for fast iteration). Cache location is governed by `HF_HOME`. **Confirm with the user before running the bundled `scripts/inspect_dataset.py` or any code that calls `load_dataset("nvidia/Nemotron-Personas-Korea", ...)`.**

Check the current `HF_HOME` value. If it is unset, the cache lands at `%USERPROFILE%\.cache\huggingface` on Windows — i.e., the system drive, which is usually not what the user wants. Ask explicitly, e.g.:

> "HF_HOME is currently `<value>` (or unset → defaults to `%USERPROFILE%\.cache\huggingface`). The dataset will cache ~5.76 GB. Where should I put it — project-local `./hf-cache`, a dedicated drive, or the default?"

Don't run the load until the user has confirmed.

## Schema (26 columns)

**Identity** — `uuid`.

**Demographics** — `sex` (`남자` / `여자`), `age` (`int64`, 19–99), `province` (17 distinct values, abbreviated — see quirks), `district` (`{short-province}-{city/gu}`, e.g. `서울-강서구`), `education_level`, `marital_status`, `family_type`, `housing_type`, `occupation`, `military_status`, `bachelors_field`, `country` (constant).

**Compact persona** — `persona`. One sentence, ~50 words. The right field for closed-form survey answers; over-narrative makes the LLM pattern-match on hobbies and skews short answers.

**6 narrative facets** (~2–4 sentences each) — `professional_persona`, `sports_persona`, `arts_persona`, `travel_persona`, `culinary_persona`, `family_persona`. Right for interview-depth use cases.

**4 supplementary narrative fields** — `cultural_background`, `skills_and_expertise`, `hobbies_and_interests`, `career_goals_and_ambitions`.

**2 list-form variants** — `skills_and_expertise_list`, `hobbies_and_interests_list` (Python-list-as-string).

## Field-semantics quirks

These bit during inspection on a real project; surface them up front when designing prompts or analyses.

- **`province` uses non-standard abbreviated naming, internally inconsistent.** Values are `경기` (not `경기도`), `서울`, `부산`, etc. — and the Jeolla pair is asymmetrically shortened: `전북` is doubly-shortened (전라북도 → 전북) while `전라남` is singly-shortened (전라남도 → 전라남). Comparing to KOSIS data needs a name-map; charts should use dataset values for fidelity.
- **`district` already includes the short-province prefix.** Format is `{short-province}-{city/gu}`, e.g. `경상북-문경시`, `서울-강서구`. A prompt that injects `{province} {district}` produces redundant double-counted location like `경상북 경상북-문경시`. Use `{district}` alone, or `{province}` alone — never both.
- **`age` is `int64`, not pre-binned.** Bin manually if you need bands.
- **`military_status` returns `비현역` for ineligible rows** (older women, etc.) — not a clean indicator of actual military service.
- **`bachelors_field` is `해당없음` for non-bachelor's-degree holders** — filter before any field-of-study analysis.
- **`country` is constant `대한민국`** — drop entirely from any extension that uses this dataset.

## Choosing which fields to inject

Decide per question, not by use mode. For each candidate narrative field, ask: **does this field plausibly inform the answer?**

- **Always include** the compact `persona` field and the structured demographics block. Cheap, universally relevant.
- **Include facets that touch the question's domain.** Travel question → `travel_persona`. Food question → `culinary_persona`. Consumer adoption / brand / spending → `professional_persona` (income & role-derived priorities), `hobbies_and_interests` (consumption-category cues), `career_goals_and_ambitions` (forward-looking attitudes). Don't include `sports_persona` for a question about banking apps just because the field exists.
- **When in doubt, include.** Information loss from a missing field is harder to recover than slight over-pattern-matching from an extra one. If you can construct any plausible mechanism by which the field touches the answer, include it. Reserve exclusion for facets that are clearly orthogonal to the question.
- **The over-pattern-matching warning is real but narrow.** For closed-form (Y/N, Likert, multi-choice, numeric), an *irrelevant* facet — vivid hobby detail in a question about something else — can crystallize the answer onto a personality adjective rather than the persona's actual circumstances. The fix is field selection, not blanket suppression of narrative depth.
- **Interview / qualitative depth** — default to all 10 narrative fields (6 `*_persona` + 4 supplementary). Multi-turn conversation needs the texture; selective inclusion makes responses feel generic.

**Hand-off to `nemotron-personas-korea:persona-respondent`**: when dispatching to that sub-agent, your prompt IS the hand-off — there is no separate metadata channel. The agent's md file (`agents/persona-respondent.md`) reads the prompt under the assumption that you followed this guidance. Selecting fields well here directly shapes the agent's response quality on the receiving end.

## Throughput patterns and dispatch strategy

Claude Code's Agent tool has a **global concurrency cap of ~4** simultaneous sub-agent dispatches, applied across all subagent types. Per-dispatch overhead is type-dependent: `nemotron-personas-korea:persona-respondent` ≈ 1.85s/dispatch (plugin loading); `general-purpose` ≈ 1.2s/dispatch. The cap binds only when per-call work-time `W` is large (~25s+); at short W (~1–2s, e.g., binary Y/N or single Likert), overhead dominates and fan-out gives no speedup.

### Use single-persona-per-dispatch (`persona-respondent`) for:

- Long-form work: free-text responses, multi-turn interviews, anything ≥10s of generation.
- Voice-fidelity matters: per-persona register is critical (e.g., 22-year-old student vs. 65-year-old retiree distinct prosody).
- N ≤ 10 items at long W (cap binds at ~4× speedup with fan-out).

### Use batched-via-`general-purpose` for closed-form high-volume work

For binary, Likert, multi-choice, ≥30 items:

- **Pattern**: dispatch `general-purpose` agent with `persona-respondent`'s system instructions inlined into the user prompt, plus a multi-persona instruction.
- **Recommended batching**: 10 personas per agent prompt; fan out to ~10 agents per round. Cap binds at ~4× during a round.
- **Strict per-persona output format**: e.g., `i=NN: <answer>` one line per persona. Anchors structured output and minimizes blending.
- **Don't bother randomizing order** — per-persona answers stable across reorderings (validated: 18/20 personas range ≤1 across 3 random orderings on a Likert question).

### Validated empirically (2026-05-09)

- **Correctness:** 100/100 correct on a binary marriage question (marriage100 run). 60 personas via `persona-respondent` one-shot + 40 via batched-`general-purpose`, all matching ground truth.
- **Likert distribution:** batched produced *wider* distributions than one-shot dispatch (mean 2.85, std 1.24 vs. one-shot mean 2.50, std 1.00 with 11/20 clustered on safe-default-2). Cross-persona context provides implicit anchoring scale that corrects one-shot's central-low bias. **The pollution risk in the predicted direction was not observed.**
- **Order-independence:** mean=2.80±0.05 and std=1.24±0.01 across original/reversed/shuffled orderings (n=3 replicates × 20 personas).

### Caveats

- **Mild length-compression under batching for free-text** (~27% lower per-persona length variance, std 8.1 vs 11.1 chars). The strict format prompt enforces uniform output style. If length is a measured outcome, prefer one-shot.
- **Voice/register fidelity weaker under batching** (attention spans all personas in one call). For interview-depth or stylistic-distinctness work, stick with one-shot via `persona-respondent`.
- **Mixing agent types does NOT increase throughput.** A 5×PR + 5×GP dispatch yields the same ~4× concurrency as 10 of either type alone — the cap is global.

For full empirical evidence on the parallelism model (concurrency cap, per-type overhead, decisive experiments), see `~/.claude/rules/lessons/claude-code-agent-tool-parallelism.md`.

## Population characteristics that affect sampling design

- **Ages skew older.** Mean 50.7, median 51 (the 1M-row population, not a calibrated reference). For sex × age-band stratification at small N (~300), the small cells are 19-29, NOT 60+ as one might predict. Sample-size floors to protect crosstab cells should target 19-29.
- **17 provinces.** Stratifying on sex × age × province (8 × 17 = 136 cells) is too thin at N=300. For pilot scale, stratify on sex × age band only and report the realized 17-row province distribution; full province-stratification only becomes feasible at N ≥ ~1500.

## Designing closed-form survey instruments

Empirical findings from a five-iteration ladder on this dataset (binary → Likert → debias → softened-extremes, N up to 200) for an "early adopter" attitudinal question. Surface these up front when designing any new closed-form instrument on this dataset.

**Anchor wording strictness drives endorsement asymmetry.** A scale that *looks* symmetric on paper produces asymmetric distributions because the LLM weights the extreme labels through cultural-acceptability and narrative-justifiability filters.
- "매우 그렇다, 무조건 갈아탄다" (cell 5) → 0% endorsement across N=170 even with explicit debias instruction. Sounds immodest in Korean (self-promotion taboo).
- "전혀 아니다, 견딜 수 없을 때까지" (cell 1) → after debias, jumped from 0% to 16% (Rogers-matching). But also vacuumed mass from cell 2's natural endorsers, leaving cell 2 over-filled by +16.5 pp because cell 1 is too strict for borderline late-majority types.
- Net failure mode: distribution mean matches normative reference (2.46 vs Rogers' 2.52) but χ² rejects shape match (29.0, p<10⁻⁵), variance is 33% too small.

**Always include a debias instruction** in the question text: `솔직하게 대답해야 하며, 1부터 5까지 응답 모두를 활용해야 합니다. 1이나 5로 답하는 것을 주저하지 마세요.` Recovers the negative tail much more reliably than the positive — observed +16% to cell 1 but only +0.5% to cell 5 — but is necessary for both directions.

**Soften both extreme anchors symmetrically.** Avoid absolutist language ("전혀 ~", "매우 ~", "무조건 ~", "절대 ~") at both cells 1 and 5. The replacement should be endorsable without sounding boastful or self-deprecating in Korean.
- Replace `매우 그렇다, 무조건 X` with `상당히 그렇다, 적극적으로 X` — keeps directional commitment, loses bombast.
- Replace `전혀 아니다, X 할 때까지 안 한다` with `거의 아니다, 보통 X하지 않는다` — keeps direction without requiring near-pathological commitment.

**Validate by bin-level distribution comparison, not just mean.** Compute χ² against a normative reference (Rogers' diffusion curve for adoption questions, NHIS/KOSIS marginals for demographics, etc.). Report cell-by-cell percentages, cumulative distributions, and variance separately. A "matching mean" with χ² rejection is the failure mode this caution is about.

**Expect persistent residuals** even with best practices: ~30% variance compression and 0.05-0.10 mean-shift relative to the normative reference. These are the central-tendency residual that survives debias + symmetric anchoring. Pre-register tolerances so you don't move the goalposts.

**Subgroup-stratified analysis is more reliable than overall comparison.** Within-cell distributions (e.g. 19-29 women) often match the normative reference more cleanly than the overall sample, because the dataset's narratives encode genuine demographic variation. Use overall χ² as a screening test, then look at subgroups for the actual signal.

### The diagnostic ladder — distinguishing "no signal in the data" from "instrument can't read the signal"

A single run that returns a flat / clipped / suspicious distribution is *ambiguous between two very different causes*: (a) the persona narratives genuinely don't encode the trait you're asking about, or (b) the instrument's wording is filtering the signal out before it can be reported. From one run you cannot tell these apart — the symptom is identical.

The diagnostic move is **a ladder of runs that change one element at a time**, holding everything else constant. The early-adopter ladder above: the first three runs (binary → Likert → larger N Likert) all pointed toward "no early-adopter signal in this dataset" and would have been a wrong conclusion. Run 4 (debias instruction) recovered the laggard tail, demonstrating that the *instrument* was the problem, not the data. Run 5 (softened cell-5 anchor) recovered the innovator tail and confirmed the diagnosis.

**Do not conclude anything from a single suspicious run.** Plan to run at least 3–4 follow-ups, each changing exactly one element (anchor wording, debias instruction, scale type, framing, field selection). Treat the *evolution across the ladder* as the primary evidence.

## Bundled assets

- **`scripts/inspect_dataset.py`** — a standalone inspection script. Pins the dataset SHA, dumps schema + dtypes, samples 3 random rows in full, computes text-field length comparisons (which identifies the compact `persona` vs. the long narrative fields), reports the `province` distribution, and computes sex × age-band marginals with proportional N=300 allocation. Re-run on first contact in a new project, or whenever the dataset SHA may have changed, to verify findings against the live dataset.
- **`scripts/load_persona.py`** — standalone loader (just `datasets` + pandas, no project-specific imports). Takes `--uuid <id>` or `--filter "sex=여자,age>=30,province=서울"` and emits all 21 persona-relevant fields in `=== <fieldname> ===` blocks suitable for piping into a prompt builder. Used by the `persona-respondent` agent and `/persona-interviewee` command for portable persona loading.
- **`references/inspection-snapshot.md`** — a SHA-pinned snapshot of the script's output. Treat as a frozen reference, not a live spec — re-run the script and diff if the SHA has moved.

## Environment variables

- **`HF_HOME`** — HuggingFace's standard. Governs where `load_dataset` caches the ~5.76 GB dataset materialization. Set this BEFORE any load to keep the cache off the system drive (Windows default: `%USERPROFILE%\.cache\huggingface`).
- **`NEMOTRON_INTERVIEWS_DIR`** — used by `/persona-interviewee --save` for transcript output. Defaults to `./nemotron-interviews/` in the current working directory if unset.

## When to re-run inspection

- **First contact in a new project** — verify the snapshot still matches the live dataset.
- **Suspected schema drift** — the dataset is on HuggingFace; the maintainers can revise it.
- **An architectural decision cites a specific column or value** — confirm before committing.

The script itself runs in a few minutes wall-clock once the dataset is cached. (For first-time cache placement, see "Before loading the dataset" above.)
