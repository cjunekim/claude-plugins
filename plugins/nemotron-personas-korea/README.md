# nemotron-personas-korea

Claude Code plugin: Korean LLM-as-respondent toolkit built around the
[`nvidia/Nemotron-Personas-Korea`](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
HuggingFace dataset (1M synthetic Korean adults, calibrated to KOSIS / Supreme
Court / NHIS marginals, CC BY 4.0).

## What's inside

### Skills (auto-triggered references & runbooks)

| Name | Purpose |
|---|---|
| `nemotron-personas-korea:dataset` | Reference: schema quirks, field-semantics gotchas, survey-instrument design lessons (Likert anchor wording, debias, distribution validation); bundled inspection + persona-loader scripts. |
| `nemotron-personas-korea:dispatch-strategy` | Caller-side dispatch strategy for `persona-respondent` — mode (one-per / inline batch / file-read batch), concurrency / fan-out sizing, and the announce-before-launch format. |
| `nemotron-personas-korea:synthetic-population-validity` | Domain-agnostic methodology + statistics for comparing synthetic / LLM survey-response distributions against a real human reference (the validity stack, Cohen's w, dispersion / ICC, correlation distortion, the perfect-respondent sampling floor, holdout, reliability, a diagnosis playbook). Generalizes beyond Big Five — use it for any synth-vs-real comparison. |
| `nemotron-personas-korea:bigfive-selfimage-run` | End-to-end runbook for the Korean Big Five self-image study via `persona-respondent` dispatches (Pass 1 self-image → Pass 2 Likert → score → audit). |
| `nemotron-personas-korea:bigfive-selfimage-iter-campaign` | Augmentation-iteration variant: paired prompt-engineering iters on a locked baseline sample, compared against the campaign-best recipe. |
| `nemotron-personas-korea:bulk-reply-save` | Persist N batched-dispatch reply files with 2 tool calls (a JSON manifest + a Python helper) instead of N individual `Write`s. |

### Sub-agent & command

| Surface | Namespaced name | Purpose |
|---|---|---|
| Sub-agent | `nemotron-personas-korea:persona-respondent` | Role-plays a Korean adult survey respondent. One persona per dispatch by default; also supports inline batch, file-read batch (`READ_PERSONA_BATCH <path>`), multi-item dispatch, bracketed `[...]` stage directions (out-of-character meta-instructions), and file-write save mode (`SAVE_REPLY_TO <path>`) for long replies. Runs on Sonnet; tools `[Read, Write]`. |
| Slash command | `/nemotron-personas-korea:persona-interviewee` | Enters in-character qualitative-interview mode for a specific persona (by `uuid` or demographic filter), with optional `--save` for turn-by-turn transcript logging. |

## Required environment variables

- **`HF_HOME`** — HuggingFace's standard. Where `load_dataset` caches the
  ~5.76 GB dataset materialization. Set this BEFORE any load to keep the
  cache off the system drive (Windows default lands at
  `%USERPROFILE%\.cache\huggingface`).
- **`NEMOTRON_INTERVIEWS_DIR`** — used by `/persona-interviewee --save` for
  transcript output. Defaults to `./nemotron-interviews/` in the current
  working directory if unset.

The plugin assumes the dataset is already cached at `$HF_HOME`. First-time
loaders will trigger a download; the bundled inspection script
(`skills/dataset/scripts/inspect_dataset.py`) is the recommended place to
run that first download since it produces a SHA-pinned snapshot.

## Install

Distributed via the `cjunekim-plugins` marketplace
([`cjunekim/claude-plugins`](https://github.com/cjunekim/claude-plugins)) — add the
marketplace and install the plugin through Claude Code's `/plugin` interface. For
local development against a working copy, point Claude Code at the plugin directory
with `--plugin-dir` and reload via `/plugin` after edits.

## Layout

```
nemotron-personas-korea/
├── .claude-plugin/plugin.json              # manifest
├── README.md                               # this file
├── agents/persona-respondent.md            # the survey-respondent sub-agent
├── commands/persona-interviewee.md         # /persona-interviewee slash command
└── skills/
    ├── dataset/                            # schema + instrument-design reference (+ inspect / load scripts)
    ├── dispatch-strategy/                  # caller-side dispatch mode + concurrency sizing
    ├── synthetic-population-validity/      # synth-vs-real validation methodology + stats scripts + literature
    ├── bigfive-selfimage-run/              # Big Five self-image study runbook
    ├── bigfive-selfimage-iter-campaign/    # augmentation-iteration variant
    └── bulk-reply-save/                    # batched-dispatch reply-persistence pattern
```
