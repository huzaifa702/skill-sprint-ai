"""
SkillSprint AI - Automated Test Suite: Document Processing & Parsing
Theme: OnboardVerse | Category: Generative AI PowerPlay
"""

import os
import pytest
from src.document_processing.parser import parse_document, parse_pdf_document, parse_docx_document
from src.document_processing.chunker import chunk_document
from src.document_processing.validator import validate_document_upload


def test_pdf_parsing_extracts_sections_and_metadata():
    pdf_path = "sample_documents/POL-SEC-01.pdf"
    assert os.path.exists(pdf_path), "Sample PDF document must exist."
    doc = parse_document(pdf_path, "POL-SEC-01", "Information Security Policy", "v2.0")
    assert doc.document_code == "POL-SEC-01"
    assert len(doc.sections) >= 3
    assert any("Telemetry" in s.heading for s in doc.sections)
    assert any("Page" in s.page_or_location for s in doc.sections)


def test_docx_parsing_extracts_paragraphs_and_sections():
    docx_path = "sample_documents/POL-HR-02.docx"
    assert os.path.exists(docx_path), "Sample DOCX document must exist."
    doc = parse_document(docx_path, "POL-HR-02", "Remote Work Policy", "v2.0")
    assert doc.document_code == "POL-HR-02"
    assert len(doc.sections) >= 2
    assert any("Remote Work" in s.heading for s in doc.sections)
    assert any("Para" in s.page_or_location for s in doc.sections)


def test_chunking_preserves_traceability_metadata():
    pdf_path = "sample_documents/POL-SAF-01.pdf"
    doc = parse_document(pdf_path, "POL-SAF-01", "Flight Safety Policy", "v2.0")
    chunks = chunk_document(doc, max_words_per_chunk=100)
    assert len(chunks) >= len(doc.sections)
    for chk in chunks:
        assert chk.document_id == "POL-SAF-01"
        assert chk.version_tag == "v2.0"
        assert chk.chunk_id.startswith("CHK-POL-SAF-01-")
        assert len(chk.content) > 0


def test_document_validation_rejects_empty_file(tmp_path):
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_text("")
    res = validate_document_upload(str(empty_file), "POL-EMP-01", "Empty Document", "Policy", "v1.0")
    assert res["is_valid"] is False
    assert any("empty" in err.lower() for err in res["errors"])


def test_document_validation_rejects_unsupported_extension(tmp_path):
    exe_file = tmp_path / "malicious.exe"
    exe_file.write_text("malicious payload")
    res = validate_document_upload(str(exe_file), "POL-MAL-01", "Bad Extension", "Policy", "v1.0")
    assert res["is_valid"] is False
    assert any("extension" in err.lower() for err in res["errors"])
