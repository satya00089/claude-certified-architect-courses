# Text Editor Tool

This folder demonstrates how to give a model a **text editor tool** — a structured set of
file-system operations the model can call to read, create, and modify files on your behalf.

## What it is

The `str_replace_based_edit_tool` (Anthropic built-in type `text_editor_20250728`) exposes
five commands to the model:

| Command | Purpose |
|---------|---------|
| `view` | Read a file (optionally a line range) or list a directory |
| `str_replace` | Replace exactly one occurrence of a string in a file |
| `create` | Create a new file with specified content |
| `insert` | Insert a line at a specified position |
| `undo_edit` | Restore the previous version of a file from backup |

## Why you need it

Without a file tool, the model can only *suggest* code changes in chat. With this tool the
model can:

- **Read** actual file content instead of relying on what you paste in.
- **Apply targeted edits** — no whole-file rewrites, just precise `str_replace` patches.
- **Iterate autonomously** — view → edit → verify → continue without a human in the loop.
- **Roll back safely** — every write creates an automatic backup; `undo_edit` restores it.

This unlocks agentic use cases like:

- Automated code refactoring (rename, add type hints, extract functions)
- Documentation generation (add docstrings to every function)
- Safe linting fixes applied directly to source files
- Multi-step code review that actually patches the issues it finds

## How it works (flow)

```
User prompt
    │
    ▼
chat(messages, tools=[text_editor_schema])
    │
    ├─ stop_reason == "tool_use"  ──►  run_tool(name, input)
    │                                        │
    │        TextEditorTool executes         │
    │        (view / str_replace / ...)      │
    │                                        ▼
    │                               tool_result injected
    │                               back into messages
    │                                        │
    └─ stop_reason != "tool_use"  ◄──────────┘
           │
           ▼
    Final assistant reply
```

## Files

| File | Description |
|------|-------------|
| `text_editor_tool.ipynb` | Notebook with examples of view, edit, and undo |
| `main.py` | Small target file used by the notebook examples |
| `streamlit_app.py` | Interactive **Code Refactoring Assistant** demo |
| `requirements.txt` | Python dependencies |

## Run the Streamlit demo

```bash
pip install -r 004_tools/005_text_edit_tool/requirements.txt
# add ANTHROPIC_API_KEY to a .env file or set it in the sidebar
streamlit run 004_tools/005_text_edit_tool/streamlit_app.py
```

The demo lets you pick any `.py` file, describe a refactoring task, and watch the model read
and patch the file using the text editor tool. An **Undo last edit** button restores the file
from the automatic backup created before every write.

## Implementation notes

- `_validate_path` enforces that all file paths stay within `base_dir` — prevents path traversal.
- Every destructive operation (`str_replace`, `insert`, `create`) calls `_backup_file` first.
- `str_replace` requires **exactly one** match — use enough surrounding context to be unique.
- `max_tokens` should be at least `4096`; tool call roundtrips produce verbose content.
