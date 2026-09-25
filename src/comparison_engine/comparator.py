"""
SkillSprint AI - GenAI vs. Python Comparison Engine
Theme: OnboardVerse | Category: Generative AI PowerPlay

Compares GenAI structured output side-by-side with Python ground-truth requirements.
Stores structured comparison audits and provides drill-down analytics.
"""

from typing import Any, Dict, List, Optional
from src.database.db import execute_commit, query_all


def persist_comparison_results(
    plan_id: str,
    job_role_id: str,
    comparison_items: List[Dict[str, Any]]
) -> int:
    """
    Save row-by-row comparison audits between Python ground truth and GenAI plan.
    """
    inserted = 0
    for idx, item in enumerate(comparison_items):
        comp_id = f"CMP-{plan_id}-{idx+1:03d}"
        sql = """
            INSERT INTO comparison_results (
                comparison_id, plan_id, requirement_id, job_role_id,
                python_expected_text, genai_generated_text, match_status,
                source_document_id, source_section_id, coverage_status,
                traceability_status, validation_status, disagreement_explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_commit(sql, (
            comp_id,
            plan_id,
            item.get("requirement_id", "REQ-UNK"),
            job_role_id,
            item.get("python_expected", ""),
            item.get("genai_result", ""),
            item.get("match_status", "MATCH"),
            item.get("source_document_id", ""),
            item.get("source_section_id", ""),
            item.get("coverage_status", "Covered"),
            item.get("traceability_status", "Fully Traceable"),
            item.get("validation_status", "Verified"),
            item.get("disagreement_explanation")
        ))
        inserted += 1
    return inserted


def get_plan_comparison_report(plan_id: str) -> List[Dict[str, Any]]:
    """Fetch complete side-by-side comparison table for an onboarding plan."""
    sql = """
        SELECT
            cr.comparison_id,
            cr.requirement_id,
            r.code as requirement_code,
            r.title as requirement_title,
            r.category as requirement_category,
            r.is_mandatory,
            cr.python_expected_text,
            cr.genai_generated_text,
            cr.match_status,
            cr.source_document_id,
            cr.source_section_id,
            cr.coverage_status,
            cr.traceability_status,
            cr.validation_status,
            cr.disagreement_explanation
        FROM comparison_results cr
        LEFT JOIN requirements r ON cr.requirement_id = r.requirement_id
        WHERE cr.plan_id = ?
        ORDER BY r.is_mandatory DESC, cr.match_status ASC
    """
    return query_all(sql, (plan_id,))
