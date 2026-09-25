"""
SkillSprint AI - Policy Update Detection & Impact Analysis Engine
Theme: OnboardVerse | Category: Generative AI PowerPlay

Identifies requirements, modules, tasks, quizzes, and employee onboarding plans
affected when an organizational document or policy version changes.
Prevents ungrounded full rebuilds by pinpointing exact impacted entities.
"""

import uuid
from typing import Any, Dict, List, Optional
from src.database.db import execute_commit, query_all, query_one


def perform_policy_impact_analysis(
    document_id: str,
    old_version: str,
    new_version: str,
    change_summary: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Execute impact analysis when a policy is updated.
    Tracks affected requirements, employee plans, learning modules, and quizzes.
    """
    event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"

    # Record policy change event
    execute_commit(
        """
        INSERT INTO policy_change_events (
            event_id, document_id, old_version_tag, new_version_tag,
            change_summary, detected_by_user_id, impact_analyzed
        ) VALUES (?, ?, ?, ?, ?, ?, 1)
        """,
        (event_id, document_id, old_version, new_version, change_summary, user_id)
    )

    # 1. Identify directly affected requirements
    affected_reqs = query_all(
        "SELECT requirement_id, code, title, section_id FROM requirements WHERE document_id = ?",
        (document_id,)
    )

    # 2. Identify affected learning modules
    affected_modules = query_all(
        """
        SELECT lm.module_id, lm.plan_id, lm.title, lm.source_section_id, op.employee_id
        FROM learning_modules lm
        JOIN onboarding_plans op ON lm.plan_id = op.plan_id
        WHERE lm.source_document_id = ?
        """,
        (document_id,)
    )

    # 3. Identify affected quiz questions
    affected_quizzes = query_all(
        """
        SELECT qq.question_id, qq.quiz_id, q.plan_id, qq.question_text
        FROM quiz_questions qq
        JOIN quizzes q ON qq.quiz_id = q.quiz_id
        WHERE qq.source_document_id = ?
        """,
        (document_id,)
    )

    # 4. Identify affected onboarding plans
    affected_plan_ids = list({m["plan_id"] for m in affected_modules}.union({q["plan_id"] for q in affected_quizzes}))

    # Record impacts in policy_impact_records
    for req in affected_reqs:
        execute_commit(
            """
            INSERT INTO policy_impact_records (
                impact_id, event_id, affected_entity_type, affected_entity_id,
                impact_severity, change_description, regeneration_required
            ) VALUES (?, ?, 'Requirement', ?, 'Modified', ?, 1)
            """,
            (f"IMP-{uuid.uuid4().hex[:8]}", event_id, req["requirement_id"],
             f"Requirement grounded in {document_id} updated from {old_version} to {new_version}")
        )

    for pid in affected_plan_ids:
        # Mark plan status as outdated / review required
        execute_commit(
            "UPDATE onboarding_plans SET status = 'Outdated Policy - Review Required' WHERE plan_id = ?",
            (pid,)
        )
        execute_commit(
            """
            INSERT INTO policy_impact_records (
                impact_id, event_id, affected_entity_type, affected_entity_id,
                impact_severity, change_description, regeneration_required
            ) VALUES (?, ?, 'OnboardingPlan', ?, 'Breaking', ?, 1)
            """,
            (f"IMP-{uuid.uuid4().hex[:8]}", event_id, pid,
             f"Plan contains content citing superseded policy {document_id} {old_version}")
        )

    return {
        "event_id": event_id,
        "document_id": document_id,
        "old_version": old_version,
        "new_version": new_version,
        "change_summary": change_summary,
        "affected_requirements_count": len(affected_reqs),
        "affected_modules_count": len(affected_modules),
        "affected_quizzes_count": len(affected_quizzes),
        "affected_plans_count": len(affected_plan_ids),
        "affected_plan_ids": affected_plan_ids,
        "affected_modules": affected_modules
    }
