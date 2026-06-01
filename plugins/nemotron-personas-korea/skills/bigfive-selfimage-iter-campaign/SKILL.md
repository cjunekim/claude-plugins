---
name: bigfive-selfimage-iter-campaign
description: Augmentation-iteration variant of the Big Five selfimage pipeline — runs new prompt-engineering iterations ON TOP OF a locked V4 baseline sample for paired comparison. TRIGGER when the user asks to run "an iter on top of iter11", test a new augmentation against the iter11 baseline, design a new [관심사] / [동네에서의 모습] / [어휘 습관] variant, push a specific Big-Five trait's Cohen w against the Korean human reference, or replicate / extend the iter1-iter14 campaign of 2026-05-25 → 2026-05-28. Also TRIGGER on phrases like "iter NN on bigfive_selfimage", "new augmentation brief", "test against iter11", "build v16/v17/etc.", "compare two augmentation strategies on n=50". The base `bigfive-selfimage-run` skill handles fresh runs; this skill handles paired iter ladders that build on iter11's mean w = 0.300 recipe. DON'T use this skill for first-time Big Five runs or n>50 production runs — those go through `bigfive-selfimage-run` and the n=300 / n=500 scaling path. DO use this skill for ANY prompt-engineering work that compares against iter11 or extends the augmentation campaign.
---

# Big Five selfimage — iter-campaign runbook (augmentation variant)

This skill covers the augmentation-iteration workflow developed across iter1–iter14 (2026-05-25 → 2026-05-28). Each iter generates a per-persona narrative augmentation, folds it into Pass 1's persona_block, runs the full two-pass pipeline against the locked V4 baseline sample, and compares against iter11 (the campaign-best recipe at mean w = 0.300 vs the Korean human reference).

If you want a **fresh** Big Five selfimage run (new sample, no augmentation), use `bigfive-selfimage-run` instead. This skill assumes the V4 baseline already exists and the goal is paired comparison.

## Current best baseline — iter11 v12

Recipe (replicate this if you need a known-good run):

- **Sample**: `runs/big_five_selfimage_n50_pertrait_20260525-172312/persona_sample.parquet` (50 personas, 19-65 working-age, V4 design)
- **Augmentation**: two facets appended inside `persona_block`
  - `[관심사]` — 2 flowing sentences on Openness content (creative output + 인문서 한두 챕터 + 추상 사유 + 미적 감수성)
  - `[어휘 습관]` — **EXACTLY** the flat declarative template: `"X 씨는 평소 말과 글에 A와 B를 자연스럽게 섞어 쓰는 편입니다"` (1 sentence, no audience, no listener, no setting). This template is uniquely context-free AND uses an active behavior verb (`쓰는 편`). Empirical campaign showed any deviation from this template either reintroduces social context (iter12) or compresses E variance via regression-to-mean (iter13). See [[lessons-iter12-iter13-iter14-diversity-and-inventory-attempts]].
  - `[동네에서의 모습]` — 3 flowing sentences with: (a) positive E participation (모임 합류, 먼저 안부), (b) one C-softener (흐지부지된 / 다 못 끝낸), (c) one bluntness moment (짧게 거절 / 솔직하게 짚어), (d) one N grounding (별 탈 없이 / 크게 흔들리지 않고)
- **Pass 1**: `personality_image_prompt(paragraphs='per_trait')` with the standard `BIG_FIVE_FACET_INVENTORY` (6 facets per OCEAN). DO NOT add a 7th O facet — iter14 tested this and regressed mean w 0.300 → 0.407.
- **Pass 2**: per_item verbal-anchor format with reworded q11 + symmetric ANCHOR_BLOCK
  - q11 reworded: `"일상에서 다양한 어휘를 사용한다."` (instead of `"어려운 말을 사용한다."`)
  - Anchor: `1 = 매우 그렇지 않다` (instead of `전혀 그렇지 않다`)
  - Format: each item answered as `<question text>` / `<digit>. <label>` on its own pair of lines, blank line between items
- **Score**: per_item parser (chunked regex on blank-line-separated blocks); Cohen w vs `KOREAN_HUMAN_REFERENCE`

iter11 result (n=50): O 0.42, C 0.26, E 0.09, A_sex 0.29, N 0.44, mean w = 0.300. Five of six strict goal checks pass against iter7 baseline — only A_sex regresses by +0.06.

## Phase 1 — Write the v_NN augmentation brief

Create `scripts/_o_augment_pilot/_build_gen_prompts_v<NN>.py`. Use iter11's v12 (`_build_gen_prompts_v12.py`) as the template. Edit only the brief content; keep the persona iteration scaffolding identical. The brief should:

- State the OUTPUT FORMAT (which bracketed facets, sentence counts)
- List 3 reference examples spanning education / region demographics
- Enumerate HARD CONSTRAINTS as numbered list (banned tokens, required elements)
- End with a final reminder paragraph

Run the builder:
```
PYTHONIOENCODING=utf-8 PYTHONPATH=. .venv/Scripts/python.exe scripts/_o_augment_pilot/_build_gen_prompts_v<NN>.py
```

It writes 50 prompt files to `scripts/_o_augment_pilot/gen_prompts_v<NN>/persona_<uuid8>.txt`.

## Phase 2 — Dispatch augmentation generation (general-purpose subagents)

50 dispatches across 2 batches of 25. **Use `general-purpose`, NOT `persona-respondent-v2`** — augmentation generation is a writing task, not a role-play.

Per-dispatch prompt template:
```
Read G:/temp/nemotron/scripts/_o_augment_pilot/gen_prompts_v<NN>/persona_<uuid8>.txt and follow its instructions exactly. The file contains a generation brief plus a Korean persona. Produce the bracketed facets requested. Save ONLY the facets (with their bracketed labels, no preamble, no explanation, no closing remarks) to G:/temp/nemotron/scripts/_o_augment_pilot/gen_outputs_v<NN>/persona_<uuid8>.txt
```

Wall-clock: ~30s/dispatch, no hard cap ≤24 (launch-rate-bound, `wall ≈ N·1.8 s + W`) → ~2–3 min for both batches.

Verify count: `ls scripts/_o_augment_pilot/gen_outputs_v<NN>/ | wc -l` must equal 50. Spot-check 2 files for compliance with the brief's hard constraints. If the brief enumerates forbidden tokens, audit:
```
cd scripts/_o_augment_pilot/gen_outputs_v<NN> && for f in persona_*.txt; do awk '/^\[FACET\]/{getline; print}' "$f"; done | grep -E "FORBIDDEN_TOKEN_1|FORBIDDEN_TOKEN_2"
```
Zero matches before proceeding.

## Phase 3 — Materialize the iter run directory

Write `scripts/_o_augment_pilot/_materialize_iter<MM>.py`. Use iter11's `_materialize_iter11.py` as the template. The materializer:

- Reads 50 augmentations from `gen_outputs_v<NN>/`
- Reuses the V4 baseline sample (DO NOT generate a new sample)
- Builds Pass 1 prompts with the augmentation appended inside `persona_block`
- Creates run dir: `runs/big_five_selfimage_n50_iter<MM>_v<NN>_<ts>/`
- Subdirs: `pass1_prompts/`, `pass1_selfimages/`, `pass2_prompts/`, `pass2_replies/`

Run:
```
PYTHONIOENCODING=utf-8 PYTHONPATH=. .venv/Scripts/python.exe scripts/_o_augment_pilot/_materialize_iter<MM>.py
```

Capture the absolute run dir path for Phase 4 dispatch prompts.

## Phase 4 — Dispatch Pass 1 (persona-respondent-v2)

Same shape as `bigfive-selfimage-run` Phase 2: `READ_PERSONA_BATCH` + `SAVE_REPLY_TO`, 50 dispatches in 2 batches of 25. Wall-clock: ~40s/dispatch, no hard cap ≤24 (`wall ≈ N·1.8 s + W`) → ~2.5–3 min.

```
READ_PERSONA_BATCH <abs-path-to>/pass1_prompts/persona_<uuid8>.txt
SAVE_REPLY_TO <abs-path-to>/pass1_selfimages/persona_<uuid8>.txt
```

Verify count after each batch: `ls .../pass1_selfimages/ | wc -l` should equal 25, then 50.

## Phase 5 — Build Pass 2 prompts (per_item format + symmetric anchor)

Write `scripts/_o_augment_pilot/_build_pass2_iter<MM>.py`. Use iter11's `_build_pass2_iter11.py` as the template. Two non-default elements:

```python
REWORDED_Q11 = "일상에서 다양한 어휘를 사용한다."
QUESTIONS_REWORD = list(QUESTIONS)
QUESTIONS_REWORD[10] = REWORDED_Q11

SYMMETRIC_ANCHOR_BLOCK = (
    "[척도]\n"
    "1 = 매우 그렇지 않다\n"          # was: 전혀 그렇지 않다
    "2 = 어느 정도 그렇지 않다\n"
    "3 = 보통이다\n"
    "4 = 어느 정도 그렇다\n"
    "5 = 매우 그렇다"
)
```

And the per_item format spec (replaces the digit-batch default):
```python
PER_ITEM_FORMAT_SPEC = """[응답 형식]
12개 문항 각각에 대해 다음 두 줄 형식으로 한국어로 응답해 주세요:

  <문항 텍스트를 그대로 다시 적기>
  <응답 숫자>. <응답 라벨>

문항 간에는 빈 줄(공백 한 줄)로 구분해 주세요. ..."""
```

Run:
```
PYTHONIOENCODING=utf-8 PYTHONPATH=. .venv/Scripts/python.exe scripts/_o_augment_pilot/_build_pass2_iter<MM>.py
```

## Phase 6 — Dispatch Pass 2

Same shape as Phase 4 — `READ_PERSONA_BATCH` + `SAVE_REPLY_TO` × 50, two batches of 25. Pass 2 replies are short (~12 lines): ~13s/dispatch, no hard cap ≤24 — launch-emit-dominated (`wall ≈ N·1.8 s + W`) → ~2 min.

Verify count after both batches.

## Phase 7 — Score (per_item parser, Cohen w vs Korean ref)

Write `scripts/_o_augment_pilot/_score_iter<MM>.py`. Use iter11's `_score_iter11.py` as the template. Key element — the per_item parser:

```python
def parse_per_item(reply: str) -> list[int]:
    chunks = [c.strip() for c in reply.strip().split("\n\n") if c.strip()]
    if len(chunks) != 12:
        raise ValueError(f"expected 12 items, got {len(chunks)}")
    answers = []
    for i, chunk in enumerate(chunks, 1):
        lines = [l.strip() for l in chunk.splitlines() if l.strip()]
        m = re.match(r"^([1-5])\.", lines[-1])
        if not m:
            raise ValueError(f"item {i}: no leading digit: {lines[-1]!r}")
        answers.append(int(m.group(1)))
    return answers
```

The scorer should compute Cohen w vs `KOREAN_HUMAN_REFERENCE` for each trait (O, C, E, A_whole, A_sex, N) and print the result alongside iter11's baseline for comparison. Save `answers.parquet` and `_iter<MM>_result.json` to the run dir.

## Phase 8 — Diagnose paired shift BEFORE proposing next iter

**This is the critical phase.** If your iter's aggregate Cohen w is unexpected (regression or partial-fix), run the per-persona paired-shift diagnostic before designing iter<MM+1>:

```python
i_prev = pd.read_parquet(prev_run / "answers.parquet")[["uuid8", "<trait>_q"]]
i_curr = pd.read_parquet(curr_run / "answers.parquet")[["uuid8", "<trait>_q"]]
paired = i_prev.merge(i_curr, on="uuid8", suffixes=("_prev", "_curr"))
paired["shift"] = paired["<trait>_q_curr"] - paired["<trait>_q_prev"]

for q in sorted(paired["<trait>_q_prev"].unique()):
    sub = paired[paired["<trait>_q_prev"] == q]
    print(f"{q}  n={len(sub)}  mean_shift={sub['shift'].mean():+.2f}")
```

Look for the **regression-to-mean signature**: low-baseline rises, high-baseline falls, monotonic at the extremes. That's RTM, not a real intervention effect. The intervention is leaving persona-level behavior under-specified, and Pass 2 falls back to the middle prior. Going into the next iter without seeing this signal will repeat the iter13→iter14 mechanism failure documented in [[methodology-diagnostic-before-next-iter]].

If RTM is the explanation: the next iter should add an **active anchor** (behavior verb, frequency claim, concrete instance), not another reformulation of the same passive content.

## Failed-attempt history (cautions)

Don't repeat these — they're documented in memory:

| iter | change vs iter11 | mean w | why it failed |
|---|---|---:|---|
| 12 | diversify `[어휘 습관]` syntactically with social-context examples | 0.362 | Each diverse shape reintroduced audience tokens (`친구들과의 자리에서` etc.) → trait spillover |
| 13 | diversify `[어휘 습관]` context-free (intrinsic vocabulary only) | 0.324 | Stative shapes (`끼어 있다`, `있다`, `좋아한다`) leave E behavior under-specified → RTM compresses Q4 → 2% |
| 14 | drop `[어휘 습관]`, add 7th O facet (어휘 다양성) + Pass 2 tags | 0.407 | 7th facet enriched O paragraph → gestalt impression spillover into C (+0.16) and E (+0.35) |

## When to stop iterating

Per [[lesson-llm-respondent-prior-hierarchy]]: stop after ~2 failed attempts with uniform-wording iteration. The iter11 monoculture template is now strongly validated as the local optimum after 3 different families of improvement attempts (diversity-with-context, diversity-without-context, inventory-level) all regressed. Future improvements need to come from a different lever: per-trait Pass 1 prompts, persona pre-filtering, or instrument-level changes (not augmentation reformulations).

## Pointers

- iter11 canonical recipe code: `scripts/_o_augment_pilot/_build_gen_prompts_v12.py`, `_materialize_iter11.py`, `_build_pass2_iter11.py`, `_score_iter11.py`
- Paired-shift diagnostic template: `scripts/_o_augment_pilot/_analyze_iter13_e_shift.py`, `_analyze_iter13_e_shift2.py`
- Locked baseline sample: `runs/big_five_selfimage_n50_pertrait_20260525-172312/persona_sample.parquet`
- Memory: [[finding-iter11-minimal-q11-symmetric-anchor]], [[lessons-iter12-iter13-iter14-diversity-and-inventory-attempts]], [[methodology-diagnostic-before-next-iter]], [[finding-korean-distribution-match-pipeline]], [[methodology-paired-prompt-ladder]]
