# nemotron-personas-korea

Claude Code plugin: Korean LLM-as-respondent toolkit built around the
[`nvidia/Nemotron-Personas-Korea`](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
HuggingFace dataset (1M synthetic Korean adults, calibrated to KOSIS / Supreme
Court / NHIS marginals, CC BY 4.0).

## What's inside

| Surface | Namespaced name | Purpose |
|---|---|---|
| Skill | `nemotron-personas-korea:dataset` | Auto-trigger reference: schema quirks, field-semantics gotchas, survey-instrument design lessons (Likert anchor wording, debias, distribution validation), bundled inspection + persona-loader scripts. |
| Sub-agent | `nemotron-personas-korea:persona-respondent` | Role-plays a Korean adult for closed-form survey calls (Y/N, Likert, multi-choice, numeric, free-text). Pinned to Sonnet 4.6. |
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

## Install (local-development)

```powershell
claude --plugin-dir C:\Users\user\.claude\plugins\nemotron-personas-korea
```

Use `/reload-plugins` to pick up edits without restarting.

## Layout

```
nemotron-personas-korea/
├── .claude-plugin/plugin.json    # manifest
├── README.md                     # this file
├── agents/persona-respondent.md
├── commands/persona-interviewee.md
└── skills/dataset/
    ├── SKILL.md                  # the auto-trigger reference
    ├── scripts/
    │   ├── inspect_dataset.py    # one-shot SHA + schema dump (~5 min wall-clock once cached)
    │   └── load_persona.py       # standalone --uuid / --filter loader (used by the agent + command)
    └── references/inspection-snapshot.md
