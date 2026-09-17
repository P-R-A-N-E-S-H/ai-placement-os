import io
import pytest
import docx
from pypdf import PdfWriter
from app.core.exceptions import ValidationError
from app.services.resume_parser import DocumentParser


def test_txt_parser():
    """Test plain text document parsing."""
    sample_text = "Pranesh M\nB.Tech AI Engineer\nSkills: Python, PyTorch, FastAPI, SQL\nCGPA: 9.1"
    raw_text, file_type, size = DocumentParser.parse_document("resume.txt", sample_text.encode("utf-8"))
    assert file_type == "txt"
    assert "Pranesh M" in raw_text
    assert "Python" in raw_text
    assert size > 0


def test_docx_parser():
    """Test docx document parsing with paragraphs and tables."""
    doc = docx.Document()
    doc.add_paragraph("Alex Parker")
    doc.add_paragraph("Email: alex@placementos.ai")
    doc.add_paragraph("Projects: Autonomous Multi-Agent Career Intelligence Platform")
    doc.add_paragraph("Skills: C++, Python, PyTorch, Docker, Kubernetes")

    buffer = io.BytesIO()
    doc.save(buffer)
    docx_bytes = buffer.getvalue()

    raw_text, file_type, size = DocumentParser.parse_document("alex_resume.docx", docx_bytes)
    assert file_type == "docx"
    assert "Alex Parker" in raw_text
    assert "Kubernetes" in raw_text
    assert size > 0


def test_unsupported_file_extension_fails():
    """Test unsupported extensions (.exe, .jpg) raise ValidationError."""
    with pytest.raises(ValidationError) as exc:
        DocumentParser.validate_file("resume.png", b"fake image bytes")
    assert "Unsupported file format" in str(exc.value)


def test_empty_file_fails():
    """Test empty file raises ValidationError."""
    with pytest.raises(ValidationError) as exc:
        DocumentParser.validate_file("empty.pdf", b"")
    assert "Uploaded file is empty" in str(exc.value)
