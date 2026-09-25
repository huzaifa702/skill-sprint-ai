"""
SkillSprint AI - Policy Precedence & Contradiction Detection Engine
Theme: OnboardVerse | Category: Generative AI PowerPlay

Implements configurable document precedence hierarchies:
1. Latest Approved Policy
2. Compliance Directive
3. Department SOP
4. Process Manual
5. Employee Handbook
6. FAQ
7. Informal Guidance

Detects contradictions between versions, FAQs vs policies, and generated items vs company rules.
"""

from typing import Any, Dict, List, Optional, Tuple
from src.database.db import query_all, query_one


def get_precedence_rules() -> List[Dict[str, Any]]:
    """Retrieve active policy precedence ranks from database ordered by rank (1 = highest)."""
    return query_all(
        "SELECT precedence_id, category_name, precedence_rank, description FROM policy_precedence_rules WHERE is_active = 1 ORDER BY precedence_rank ASC"
    )


def resolve_precedence(doc_a_category: str, doc_b_category: str) -> str:
    """
    Given two conflicting document categories, determine which one has higher authority.
    Returns category name of the authoritative document.
    """
    rules = {r["category_name"].lower(): r["precedence_rank"] for r in get_precedence_rules()}
    rank_a = rules.get(doc_a_category.lower(), 99)
    rank_b = rules.get(doc_b_category.lower(), 99)

    if rank_a < rank_b:
        return doc_a_category
    elif rank_b < rank_a:
        return doc_b_category
    return doc_a_category  # Equal rank, fallback to latest


def check_conflicting_clauses(
    item_claim: str,
    active_documents: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Scan generated statements or requirements against documented conflict cases
    (e.g., maximum remote work days, data retention period, expense approval thresholds).
    """
    contradictions = []
    claim_lower = item_claim.lower()

    # Predefined known conflict checkpoints across enterprise document types
    conflict_checkpoints = [
        {
            "topic": "Remote Work Allowance",
            "regex": r"remote\s+work|work\s+from\s+home|telecommut",
            "rule_latest": "Maximum 2 days per week remote work with manager approval (POL-HR-02 v2.0)",
            "rule_old": "Up to 4 days remote work permitted (FAQ-GEN-01 / POL-HR-02 v1.0)",
            "authoritative_category": "Latest Approved Policy",
            "deprecated_category": "FAQ"
        },
        {
            "topic": "Flight Telemetry Data Retention",
            "regex": r"telemetry\s+data|flight\s+logs|data\s+retention",
            "rule_latest": "Flight logs must be retained encrypted for 7 years (POL-SEC-01 v2.0)",
            "rule_old": "Telemetry logs may be purged after 180 days (SOP-OPS-01 v1.0)",
            "authoritative_category": "Latest Approved Policy",
            "deprecated_category": "Department SOP"
        },
        {
            "topic": "UAV Pre-Flight Inspection Sign-Off",
            "regex": r"pre-flight\s+inspection|flight\s+sign-off|airworthiness\s+check",
            "rule_latest": "Requires dual sign-off from both Flight QA and Lead Pilot (SOP-QA-03 v2.0)",
            "rule_old": "Single operator sign-off sufficient (HANDBOOK-2024)",
            "authoritative_category": "Department SOP",
            "deprecated_category": "Employee Handbook"
        }
    ]

    for cp in conflict_checkpoints:
        import re
        if re.search(cp["regex"], claim_lower):
            # If claim matches the deprecated wording rather than the authoritative policy
            if any(term in claim_lower for term in ["4 days", "180 days", "single operator"]):
                contradictions.append({
                    "topic": cp["topic"],
                    "generated_statement": item_claim,
                    "authoritative_rule": cp["rule_latest"],
                    "conflicting_reference": cp["rule_old"],
                    "higher_precedence_source": cp["authoritative_category"],
                    "deprecated_source": cp["deprecated_category"],
                    "explanation": (
                        f"Generated content reflects '{cp['deprecated_category']}' which is superseded by "
                        f"'{cp['authoritative_category']}' according to enterprise precedence rules."
                    )
                })

    return contradictions
