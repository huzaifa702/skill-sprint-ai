"""
SkillSprint AI - Content Chunking & Source Traceability Engine
Theme: OnboardVerse | Category: Generative AI PowerPlay

Splits parsed document sections into manageable, context-preserved chunks.
Ensures every chunk retains chunk_id, document_id, section_id, heading,
source location, and version tag for ground-truth traceability.
"""

from dataclasses import dataclass
from typing import List
from src.document_processing.parser import ParsedDocument, ParsedSection


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    section_number: str
    heading: str
    source_location: str
    version_tag: str
    content: str
    token_count_approx: int
    chunk_index: int


def chunk_document(
    parsed_doc: ParsedDocument,
    max_words_per_chunk: int = 250,
    overlap_words: int = 35
) -> List[DocumentChunk]:
    """
    Split document sections into overlapping chunks to ensure semantic continuity
    while strictly binding every chunk to its document ID and section reference.
    """
    chunks: List[DocumentChunk] = []
    chunk_counter = 1

    for sec in parsed_doc.sections:
        words = sec.content.split()
        if not words:
            continue

        if len(words) <= max_words_per_chunk:
            chunk_id = f"CHK-{parsed_doc.document_code}-{sec.section_number.replace('.', '_')}-{chunk_counter}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                document_id=parsed_doc.document_code,
                section_number=sec.section_number,
                heading=sec.heading,
                source_location=sec.page_or_location,
                version_tag=parsed_doc.version_tag,
                content=sec.content,
                token_count_approx=int(len(words) * 1.3),
                chunk_index=chunk_counter
            ))
            chunk_counter += 1
        else:
            # Overlapping sliding window
            step = max_words_per_chunk - overlap_words
            start = 0
            while start < len(words):
                end = min(start + max_words_per_chunk, len(words))
                chunk_words = words[start:end]
                chunk_content = " ".join(chunk_words)

                sub_id = f"CHK-{parsed_doc.document_code}-{sec.section_number.replace('.', '_')}-{chunk_counter}"
                chunks.append(DocumentChunk(
                    chunk_id=sub_id,
                    document_id=parsed_doc.document_code,
                    section_number=sec.section_number,
                    heading=sec.heading,
                    source_location=sec.page_or_location,
                    version_tag=parsed_doc.version_tag,
                    content=chunk_content,
                    token_count_approx=int(len(chunk_words) * 1.3),
                    chunk_index=chunk_counter
                ))
                chunk_counter += 1
                if end == len(words):
                    break
                start += step

    return chunks
