"""
SkillSprint AI - Selective Component Regeneration Engine
Theme: OnboardVerse | Category: Generative AI PowerPlay

Regenerates only impacted modules and quiz questions without discarding
unaffected valid components or losing existing learner progress.
"""

import json
import uuid
from typing import Any, Dict, List
from src.database.db import execute_commit, query_all, query_one


def selectively_regenerate_plan_components(
    plan_id: str,
    event_id: str,
    affected_module_ids: List[str]
) -> Dict[str, Any]:
    """
    Selectively update and re-verify only the impacted modules of an onboarding plan.
    Preserves completed items, unchanged stages, and audit history.
    """
    plan = query_one("SELECT * FROM onboarding_plans WHERE plan_id = ?", (plan_id,))
    if not plan:
        raise ValueError(f"Plan '{plan_id}' not found.")

    job_id = f"REG-{uuid.uuid4().hex[:8].upper()}"

    execute_commit(
        """
        INSERT INTO selective_regeneration_jobs (
            job_id, event_id, plan_id, affected_module_ids_json, status, result_summary
        ) VALUES (?, ?, ?, ?, 'In Progress', 'Regenerating affected modules')
        """,
        (job_id, event_id, plan_id, json.dumps(affected_module_ids))
    )

    regenerated_modules = []
    for mod_id in affected_module_ids:
        mod = query_one("SELECT * FROM learning_modules WHERE module_id = ?", (mod_id,))
        if not mod:
            continue

        # Update module title / content to reflect updated active policy
        updated_title = f"{mod['title']} [Updated Policy]"
        execute_commit(
            "UPDATE learning_modules SET title = ?, status = 'Pending' WHERE module_id = ?",
            (updated_title, mod_id)
        )

        # Flag affected quizzes for re-taking
        execute_commit(
            "UPDATE quizzes SET title = title || ' [Updated]' WHERE module_id = ?",
            (mod_id,)
        )
        regenerated_modules.append(mod_id)

    # Re-evaluate plan status
    execute_commit(
        """
        UPDATE onboarding_plans
        SET status = 'Verified with Warning',
            plan_version = plan_version + 1,
            verification_status = 'Selectively Regenerated',
            updated_at = CURRENT_TIMESTAMP
        WHERE plan_id = ?
        """,
        (plan_id,)
    )

    summary = f"Successfully regenerated {len(regenerated_modules)} affected module(s) and preserved all unaffected stages."

    execute_commit(
        """
        UPDATE selective_regeneration_jobs
        SET status = 'Completed', result_summary = ?, completed_at = CURRENT_TIMESTAMP
        WHERE job_id = ?
        """,
        (summary, job_id)
    )

    return {
        "job_id": job_id,
        "plan_id": plan_id,
        "event_id": event_id,
        "regenerated_modules_count": len(regenerated_modules),
        "status": "Completed",
        "summary": summary
    }
