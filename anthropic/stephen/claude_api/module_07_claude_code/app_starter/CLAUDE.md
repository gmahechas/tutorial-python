# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (uv auto-detects .venv — no activation needed)
uv pip install -e .

# Start the MCP server
uv run main.py

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_docx
```

## Architecture

`main.py` creates a `FastMCP` server instance and registers tool functions with `mcp.tool()(fn)`. Tools are plain Python functions defined in `tools/` and imported into `main.py` for registration. The `tools/` module is separate from the server so functions can be tested independently.

`tools/document.py` — conversion utilities (e.g. binary document → markdown via `markitdown`)  
`tools/math.py` — example registered MCP tool (`add`)

Test fixtures (`.docx`, `.pdf`) live in `tests/fixtures/`.

## Defining MCP Tools

Tools are ordinary Python functions registered with the server. Follow this pattern:

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does"),
) -> ReturnType:
    """One-line summary.

    Detailed explanation of what the tool does.

    When to use:
    - Specific scenario A
    - Specific scenario B

    Examples:
    >>> my_tool("foo", 42)
    "result"
    """
    # implementation
```

Register in `main.py`:

```python
from tools.my_module import my_tool
mcp.tool()(my_tool)
```

Key rules:
- Always apply appropriate type annotations to all function arguments and return types
- Use `Field(description=...)` on every parameter — this is what the AI sees when deciding how to call the tool
- Docstring structure: one-line summary → detailed explanation → "When to use" bullets → `Examples` block
- Utility/helper functions go in `tools/` but only registered tool functions need `Field` annotations
