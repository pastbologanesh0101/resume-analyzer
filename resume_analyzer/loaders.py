"""
Input loaders: read plain-text resumes/job descriptions from .txt files,
with optional .docx support via python-docx if it is installed.
"""

from __future__ import annotations

from pathlib import Path


def load_text(path: str) -> str:
    """
    Load a resume or job description as plain text.

    .txt files are read directly (required, no extra dependency).
    .docx files are supported if python-docx is installed (optional bonus
    format support); a clear error is raised otherwise.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = p.suffix.lower()
    if suffix == ".docx":
        try:
            import docx  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "Reading .docx files requires the optional 'python-docx' "
                "dependency. Install it with: pip install python-docx"
            ) from exc
        document = docx.Document(str(p))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    # Default: treat as plain text (.txt and anything else).
    return p.read_text(encoding="utf-8", errors="ignore")
