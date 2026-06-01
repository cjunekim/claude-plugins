# cjunekim-plugins

Personal Claude Code marketplace by [@cjunekim](https://github.com/cjunekim).

## Plugins

| Plugin | Purpose |
|---|---|
| [`nemotron-personas-korea`](./plugins/nemotron-personas-korea/) | Korean LLM-as-respondent toolkit built around the [`nvidia/Nemotron-Personas-Korea`](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) HuggingFace dataset. Bundles six skills (dataset reference, dispatch strategy, the domain-agnostic synthetic-population-validity methodology, two Big Five self-image runbooks, and a bulk-reply-save pattern), a persona-respondent sub-agent, and a `/persona-interviewee` slash command for in-character qualitative interviews. |

## Install

In your Claude Code session:

```
/plugin marketplace add cjunekim/claude-plugins
/plugin install nemotron-personas-korea@cjunekim-plugins
/reload-plugins
```

After this, the plugin's namespaced surfaces become available:
- skills (auto-trigger): `nemotron-personas-korea:dataset`, `:dispatch-strategy`, `:synthetic-population-validity`, `:bigfive-selfimage-run`, `:bigfive-selfimage-iter-campaign`, `:bulk-reply-save`
- agent: `nemotron-personas-korea:persona-respondent`
- command: `/nemotron-personas-korea:persona-interviewee`

See each plugin's own README for plugin-specific environment variables and usage notes.

## Visibility

This repository is currently **private**. Collaborators need read access to the repo for `/plugin marketplace add cjunekim/claude-plugins` to succeed (CC delegates auth to the local `gh` CLI).
