from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text(file_path: str) -> tuple[str, int | None]:
    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf(path)

    if extension == ".docx":
        return extract_docx(path)

    if extension == ".txt":
        return extract_txt(path)

    raise ValueError("UNSUPPORTED_FILE_TYPE")


def extract_pdf(path: Path) -> tuple[str, int]:
    reader = PdfReader(path)

    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages), len(reader.pages)


def extract_docx(path: Path) -> tuple[str, None]:
    document = DocxDocument(path)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )

    return text, None


def extract_txt(path: Path) -> tuple[str, None]:
    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    return text, None