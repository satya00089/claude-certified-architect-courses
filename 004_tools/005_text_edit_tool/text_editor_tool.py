"""
Code Refactoring Assistant — Streamlit Demo
============================================
Use case: point the assistant at any .py file in this folder, describe a refactoring
task in plain English, and watch the model use the text editor tool to read and patch
the file autonomously.

Examples of tasks you can try:
  - "Add a docstring to every function that is missing one"
  - "Add type hints to all function parameters and return values"
  - "Rename the variable 'result' to 'response' everywhere"
  - "Extract the inline logic inside main() into a helper function called _run"
  - "Add error handling around the client.messages.create call"
"""

import os
import json
import shutil
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()


# ── Text Editor Tool implementation ──────────────────────────────────────────

class TextEditorTool:
    """A simple text editor tool with a few basic commands (view, str_replace, create, insert, undo_edit)."""
    def __init__(self, base_dir: str = ""):
        """Initialize the text editor with a base directory for file operations and a backup directory for undo."""
        self.base_dir = os.path.normpath(base_dir or os.getcwd())
        self.backup_dir = os.path.join(self.base_dir, ".backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def _validate_path(self, file_path: str) -> str:
        """Validate the file path to ensure it is within the allowed directory."""
        abs_path = os.path.normpath(os.path.join(self.base_dir, file_path))
        if not abs_path.startswith(self.base_dir):
            raise ValueError(f"Access denied: '{file_path}' is outside the allowed directory")
        return abs_path

    def _backup(self, abs_path: str):
        """Create a backup of the file before making changes."""
        if os.path.exists(abs_path):
            name = os.path.basename(abs_path)
            dest = os.path.join(self.backup_dir, f"{name}.{os.path.getmtime(abs_path):.0f}.bak")
            shutil.copy2(abs_path, dest)
            return dest
        return ""

    def view(self, path: str, view_range=None) -> str:
        """View the contents of a file or directory. Optionally, specify a range of lines to view."""
        abs_path = self._validate_path(path)
        if os.path.isdir(abs_path):
            return "\n".join(os.listdir(abs_path))
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")
        if view_range:
            start, end = view_range
            end = len(lines) if end == -1 else end
            lines = lines[start - 1:end]
            return "\n".join(f"{i}: {l}" for i, l in enumerate(lines, start))
        return "\n".join(f"{i}: {l}" for i, l in enumerate(lines, 1))

    def str_replace(self, path: str, old_str: str, new_str: str) -> str:
        """Replace the first occurrence of old_str with new_str in the specified file. Requires enough context for uniqueness."""
        abs_path = self._validate_path(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        count = content.count(old_str)
        if count == 0:
            raise ValueError("No match found for replacement.")
        if count > 1:
            raise ValueError(f"Found {count} matches — provide more context to make it unique.")
        self._backup(abs_path)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content.replace(old_str, new_str, 1))
        return "Successfully replaced text at exactly one location."

    def create(self, path: str, file_text: str) -> str:
        """Create a new file with the specified content. Raises an error if the file already exists."""
        abs_path = self._validate_path(path)
        if os.path.exists(abs_path):
            raise FileExistsError("File already exists. Use str_replace to modify it.")
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(file_text)
        return f"Successfully created {path}"

    def insert(self, path: str, insert_line: int, new_str: str) -> str:
        """Insert a new line of text after the specified line number in the file."""
        abs_path = self._validate_path(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {path}")
        self._backup(abs_path)
        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if insert_line == 0:
            lines.insert(0, new_str + "\n")
        elif 0 < insert_line <= len(lines):
            lines.insert(insert_line, new_str + "\n")
        else:
            raise IndexError(f"Line {insert_line} out of range (file has {len(lines)} lines).")
        with open(abs_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return f"Successfully inserted text after line {insert_line}"

    def undo_edit(self, path: str) -> str:
        """Restore the most recent backup of the specified file."""
        abs_path = self._validate_path(path)
        name = os.path.basename(abs_path)
        backups = sorted(
            [f for f in os.listdir(self.backup_dir) if f.startswith(name + ".") and f.endswith(".bak")],
            reverse=True,
        )
        if not backups:
            raise FileNotFoundError(f"No backup found for {path}")
        shutil.copy2(os.path.join(self.backup_dir, backups[0]), abs_path)
        return f"Successfully restored {path} from backup."


def run_tool(editor: TextEditorTool, tool_name: str, tool_input: dict) -> str:
    """Executes a specified tool with the given input."""
    if tool_name != "str_replace_based_edit_tool":
        raise ValueError(f"Unknown tool: {tool_name}")
    cmd = tool_input.get("command")
    if cmd == "view":
        return editor.view(tool_input["path"], tool_input.get("view_range"))
    elif cmd == "str_replace":
        return editor.str_replace(tool_input["path"], tool_input["old_str"], tool_input["new_str"])
    elif cmd == "create":
        return editor.create(tool_input["path"], tool_input["file_text"])
    elif cmd == "insert":
        return editor.insert(tool_input["path"], tool_input["insert_line"], tool_input["new_str"])
    elif cmd == "undo_edit":
        return editor.undo_edit(tool_input["path"])
    else:
        raise ValueError(f"Unknown command: {cmd}")


TEXT_EDITOR_SCHEMA = {
    "type": "text_editor_20250728",
    "name": "str_replace_based_edit_tool",
}

SYSTEM_PROMPT = """\
You are a code refactoring assistant. You have access to a text editor tool that lets you
read and modify files. When the user asks you to refactor code:
1. Use the view command to read the file first.
2. Apply each change with str_replace (one per call, with enough context for uniqueness).
3. After all edits, summarise what you changed and why.
Keep changes minimal and targeted. Do not rewrite the file wholesale."""


# ── Helpers ───────────────────────────────────────────────────────────────────

def list_py_files(base_dir: str) -> list[str]:
    """List all .py files in the specified directory."""
    return [f for f in os.listdir(base_dir) if f.endswith(".py")]


def read_file_safe(path: str) -> str:
    """Read the contents of a file safely, returning an error message if it fails."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"(Could not read file: {e})"


def run_refactor(client, model: str, task: str, file_name: str, editor: TextEditorTool, log_fn):
    """Run the multi-turn tool loop and stream steps into log_fn()."""
    messages = [{"role": "user", "content": f"Refactor the file `{file_name}`: {task}"}]

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=[TEXT_EDITOR_SCHEMA],
        )

        # Collect assistant content blocks as plain dicts for re-insertion
        content_blocks = []
        for block in response.content:
            if block.type == "text":
                content_blocks.append({"type": "text", "text": block.text})
                if block.text.strip():
                    log_fn("assistant", block.text)
            elif block.type == "tool_use":
                content_blocks.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
                log_fn("tool_call", f"**{block.name}** › `{block.input.get('command')}` on `{block.input.get('path')}`")

        messages.append({"role": "assistant", "content": content_blocks})

        if response.stop_reason != "tool_use":
            break

        # Execute tools and gather results
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                output = run_tool(editor, block.name, block.input)
                log_fn("tool_result", f"✓ {output[:200]}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output),
                    "is_error": False,
                })
            except Exception as e:
                log_fn("tool_error", f"✗ {e}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Error: {e}",
                    "is_error": True,
                })

        messages.append({"role": "user", "content": tool_results})

    return messages


# ── Streamlit UI ──────────────────────────────────────────────────────────────

def main():
    """Streamlit UI for the Code Refactoring Assistant demo."""
    st.set_page_config(page_title="Code Refactoring Assistant", layout="wide")
    st.title("Code Refactoring Assistant")
    st.markdown(
        "Describe a refactoring task in plain English — the model reads and patches your file "
        "using the **text editor tool** (`view` + `str_replace` + `undo_edit`)."
    )

    model = st.sidebar.text_input("Model", value="claude-sonnet-4-5")
    base_dir = st.sidebar.text_input(
        "Working directory",
        value=os.path.dirname(os.path.abspath(__file__)),
    )

    # File picker
    py_files = list_py_files(base_dir) if os.path.isdir(base_dir) else []
    if not py_files:
        st.warning(f"No .py files found in `{base_dir}`")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        selected_file = st.selectbox("Select a Python file to refactor", py_files)
        file_path = os.path.join(base_dir, selected_file)

        st.markdown("**Current file contents:**")
        st.code(read_file_safe(file_path), language="python")

        # Undo button
        editor_for_undo = TextEditorTool(base_dir)
        if st.button("↩ Undo last edit"):
            try:
                msg = editor_for_undo.undo_edit(selected_file)
                st.success(msg)
                st.rerun()
            except Exception as e:
                st.error(str(e))

    with col2:
        st.markdown("**Refactoring task**")
        task = st.text_area(
            "Describe what you want changed",
            height=120,
            placeholder=(
                "Examples:\n"
                "• Add a docstring to every function that is missing one\n"
                "• Add type hints to all function parameters and return values\n"
                "• Add error handling around the client.messages.create call\n"
                "• Rename the variable 'result' to 'response' everywhere"
            ),
        )

        run_btn = st.button("Run refactor", type="primary", disabled=not task.strip())

        if run_btn and task.strip():
            log_container = st.container()
            log_entries = []

            def log_fn(kind: str, text: str):
                log_entries.append((kind, text))

            with st.spinner("Running…"):
                client = Anthropic()
                editor = TextEditorTool(base_dir)
                try:
                    run_refactor(client, model, task, selected_file, editor, log_fn)
                except Exception as e:
                    st.error(f"Error: {e}")

            with log_container:
                st.markdown("**Step-by-step trace:**")
                for kind, text in log_entries:
                    if kind == "assistant":
                        st.info(text)
                    elif kind == "tool_call":
                        st.markdown(f"🔧 {text}")
                    elif kind == "tool_result":
                        st.success(text)
                    elif kind == "tool_error":
                        st.error(text)

            st.markdown("**Updated file:**")
            st.code(read_file_safe(file_path), language="python")


if __name__ == "__main__":
    main()
