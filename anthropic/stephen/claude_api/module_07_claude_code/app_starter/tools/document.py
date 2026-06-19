from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pathlib import Path
from pydantic import Field


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    path: str = Field(description="Absolute or relative path to a PDF or DOCX file"),
) -> str:
    """Convert a PDF or DOCX file to markdown text.

    Reads the file at the given path and returns its contents as markdown.

    When to use:
    - When you have a local file path to a document and need its text content
    - When you want to extract readable text from a PDF or DOCX file

    Examples:
    >>> document_path_to_markdown("/docs/report.pdf")
    "# Report\\n\\nSome content..."
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No such file: '{path}'")
    return binary_document_to_markdown(file_path.read_bytes(), file_path.suffix.lstrip("."))
