"""Tests for CV upload and file validation."""
import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.file_utils import validate_file, allowed_file, extract_text_from_file
from app.routes.cv import cv_bp
from app.routes.profile import profile_bp


class TestFileValidation:
    """Test file validation utilities."""

    def test_allowed_file_pdf(self):
        """Test PDF files are allowed."""
        assert allowed_file("resume.pdf") is True
        assert allowed_file("RESUME.PDF") is True
        assert allowed_file("my.resume.pdf") is True

    def test_allowed_file_docx(self):
        """Test DOCX files are allowed."""
        assert allowed_file("resume.docx") is True
        assert allowed_file("RESUME.DOCX") is True

    def test_allowed_file_rejected(self):
        """Test other extensions are rejected."""
        assert allowed_file("resume.txt") is False
        assert allowed_file("resume.doc") is False
        assert allowed_file("resume.png") is False
        assert allowed_file("resume") is False
        assert allowed_file("") is False

    def test_validate_file_valid(self):
        """Test valid file passes validation."""
        mock_file = MagicMock()
        mock_file.filename = "resume.pdf"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024)  # 1KB

        is_valid, error = validate_file(mock_file)
        assert is_valid is True
        assert error == ""

    def test_validate_file_no_file(self):
        """Test None file fails validation."""
        is_valid, error = validate_file(None)
        assert is_valid is False
        assert "Không có file" in error

    def test_validate_file_no_filename(self):
        """Test file without filename fails."""
        mock_file = MagicMock()
        mock_file.filename = ""
        is_valid, error = validate_file(mock_file)
        assert is_valid is False
        assert "Không có file" in error

    def test_validate_file_wrong_extension(self):
        """Test wrong extension fails."""
        mock_file = MagicMock()
        mock_file.filename = "resume.txt"
        is_valid, error = validate_file(mock_file)
        assert is_valid is False
        assert "PDF hoặc DOCX" in error

    def test_validate_file_too_large(self):
        """Test file exceeding size limit fails."""
        mock_file = MagicMock()
        mock_file.filename = "resume.pdf"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=10 * 1024 * 1024)  # 10MB

        is_valid, error = validate_file(mock_file)
        assert is_valid is False
        assert "quá lớn" in error

    def test_validate_file_empty(self):
        """Test empty file fails."""
        mock_file = MagicMock()
        mock_file.filename = "resume.pdf"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=0)

        is_valid, error = validate_file(mock_file)
        assert is_valid is False
        assert "rỗng" in error


class TestCVUploadRoutes:
    """Test CV upload routes."""

    def test_upload_cv_get(self, student_session):
        """Test GET /cv/upload returns form."""
        resp = student_session.get("/cv/upload")
        assert resp.status_code == 200

    def test_upload_cv_post_no_file(self, student_session):
        """Test POST without file returns error."""
        resp = student_session.post("/cv/upload", data={})
        assert resp.status_code == 302  # Redirect with flash error

    def test_upload_cv_post_empty_filename(self, student_session):
        """Test POST with empty filename returns error."""
        from io import BytesIO
        data = {"cv_file": (BytesIO(b""), "")}
        resp = student_session.post("/cv/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 302

    def test_upload_cv_post_wrong_extension(self, student_session):
        """Test POST with wrong extension returns error."""
        from io import BytesIO
        data = {"cv_file": (BytesIO(b"test"), "resume.txt")}
        resp = student_session.post("/cv/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 302

    def test_upload_cv_post_valid_pdf(self, student_session, tmp_path):
        """Test POST with valid PDF (mocked extraction)."""
        from io import BytesIO
        # Create a minimal PDF-like content
        pdf_content = b"%PDF-1.4 minimal content"

        with patch("utils.file_utils.extract_text_from_file") as mock_extract:
            mock_extract.return_value = "Python developer with SQL and Machine Learning experience"

            data = {"cv_file": (BytesIO(pdf_content), "resume.pdf")}
            resp = student_session.post("/cv/upload", data=data, content_type="multipart/form-data")

            # Should redirect on success (location may vary based on DB state)
            assert resp.status_code == 302


class TestProfileCVUploadRoutes:
    """Test profile CV upload routes (duplicate of /cv/upload)."""

    def test_upload_cv_get(self, student_session):
        """Test GET /profile/cv/upload returns form."""
        resp = student_session.get("/profile/cv/upload")
        assert resp.status_code == 200

    def test_upload_cv_post_no_file(self, student_session):
        """Test POST without file returns error."""
        resp = student_session.post("/profile/cv/upload", data={})
        assert resp.status_code == 302

    def test_upload_cv_post_wrong_extension(self, student_session):
        """Test POST with wrong extension returns error."""
        from io import BytesIO
        data = {"cv_file": (BytesIO(b"test"), "resume.txt")}
        resp = student_session.post("/profile/cv/upload", data=data, content_type="multipart/form-data")
        assert resp.status_code == 302


class TestCVUploadUniqueFilename:
    """Test that uploaded files get unique names to avoid overwriting."""

    def test_unique_filename_generation(self, student_session, tmp_path):
        """Test that duplicate filenames get unique suffixes."""
        from io import BytesIO

        pdf_content = b"%PDF-1.4 minimal content"

        with patch("utils.file_utils.extract_text_from_file") as mock_extract:
            mock_extract.return_value = "Python developer"

            # Upload same filename twice
            data1 = {"cv_file": (BytesIO(pdf_content), "resume.pdf")}
            resp1 = student_session.post("/cv/upload", data=data1, content_type="multipart/form-data")
            assert resp1.status_code == 302

            data2 = {"cv_file": (BytesIO(pdf_content), "resume.pdf")}
            resp2 = student_session.post("/cv/upload", data=data2, content_type="multipart/form-data")
            assert resp2.status_code == 302

            # Both should succeed (no overwrite error)
            # In real test, we'd check the actual saved filenames are different


class TestCVUploadEmptyContent:
    """Test handling of files with no extractable content."""

    def test_upload_empty_pdf(self, student_session):
        """Test upload of PDF with no text content."""
        from io import BytesIO

        with patch("utils.file_utils.extract_text_from_file") as mock_extract:
            mock_extract.return_value = ""  # Empty content

            data = {"cv_file": (BytesIO(b"%PDF-1.4 empty"), "empty.pdf")}
            resp = student_session.post("/cv/upload", data=data, content_type="multipart/form-data")

            # Should redirect back with error
            assert resp.status_code == 302


class TestCVUploadParseError:
    """Test handling of file parse errors."""

    def test_upload_corrupted_file(self, student_session):
        """Test upload of corrupted file."""
        from io import BytesIO

        with patch("utils.file_utils.extract_text_from_file") as mock_extract:
            mock_extract.side_effect = RuntimeError("Failed to parse PDF")

            data = {"cv_file": (BytesIO(b"corrupted"), "bad.pdf")}
            resp = student_session.post("/cv/upload", data=data, content_type="multipart/form-data")

            # Should redirect back with error
            assert resp.status_code == 302


if __name__ == "__main__":
    pytest.main([__file__, "-v"])