"""
File Utilities - File validation, text extraction from PDF/DOCX
"""
import os
from pathlib import Path
from typing import Optional

# PDF extraction
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# DOCX extraction
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file(file) -> tuple[bool, str]:
    """
    Validate uploaded file.
    Returns (is_valid, error_message).
    """
    if not file or not file.filename:
        return False, "Không có file được tải lên"

    if not allowed_file(file.filename):
        return False, "Chỉ chấp nhận file PDF hoặc DOCX"

    # Check file size (seek to end, then back)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > MAX_FILE_SIZE:
        return False, f"File quá lớn. Kích thước tối đa: {MAX_FILE_SIZE // (1024*1024)} MB"

    if size == 0:
        return False, "File rỗng"

    return True, ""


def extract_text_from_file(filepath: str) -> str:
    """
    Extract text content from PDF or DOCX file.
    Returns extracted text as string.
    """
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_from_pdf(filepath)
    elif suffix == ".docx":
        return _extract_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def _extract_from_pdf(filepath: str) -> str:
    """Extract text from PDF using pdfplumber."""
    if not PDFPLUMBER_AVAILABLE:
        raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")

    text_parts = []

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

            # Also extract tables
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row:
                        text_parts.append(" | ".join(str(cell) for cell in row if cell))

    return "\n".join(text_parts)


def _extract_from_docx(filepath: str) -> str:
    """Extract text from DOCX using python-docx."""
    if not DOCX_AVAILABLE:
        raise RuntimeError("python-docx not installed. Run: pip install python-docx")

    doc = docx.Document(filepath)
    text_parts = []

    # Extract paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)

    # Extract tables
    for table in doc.tables:
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                if cell.text.strip():
                    row_text.append(cell.text.strip())
            if row_text:
                text_parts.append(" | ".join(row_text))

    return "\n".join(text_parts)


def get_file_info(filepath: str) -> dict:
    """Get file metadata."""
    path = Path(filepath)
    stat = path.stat()

    return {
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": stat.st_mtime,
    }


def save_uploaded_file(file, upload_folder: Path, user_id: int) -> Path:
    """
    Save uploaded file to user-specific folder.
    Returns saved file path.
    """
    from werkzeug.utils import secure_filename

    filename = secure_filename(file.filename)
    user_folder = upload_folder / str(user_id)
    user_folder.mkdir(parents=True, exist_ok=True)

    filepath = user_folder / filename
    file.save(filepath)

    return filepath


def delete_file(filepath: str) -> bool:
    """Delete file if exists."""
    try:
        os.remove(filepath)
        return True
    except OSError:
        return False


if __name__ == "__main__":
    # Test
    print("File utilities loaded")
    print(f"PDF support: {PDFPLUMBER_AVAILABLE}")
    print(f"DOCX support: {DOCX_AVAILABLE}")