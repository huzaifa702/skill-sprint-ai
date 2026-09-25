"""
SkillSprint AI - Multi-Format Document Parsing Engine
Theme: OnboardVerse | Category: Generative AI PowerPlay

Extracts structured sections, headings, page/paragraph references,
and text content from PDF, DOCX, TXT, and Markdown documents.
Preserves Document ID, Version, Section Number, Heading, and Exact Source References.
"""

import os
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ParsedSection:
    section_number: str
    heading: str
    content: str
    page_or_location: str
    word_count: int = 0

    def __post_init__(self):
        self.word_count = len(self.content.split())


@dataclass
class ParsedDocument:
    document_id: str
    document_code: str
    title: str
    category: str
    version_tag: str
    file_type: str
    file_path: str
    sections: List[ParsedSection] = field(default_factory=list)
    raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def parse_pdf_document(file_path: str, doc_code: str, title: str, version: str) -> ParsedDocument:
    """Extract pages, sections, and headings from a PDF file using pypdf."""
    import pypdf

    reader = pypdf.PdfReader(file_path)
    sections: List[ParsedSection] = []
    full_text_parts = []

    current_section = "1.0"
    current_heading = "General Overview"
    current_content = []
    current_page = 1

    section_pattern = re.compile(r"^(?:Section\s+)?(\d+(?:\.\d+)*)\s*[:\-\.]?\s*(.+)$", re.IGNORECASE)

    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        page_text = page.extract_text() or ""
        full_text_parts.append(page_text)

        lines = page_text.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            match = section_pattern.match(line_str)
            if match and len(line_str) < 100:
                # Flush previous section
                if current_content:
                    sections.append(ParsedSection(
                        section_number=current_section,
                        heading=current_heading,
                        content="\n".join(current_content).strip(),
                        page_or_location=f"Page {current_page}"
                    ))
                    current_content = []

                current_section = match.group(1)
                current_heading = match.group(2).strip()
                current_page = page_num
            else:
                current_content.append(line_str)

    if current_content:
        sections.append(ParsedSection(
            section_number=current_section,
            heading=current_heading,
            content="\n".join(current_content).strip(),
            page_or_location=f"Page {current_page}"
        ))

    # If no explicit numbered sections found, split by pages
    if not sections:
        for idx, page in enumerate(reader.pages):
            p_text = page.extract_text() or ""
            sections.append(ParsedSection(
                section_number=f"{idx+1}.0",
                heading=f"Page {idx+1} Content",
                content=p_text.strip(),
                page_or_location=f"Page {idx+1}"
            ))

    return ParsedDocument(
        document_id=doc_code,
        document_code=doc_code,
        title=title,
        category="Policy",
        version_tag=version,
        file_type="pdf",
        file_path=file_path,
        sections=sections,
        raw_text="\n\n".join(full_text_parts)
    )


def parse_docx_document(file_path: str, doc_code: str, title: str, version: str) -> ParsedDocument:
    """Extract paragraphs, headings, and sections from DOCX using direct OpenXML parsing."""
    sections: List[ParsedSection] = []
    full_text_parts = []

    current_section = "1.0"
    current_heading = "General Overview"
    current_content = []
    para_counter = 0

    section_pattern = re.compile(r"^(?:Section\s+)?(\d+(?:\.\d+)*)\s*[:\-\.]?\s*(.+)$", re.IGNORECASE)

    try:
        with zipfile.ZipFile(file_path, "r") as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

            for p in tree.iterfind(".//w:p", namespace):
                texts = [node.text for node in p.iterfind(".//w:t", namespace) if node.text]
                p_text = "".join(texts).strip()
                if not p_text:
                    continue

                para_counter += 1
                full_text_parts.append(p_text)

                match = section_pattern.match(p_text)
                if match and len(p_text) < 120:
                    if current_content:
                        sections.append(ParsedSection(
                            section_number=current_section,
                            heading=current_heading,
                            content="\n".join(current_content).strip(),
                            page_or_location=f"Para {max(1, para_counter - len(current_content))}-{para_counter-1}"
                        ))
                        current_content = []

                    current_section = match.group(1)
                    current_heading = match.group(2).strip()
                else:
                    current_content.append(p_text)

        if current_content:
            sections.append(ParsedSection(
                section_number=current_section,
                heading=current_heading,
                content="\n".join(current_content).strip(),
                page_or_location=f"Para {max(1, para_counter - len(current_content) + 1)}-{para_counter}"
            ))
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX file '{file_path}': {str(e)}")

    if not sections:
        sections.append(ParsedSection(
            section_number="1.0",
            heading="Full Document",
            content="\n".join(full_text_parts),
            page_or_location="Full Document"
        ))

    return ParsedDocument(
        document_id=doc_code,
        document_code=doc_code,
        title=title,
        category="SOP",
        version_tag=version,
        file_type="docx",
        file_path=file_path,
        sections=sections,
        raw_text="\n\n".join(full_text_parts)
    )


def parse_text_or_markdown(file_path: str, doc_code: str, title: str, version: str) -> ParsedDocument:
    """Parse TXT or Markdown file into structured sections by markdown headings or numbering."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    lines = text.splitlines()
    sections: List[ParsedSection] = []
    current_section = "1.0"
    current_heading = "Introduction"
    current_content = []
    line_start = 1

    md_heading_pattern = re.compile(r"^(#{1,4})\s*(?:Section\s+)?(\d+(?:\.\d+)*)?\s*(.+)$")
    sec_num_pattern = re.compile(r"^(?:Section\s+)?(\d+(?:\.\d+)*)\s*[:\-\.]?\s*(.+)$", re.IGNORECASE)

    for idx, line in enumerate(lines):
        line_str = line.strip()
        if not line_str:
            continue

        md_match = md_heading_pattern.match(line_str)
        sec_match = sec_num_pattern.match(line_str) if not md_match else None

        if md_match:
            if current_content:
                sections.append(ParsedSection(
                    section_number=current_section,
                    heading=current_heading,
                    content="\n".join(current_content).strip(),
                    page_or_location=f"Lines {line_start}-{idx}"
                ))
                current_content = []

            sec_num = md_match.group(2) or f"{len(sections)+1}.0"
            heading_txt = md_match.group(3).strip()
            current_section = sec_num
            current_heading = heading_txt
            line_start = idx + 1

        elif sec_match and len(line_str) < 100:
            if current_content:
                sections.append(ParsedSection(
                    section_number=current_section,
                    heading=current_heading,
                    content="\n".join(current_content).strip(),
                    page_or_location=f"Lines {line_start}-{idx}"
                ))
                current_content = []

            current_section = sec_match.group(1)
            current_heading = sec_match.group(2).strip()
            line_start = idx + 1
        else:
            current_content.append(line_str)

    if current_content:
        sections.append(ParsedSection(
            section_number=current_section,
            heading=current_heading,
            content="\n".join(current_content).strip(),
            page_or_location=f"Lines {line_start}-{len(lines)}"
        ))

    file_ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    return ParsedDocument(
        document_id=doc_code,
        document_code=doc_code,
        title=title,
        category="Manual",
        version_tag=version,
        file_type=file_ext,
        file_path=file_path,
        sections=sections,
        raw_text=text
    )


def parse_document(file_path: str, doc_code: str, title: str, version: str) -> ParsedDocument:
    """Dispatcher to parse any supported document type."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return parse_pdf_document(file_path, doc_code, title, version)
    elif ext == ".docx":
        return parse_docx_document(file_path, doc_code, title, version)
    elif ext in [".txt", ".md"]:
        return parse_text_or_markdown(file_path, doc_code, title, version)
    else:
        raise ValueError(f"Unsupported document format: '{ext}'. Allowed: .pdf, .docx, .txt, .md")
