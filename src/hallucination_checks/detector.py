"""
SkillSprint AI - Hallucination & Unsupported Content Detection Engine
Theme: OnboardVerse | Category: Generative AI PowerPlay

Identifies generated statements lacking factual support in approved documents.
Distinguishes:
1. Source-supported content
2. Reasonable instructional phrasing
3. Unsupported factual claims (hallucinations)
"""

import re
from typing import Any, Dict, List, Set, Tuple


def extract_factual_claims(text: str) -> List[str]:
    """Extract sentences containing specific numerical values, percentages, or strict mandates."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    claims = []
    for s in sentences:
        s_clean = s.strip()
        # Look for factual claims: digits, days, hours, percentages, standards, specific mandates
        if re.search(r"\b\d+\b|%|\$|standard|regulation|iso|faa|compliance|strict|never|must", s_clean, re.IGNORECASE):
            if len(s_clean.split()) >= 4:
                claims.append(s_clean)
    return claims


def detect_hallucinated_claims(
    generated_text: str,
    approved_source_text: str,
    threshold_keyword_overlap: float = 0.45
) -> List[Dict[str, Any]]:
    """
    Compare factual claims in generated text against approved source corpus.
    Flags claims with insufficient lexical/semantic grounding.
    """
    claims = extract_factual_claims(generated_text)
    hallucinations = []
    approved_words = set(re.findall(r"\w+", approved_source_text.lower()))

    for claim in claims:
        claim_words = [w for w in re.findall(r"\w+", claim.lower()) if len(w) > 3]
        if not claim_words:
            continue

        matched_words = [w for w in claim_words if w in approved_words]
        overlap_ratio = len(matched_words) / len(claim_words)

        if overlap_ratio < threshold_keyword_overlap:
            hallucinations.append({
                "claim": claim,
                "overlap_ratio": round(overlap_ratio, 2),
                "status": "UNSUPPORTED_FACTUAL_CLAIM",
                "severity": "HIGH",
                "reason": (
                    f"Only {int(overlap_ratio*100)}% of key terms found in approved company documents. "
                    f"Possible AI hallucination or ungrounded policy assertion."
                )
            })

    return hallucinations


def check_unsupported_topic_request(
    topic_query: str,
    approved_documents_text: str
) -> Dict[str, Any]:
    """
    Hidden-Topic Challenge Handler:
    Checks if a requested training topic exists in approved company documentation.
    If unsupported, advises refusal or manual review rather than fabricating rules.
    """
    topic_keywords = [w for w in re.findall(r"\w+", topic_query.lower()) if len(w) > 3]
    if not topic_keywords:
        return {"is_supported": False, "reason": "Empty or trivial topic request."}

    corpus_lower = approved_documents_text.lower()
    matches = [kw for kw in topic_keywords if kw in corpus_lower]
    support_ratio = len(matches) / len(topic_keywords)

    is_supported = support_ratio >= 0.5
    return {
        "is_supported": is_supported,
        "support_ratio": round(support_ratio, 2),
        "matched_keywords": matches,
        "action": "PROCEED" if is_supported else "REFUSE_AND_FLAG",
        "explanation": (
            "Topic is verified against approved organizational documents."
            if is_supported else
            f"The topic '{topic_query}' was NOT found in any approved organizational documents. "
            f"The application refuses ungrounded generation and flags the request for manual review."
        )
    }
