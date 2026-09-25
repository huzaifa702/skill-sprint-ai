"""
SkillSprint AI - Role Requirement Matrix (Independent Ground Truth)
Theme: OnboardVerse | Category: Generative AI PowerPlay

Maintains and queries the structured ground-truth mapping between
organizational job roles and policy/process requirements.
Independent from GenAI logic.
"""

from typing import Any, Dict, List, Optional
from src.database.db import execute_commit, query_all, query_one


def get_matrix_for_role(role_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve the complete ground-truth requirement matrix for a specific job role.
    Includes document ID, section reference, mandatory flag, due stage, and priority.
    """
    sql = """
        SELECT
            r.requirement_id,
            r.code as requirement_code,
            r.title as requirement_title,
            r.description as requirement_description,
            r.requirement_type,
            r.category as requirement_category,
            r.document_id,
            r.section_id,
            r.version_tag,
            d.title as document_title,
            d.category as document_category,
            d.status as document_status,
            rm.mandatory_for_role,
            rm.role_priority,
            rm.due_stage,
            rm.assessment_required,
            rm.practical_task_required,
            jr.role_id,
            jr.code as role_code,
            jr.title as role_title
        FROM role_requirements rm
        JOIN requirements r ON rm.requirement_id = r.requirement_id
        JOIN job_roles jr ON rm.job_role_id = jr.role_id
        JOIN documents d ON r.document_id = d.document_id
        WHERE rm.job_role_id = ? AND r.is_active = 1
        ORDER BY
            CASE rm.due_stage
                WHEN 'Day 1' THEN 1
                WHEN 'Week 1' THEN 2
                WHEN 'Week 2' THEN 3
                WHEN 'First 30 Days' THEN 4
                WHEN 'First 60 Days' THEN 5
                WHEN 'First 90 Days' THEN 6
                ELSE 7
            END,
            CASE rm.role_priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END
    """
    return query_all(sql, (role_id,))


def get_mandatory_requirements_for_role(role_id: str) -> List[Dict[str, Any]]:
    """Retrieve only mandatory ground-truth requirements for a role."""
    all_reqs = get_matrix_for_role(role_id)
    return [r for r in all_reqs if r["mandatory_for_role"] == 1]


def get_prerequisites_for_requirement(requirement_id: str) -> List[Dict[str, Any]]:
    """Retrieve prerequisite requirements that must be completed prior to this requirement."""
    sql = """
        SELECT
            rp.prereq_id,
            rp.rationale,
            r.requirement_id as prereq_req_id,
            r.code as prereq_code,
            r.title as prereq_title,
            r.document_id,
            r.section_id
        FROM requirement_prerequisites rp
        JOIN requirements r ON rp.prerequisite_requirement_id = r.requirement_id
        WHERE rp.requirement_id = ?
    """
    return query_all(sql, (requirement_id,))


def add_role_requirement_mapping(
    job_role_id: str,
    requirement_id: str,
    mandatory_for_role: int = 1,
    role_priority: str = "High",
    due_stage: str = "Week 1",
    assessment_required: int = 1,
    practical_task_required: int = 0
) -> str:
    """Insert or update a ground-truth mapping in the Role Requirement Matrix."""
    mapping_id = f"MAP-{job_role_id}-{requirement_id}"
    sql = """
        INSERT INTO role_requirements (
            mapping_id, job_role_id, requirement_id, mandatory_for_role,
            role_priority, due_stage, assessment_required, practical_task_required
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_role_id, requirement_id) DO UPDATE SET
            mandatory_for_role = excluded.mandatory_for_role,
            role_priority = excluded.role_priority,
            due_stage = excluded.due_stage,
            assessment_required = excluded.assessment_required,
            practical_task_required = excluded.practical_task_required
    """
    execute_commit(sql, (
        mapping_id, job_role_id, requirement_id, mandatory_for_role,
        role_priority, due_stage, assessment_required, practical_task_required
    ))
    return mapping_id
