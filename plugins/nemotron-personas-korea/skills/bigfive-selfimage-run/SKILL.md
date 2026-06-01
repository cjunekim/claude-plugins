---
name: bigfive-selfimage-run
description: End-to-end runbook for the Korean Big Five selfimage study using `persona-respondent` subagent dispatches (Pass 1 self-image → Pass 2 Likert → score → audit). TRIGGER when the user asks to run a Big Five selfimage experiment at any n, scale a previous run to a larger n, re-run with different demographics/seed, or audit an existing run dir. TRIGGER on phrases like "run bigfive_selfimage at n=300", "let's scale to n=500", "do another Big Five run", "audit run XYZ", "let's do a Big Five study". TRIGGER when starting work in the `nemotron` project on anything Big-Five-related where the existing `nemotron/bigfive_selfimage/` package is the right entry point (not the older `nemotron.bigfive` API-based pipeline). Covers the operational sequence — materialize prompts, dispatch Pass 1 in parallel via file-read + file-write directives (`READ_PERSONA_BATCH` + `SAVE_REPLY_TO`), verify counts, build Pass 2 prompts, dispatch Pass 2, score, audit. The subagent writes its own reply files in parallel, so the dispatcher never retranscribes content — neither in inline replies nor in JSON manifests. Don't try to redo orchestration ad-hoc; this skill exists because the n=100 run revealed several wrong defaults (per-file Writes, sequential dispatch, manifest hand-transcription, missed personas) that this runbook now guards against.
---

# Big Five selfimage — operational runbook

The `nemotron.bigfive_selfimage` pipeline is a two-pass Korean personality study: Pass 1 generates a persona's first-person self-image in Korean; Pass 2 answers the 12-item NPA Likert with that self-image baked in. All dispatch goes through `nemotron-personas-korea:persona-respondent` — no API spend.

This runbook assumes everything exists in the project: the agent, the helpers (`nemotron.bigfive_selfimage`), the smoke materializer (`scripts/bigfive_selfimage_smoke.py`), and the save helper (`scripts/bigfive_selfimage_save_replies.py`). If anything is missing, fall back to the spec at `docs/superpowers/specs/2026-05-24-bigfive-v2-persona-respondent-design.md`.

## Phase 1 — Materialize the run directory

One Bash call. Pass `--n <count>` and `--label <name>`. The label becomes part of the run-dir name (e.g., `runs/big_five_selfimage_n300_<ts>/`).

```bash
PYTHONIOENCODING=utf-8 PYTHONPATH=. .venv/Scripts/python.exe scripts/bigfive_selfimage_smoke.py \
    --n 300 --label n300
```

The script writes:
- `persona_sample.parquet` — the sampled personas
- `_persona_direction.txt`, `_personality_image_prompt.txt`, `_answering_heuristics.txt`, `_questions.txt`, `_anchors.txt` — system-prompt snapshots
- `pass1_prompts/persona_<uuid8>.txt` × N — Pass 1 dispatch prompts ready for file-read
- Empty target dirs: `pass1_selfimages/`, `pass2_prompts/`, `pass2_replies/`
- `manifest.json`

Capture the run dir absolute path. You'll need it for the dispatch prompts (`READ_PERSONA_BATCH <abs_path>`).

## Phase 2 — Dispatch Pass 1

Use **file-read mode** plus the **file-write save directive**. Each Agent dispatch's prompt is two lines:

```
READ_PERSONA_BATCH <abs-path-to>/pass1_prompts/persona_<uuid8>.txt
SAVE_REPLY_TO <abs-path-to>/pass1_selfimages/persona_<uuid8>.txt
```

The first line tells the agent to read its persona prompt from disk (~50 bytes of dispatch instead of ~3 KB of inline persona content). The second line tells the agent to `Write` its reply directly to disk — the reply text bytes never flow back through the dispatcher's output stream, which is the binding constraint for long-reply work. This combination is why Pass 1 dispatches scale: dispatch prompts stay tiny AND tool_result content stays tiny ("OK" per dispatch).

**Parallelism**: issue all N dispatches across as few assistant turns as comfortable. No hard cap ≤24 (measured 2026-05-30) — dispatch is launch-rate-bound (~1.8 s/dispatch emit), so the personas you dispatch in a turn effectively all overlap. The 25-dispatches-per-turn upper bound is a *context-headroom* guide (you need ⌈N/25⌉ turns), NOT a concurrency limit. (Cap model changed 2026-05-30 — see the global `agent-tool-throughput` lesson; re-measure, never quote a cap from memory.)

**Per-dispatch arguments:**
- `subagent_type`: `nemotron-personas-korea:persona-respondent`
- `description`: e.g., `"Pass 1 <uuid8>"` (UI label, short)
- `prompt`: the two-line `READ_PERSONA_BATCH` + `SAVE_REPLY_TO` block above

Wall-clock estimate: no hard cap ≤24, launch-rate-bound → `wall ≈ N·1.8 s + W` (W≈15–20 s/dispatch). For N=100, ~3–4 min; for N=300, ~9–11 min. (Model extrapolated beyond the measured N≤24 — re-measure; the cap model changed 2026-05-30, see the global `agent-tool-throughput` lesson.)

**Don't drop personas.** Before the next phase, verify the dispatch count matches the persona count. A common failure mode is skipping a uuid in the batch construction. Diff `pass1_prompts/` vs your dispatched-uuid list.

## Phase 3 — Verify Pass 1 self-image count

With `SAVE_REPLY_TO` in the dispatch, each agent writes its reply directly to `pass1_selfimages/persona_<uuid8>.txt`. No manifest, no save helper. After all Pass 1 dispatches return, verify the count and sanity-check one or two files:

```bash
ls runs/<ts>/pass1_selfimages/ | wc -l    # should equal N
```

If any files are missing, re-dispatch the corresponding personas (look up uuids by diffing `ls pass1_prompts/` vs `ls pass1_selfimages/`).

Sanity-read 1–2 files to confirm they are clean Korean self-image prose — no leading "OK", no bracketed stage direction, no JSON wrapping. If you see leakage of the dispatcher contract into the file content, the agent's "Write content is the reply only" rule is being violated and the rest of the batch should be inspected before scoring.

## Phase 4 — Build Pass 2 prompts

One Bash call. Reads each Pass 1 selfimage from disk, builds the full Pass 2 prompt, writes to `pass2_prompts/persona_<uuid8>.txt`:

```bash
PYTHONIOENCODING=utf-8 PYTHONPATH=. .venv/Scripts/python.exe -c "
import sys
from pathlib import Path
import pandas as pd
from nemotron.bigfive_selfimage import pass2_prompt

run_dir = Path(sys.argv[1])
sample = pd.read_parquet(run_dir / 'persona_sample.parquet')
selfimg_dir = run_dir / 'pass1_selfimages'
out_dir = run_dir / 'pass2_prompts'

for _, p in sample.iterrows():
    uuid8 = p['uuid'][:8]
    selfimg = (selfimg_dir / f'persona_{uuid8}.txt').read_text(encoding='utf-8')
    (out_dir / f'persona_{uuid8}.txt').write_text(
        pass2_prompt(p, selfimg), encoding='utf-8',
    )
print(f'wrote {len(sample)} Pass 2 prompts to {out_dir}')
" '<run_dir>'
```

## Phase 5 — Dispatch Pass 2

Same shape as Phase 2 — two-line dispatch with `READ_PERSONA_BATCH` + `SAVE_REPLY_TO`, pointing at `pass2_prompts/` and `pass2_replies/`:

```
READ_PERSONA_BATCH <abs-path-to>/pass2_prompts/persona_<uuid8>.txt
SAVE_REPLY_TO <abs-path-to>/pass2_replies/persona_<uuid8>.txt
```

Pass 2 replies are short (12 lines of digits), so the inline-reply path would also be cheap. Using `SAVE_REPLY_TO` here is for consistency with Phase 2 — same dispatch shape, same verification step in Phase 6, fewer special cases to remember. Pass 2 dispatches are faster (~3–5 s each — the reply is just 12 digits). For N=300, ~5–8 min wall.

## Phase 6 — Verify Pass 2 reply count

Same as Phase 3: `ls runs/<ts>/pass2_replies/ | wc -l` should equal N. Sanity-read 1–2 files to confirm they are 12 lines, each a single digit 1–5 — no leading "OK", no Korean text, no commentary.

## Phase 7 — Parse, score, and write summary

One Bash call. Reuses `nemotron.bigfive.analysis.summary_report` and `big_five.big_five` for the canonical scoring path:

```bash
PYTHONIOENCODING=utf-8 PYTHONPATH=. .venv/Scripts/python.exe -c "
import json, sys
from pathlib import Path
import pandas as pd

from big_five import big_five
from nemotron.bigfive import KOREAN_HUMAN_REFERENCE
from nemotron.bigfive.analysis import summary_report
from nemotron.bigfive.instrument import QUESTIONS
from nemotron.bigfive.persona import sex_key
from nemotron.bigfive_selfimage import parse_likert

run_dir = Path(sys.argv[1])
sample = pd.read_parquet(run_dir / 'persona_sample.parquet')
replies_dir = run_dir / 'pass2_replies'

scored = []
failures = []
for _, p in sample.iterrows():
    uuid8 = p['uuid'][:8]
    reply = (replies_dir / f'persona_{uuid8}.txt').read_text(encoding='utf-8')
    try:
        answers = parse_likert(reply)
    except ValueError as e:
        failures.append({'uuid': p['uuid'], 'error': str(e), 'reply': reply})
        continue
    sex = sex_key(p['sex'])
    bf = big_five(answers, sex=sex)
    scored.append({
        'uuid': p['uuid'], 'sex': p['sex'], 'age': int(p['age']),
        'occupation': p.get('occupation'),
        'augmentation': '(none — selfimage path)',
        'answers': answers,
        'O_raw': bf.O.raw, 'O_q': bf.O.category,
        'C_raw': bf.C.raw, 'C_q': bf.C.category,
        'E_raw': bf.E.raw, 'E_q': bf.E.category,
        'A_raw': bf.A.raw, 'A_q': bf.A.category,
        'A_whole_q': bf.A_whole.category,
        'N_raw': bf.N.raw, 'N_q': bf.N.category,
    })

if failures:
    (run_dir / 'failures.json').write_text(
        json.dumps(failures, ensure_ascii=False, indent=2), encoding='utf-8',
    )

pd.DataFrame(scored).to_parquet(run_dir / 'answers.parquet')
(run_dir / 'answers.json').write_text(
    json.dumps(scored, ensure_ascii=False, indent=2), encoding='utf-8',
)

title = f'Big Five selfimage n={len(scored)} via persona-respondent'
summary = summary_report(scored, title=title)
ans_lists = [s['answers'] for s in scored]
all_answers = pd.Series([x for row in ans_lists for x in row])
anchor_counts = all_answers.value_counts().sort_index().to_dict()
extra = (
    f'\nq3: {QUESTIONS[2]}\nq7: {QUESTIONS[6]}\n'
    f'Korean human reference (n=123): {KOREAN_HUMAN_REFERENCE}\n'
    f'parse failures: {len(failures)}/{len(sample)}\n'
    f'anchor distribution across {len(all_answers)} answers: {anchor_counts}\n'
)
(run_dir / 'summary.txt').write_text(summary + extra, encoding='utf-8')
print(summary + extra)
" '<run_dir>'
```

If `failures.json` exists with non-empty content, re-dispatch the failed personas (Pass 2 only) and re-run scoring.

## Phase 8 — Audit against acceptance criteria

Walk the five criteria. The first four are mechanical; the fifth is a manual read.

| # | Criterion | Pass bar | How to check |
|---|---|---|---|
| 1 | Format compliance | ≥(N-1)/N parsed on first try | `cat failures.json 2>/dev/null \| jq length` |
| 2 | Language compliance | ≥(N-1)/N Pass 1 selfimages are Korean + first-person | Sample 5–10, read with the Read tool |
| 3 | In-character voice | ≥2/3 sampled selfimages clearly match their persona row | Read 3 selfimages alongside `persona_sample.parquet` rows |
| 4 | Distribution shape | All 5 anchors used; not all bunched on 3 | The summary.txt's `anchor distribution` line |
| 5 | No stage-direction leakage | 0 files contain `[`, `stage direction`, `as a persona` | `grep -lE '\[\|stage direction\|as a persona' pass*_*/*.txt` |

Append the audit verdict to `summary.txt`:

```
## Acceptance audit
- (1) Format compliance: N/N parsed cleanly. PASS.
- (2) Language compliance: N/N Korean + first-person (visual check). PASS.
- (3) In-character voice: 3/3 sampled. PASS.
- (4) Distribution shape: all 5 anchors used (counts X/Y/Z/W/V). PASS.
- (5) Stage-direction leakage: 0 files. PASS.

Overall: PASS (5/5).
```

## Interpretation reminders

- **N (Neuroticism) typically matches Korean human ref closely** (Cohen's w ≈ 0.1 in the n=100 run). The Answering Heuristics + Pass-1-self-image-priming reproduces the human N distribution within sampling noise.
- **C (Conscientiousness) skews systematically high** — Cohen's w around 1.4–1.5 in n=100 and n=300. This is real, persistent across instrument versions (matches v6c finding). Don't treat it as a bug.
- **O and E skew low** — Nemotron personas are more conservative and introverted than the Korean human reference. Mid-magnitude effect (w ≈ 0.6).
- **Bimodal anchor distribution** (peaks at 2 and 4, valley at 3) is the expected shape — that's the Answering Heuristics counteracting middle-bunching. A Gaussian peak on 3 would mean the heuristics failed.

## Common failure modes (learned the hard way)

- **Hand-transcribing replies into a manifest**: the original n=20 / n=100 runs paid ~10–20 min just retyping Korean self-images into a JSON manifest. The fix is `SAVE_REPLY_TO` in the dispatch (Phase 2/5 above) — the subagent writes its own file, the dispatcher never sees the content. Don't fall back to manifest-based saves unless the agent contract genuinely lacks Write.
- **Dropping a persona in the dispatch list**: easy to miss one between batches. After Phase 2/5, `ls pass1_prompts/ | wc -l` vs `ls pass1_selfimages/ | wc -l` — the mismatch is the dropped uuids.
- **Inline prompts at scale**: don't. File-read mode (`READ_PERSONA_BATCH`) is dramatically cheaper at N ≥ 25 because main-session emit cost on 3 KB Korean prompts is ~29 s/dispatch (see `agent-tool-throughput` skill).
- **Forgetting `PYTHONIOENCODING=utf-8` + `PYTHONPATH=.`**: the project requires both for any Python invocation. Korean text + sibling-package imports.
- **`SAVE_REPLY_TO` content has "OK" or stage direction in it**: the agent's contract says the file content is the reply only and the in-conversation output is `OK`. If a file contains `OK\n저는…` or `[…]` text, the agent confused the two channels. Re-dispatch the affected uuid before scoring; the file is contaminated.
