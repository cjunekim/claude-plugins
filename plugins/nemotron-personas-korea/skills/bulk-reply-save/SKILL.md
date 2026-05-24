---
name: bulk-reply-save
description: Persist N persona-respondent reply files (or any N similar text files from one turn) using 2 tool calls — JSON manifest + Bash + Python helper — instead of N individual `Write` tool calls. TRIGGER any time you are about to emit ≥3 `Write` tool_use blocks for similar files (same target directory, parallel naming scheme) in one assistant response. TRIGGER when finishing a batched Agent-tool dispatch (`persona-respondent`, `persona-respondent-v2`, or any inline-batch fanout) and about to save Pass 1 self-images, Pass 2 Likert replies, augmentation outputs, or any other batched-dispatch artifacts. TRIGGER when persisting N agent outputs after a parallel `READ_PERSONA_BATCH` fan-out, or any time the user says "save the replies" / "write all of these" / "persist these to disk" after a batched dispatch. Per-file `Write` calls at N≥3 carry per-call harness overhead and may serialize at the framework layer — the bulk pattern writes N files inside a single Python process at OS speed (sub-millisecond per file).
---

# Bulk reply save

When a turn ends with N similar files to persist (e.g., 25 persona-respondent reply files into one directory), do **not** emit N `Write` tool_use blocks. The faster pattern is **one JSON manifest + one Bash invocation of a Python helper**.

## When the subagent-Write pattern is even better

If the subagent has `Write` in its tools list (e.g., `persona-respondent-v2` from v0.1.6 onward), prefer the `SAVE_REPLY_TO <abs-path>` directive in the dispatch prompt over this skill's manifest pattern. Each subagent writes its own reply file in parallel inside its own context, so the heavy reply content never flows through the dispatcher's output stream at all.

The manifest pattern in this skill still requires the dispatcher to retranscribe N reply texts as output tokens into the JSON literal. For long replies (e.g., 1 KB Korean self-images), that is the wall-clock bottleneck — not the per-`Write` tool overhead. `SAVE_REPLY_TO` eliminates the retranscription entirely.

**This skill remains the right choice when**:
- The subagent doesn't have `Write` (lighter agent contracts).
- You're persisting N files produced by your own logic, not by subagents (e.g., post-processing transforms applied per-key).
- The dispatch returns one batched response with multiple items that you must fan back out per-key.
- The reply content is short (≤30 chars per item) — the retranscription cost is trivial and the manifest is a useful audit artifact.

## Why per-file Writes are slow at scale

Even when N `Write` tool calls are issued in parallel within one assistant response, each is a separate tool-call invocation with framework overhead. The wall-clock pattern is closer to serialized than truly concurrent. For N=25 selfimage files, this can add ~10s of overhead that contributes nothing to the actual file I/O (which would take <100ms total in a tight Python loop).

The bulk pattern collapses that to:
- 1 `Write` tool call (the JSON manifest, ~5–20 KB)
- 1 `Bash` tool call (Python loop writing N files at OS speed)

## The pattern

### Step 1: Construct a JSON manifest

Build a JSON object mapping a stable key (usually `uuid8` for persona-respondent work) to the reply content:

```json
{
  "077756dd": "저는 기본적으로 사람을 좋아하고…",
  "09e26797": "저는 논리적으로 생각하는 편이고…",
  ...
}
```

### Step 2: One `Write` tool call

Write the manifest to disk alongside the run directory:

```
Write({
  file_path: "G:/temp/nemotron/runs/<ts>/_save_manifest.json",
  content: <json text, UTF-8, ensure_ascii=false>
})
```

### Step 3: One `Bash` tool call to a save helper

For the `nemotron` project, use `scripts/bigfive_selfimage_save_replies.py`:

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/bigfive_selfimage_save_replies.py \
    <target_dir> <manifest.json>
```

The helper:
1. Loads the JSON.
2. Iterates `{key: content}`.
3. Writes each as `<target_dir>/persona_<key>.txt`.

Total: 2 tool calls vs N. For N=100, that's a ~50× reduction in tool-call overhead.

## When NOT to use this

- **N < 3**: per-file `Write` calls are fine — no point setting up the manifest.
- **Files have heterogeneous content shapes or different target dirs**: the manifest assumes uniform `<target>/persona_<key>.txt` naming. Heterogeneous → per-file Writes are clearer.
- **Per-file processing logic is needed before write** (e.g., reformat each reply differently): bulk pattern doesn't help. Use Python to process + write in the same Bash call.

## Example: 25 Pass 1 self-image saves

**Anti-pattern (slow):**
```
Write({file_path: "…/pass1_selfimages/persona_aaa.txt", content: "저는 …"})
Write({file_path: "…/pass1_selfimages/persona_bbb.txt", content: "저는 …"})
… × 25 …
```

**Pattern (fast):**
```
Write({
  file_path: "runs/<ts>/_save_manifest.json",
  content: '{"aaa": "저는 …", "bbb": "저는 …", …}'
})
Bash({
  command: "python scripts/bigfive_selfimage_save_replies.py runs/<ts>/pass1_selfimages runs/<ts>/_save_manifest.json"
})
```

After the Bash call confirms the count, delete the manifest if you don't want it as an audit artifact:

```bash
rm runs/<ts>/_save_manifest.json
```

## Variants for new projects

If working in a project that doesn't have `bigfive_selfimage_save_replies.py`, the helper is ~15 lines — copy this template to `scripts/save_replies_batch.py` once per project:

```python
"""Read a JSON manifest of {key: content}, write each as <target>/persona_<key>.txt."""
from __future__ import annotations
import json, sys
from pathlib import Path


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    target = Path(argv[1])
    target.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    for key, content in manifest.items():
        (target / f"persona_{key}.txt").write_text(content, encoding="utf-8")
    print(f"wrote {len(manifest)} files to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

Adapt the filename pattern (`persona_<key>.txt`) if your project uses a different scheme.

## Bonus: Pass 2 Likert replies

The same pattern works for Pass 2 saves. Manifest entries are 12-digit strings:

```json
{
  "077756dd": "1\n4\n2\n5\n1\n1\n2\n4\n1\n2\n4\n3",
  "09e26797": "5\n4\n3\n2\n3\n4\n2\n2\n4\n3\n2\n5",
  …
}
```

Target dir: `pass2_replies/`. Helper script doesn't care what's in the content — it just writes.
