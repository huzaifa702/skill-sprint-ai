"""
SkillSprint AI - Deterministic Requirement Extraction Layer
Theme: OnboardVerse | Category: Generative AI PowerPlay

Extracts structured, identifiable enterprise requirements from parsed documents.
Distinguishes requirement types (Must Know, Must Complete, Must Demonstrate,
Must Acknowledge, Recommended, Optional) and mandatory vs. informational clauses.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from src.document_processing.parser import ParsedDocument, ParsedSection


@dataclass
class ExtractedRequirement:
    requirement_id: str
    code: str
    document_id: str
    section_id: str
    version_tag: str
    category: str
    title: str
    description: str
    requirement_type: str  # Must Know, Must Complete, Must Demonstrate, Must Acknowledge, Recommended, Optional
    is_mandatory: int      # 1 or 0
    priority: str          # Critical, High, Medium, Low
    compliance_ref: Optional[str] = None


# Deterministic keyword patterns for requirement classification
MANDATORY_TRIGGERS = [
    r"\bshall\b", r"\bmust\b", r"\brequired\b", r"\bmandatory\b",
    r"\bis\s+obligated\s+to\b", r"\bstrictly\s+prohibited\b", r"\bunder\s+no\s+circumstances\b"
]

RECOMMENDED_TRIGGERS = [
    r"\bshould\b", r"\brecommended\b", r"\bencouraged\b", r"\badvised\b", r"\bbest\s+practice\b"
]

DEMONSTRATE_TRIGGERS = [
    r"\bdemonstrate\b", r"\bperform\b", r"\bexecute\b", r"\bsubmit\s+evidence\b", r"\bpass\s+assessment\b"
]

COMPLETE_TRIGGERS = [
    r"\bcomplete\b", r"\bfinish\b", r"\bundergo\b", r"\battend\b", r"\bparticipate\b"
]

ACKNOWLEDGE_TRIGGERS = [
    r"\bsign\b", r"\backnowledge\b", r"\bconfirm\b", r"\bagree\s+to\b", r"\baffirm\b"
]


def classify_sentence(sentence: str) -> Dict[str, Any]:
    """Classify requirement type and mandatory status from grammatical and lexical indicators."""
    s_lower = sentence.lower()

    # Check if mandatory
    is_mandatory = 1 if any(re.search(pat, s_lower) for pat in MANDATORY_TRIGGERS) else 0

    # Determine requirement type
    if any(re.search(pat, s_lower) for pat in ACKNOWLEDGE_TRIGGERS):
        req_type = "Must Acknowledge" if is_mandatory else "Recommended"
    elif any(re.search(pat, s_lower) for pat in DEMONSTRATE_TRIGGERS):
        req_type = "Must Demonstrate" if is_mandatory else "Recommended"
    elif any(re.search(pat, s_lower) for pat in COMPLETE_TRIGGERS):
        req_type = "Must Complete" if is_mandatory else "Optional"
    elif is_mandatory:
        req_type = "Must Know"
    elif any(re.search(pat, s_lower) for pat in RECOMMENDED_TRIGGERS):
        req_type = "Recommended"
    else:
        req_type = "Optional"

    # Priority
    if "critical" in s_lower or "severe" in s_lower or "immediate" in s_lower or "prohibited" in s_lower:
        priority = "Critical"
    elif is_mandatory:
        priority = "High"
    elif req_type == "Recommended":
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "requirement_type": req_type,
        "is_mandatory": is_mandatory,
        "priority": priority
    }


def extract_requirements_from_document(parsed_doc: ParsedDocument) -> List[ExtractedRequirement]:
    """
    Extract structured requirement entities from parsed document sections.
    Generates stable, unique requirement identifiers tied to document code and section.
    """
    extracted: List[ExtractedRequirement] = []
    counter = 1

    for sec in parsed_doc.sections:
        # Split section content into sentences/clauses
        sentences = re.split(r"(?<=[.!?])\s+", sec.content)
        for s in sentences:
            s_clean = s.strip()
            # Filter out very short lines or headers
            if len(s_clean.split()) < 6:
                continue

            classification = classify_sentence(s_clean)

            # Keep all mandatory or recommended clauses as identifiable requirements
            if classification["is_mandatory"] or classification["requirement_type"] != "Optional":
                req_code = f"REQ-{parsed_doc.document_code}-{sec.section_number.replace('.', '_')}-{counter:03d}"
                req_id = req_code

                # Generate concise title from section heading or first words
                title_words = s_clean.split()[:7]
                title = f"{sec.heading}: {' '.join(title_words)}..."

                extracted.append(ExtractedRequirement(
                    requirement_id=req_id,
                    code=req_code,
                    document_id=parsed_doc.document_code,
                    section_id=sec.section_number,
                    version_tag=parsed_doc.version_tag,
                    category=parsed_doc.category,
                    title=title,
                    description=s_clean,
                    requirement_type=classification["requirement_type"],
                    is_mandatory=classification["is_mandatory"],
                    priority=classification["priority"],
                    compliance_ref=f"{parsed_doc.document_code} Sec {sec.section_number}"
                ))
                counter += 1

    return extracted
