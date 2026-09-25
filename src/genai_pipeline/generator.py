"""
SkillSprint AI - Pipeline 1: GenAI Personalized Onboarding Generator
Theme: OnboardVerse | Category: Generative AI PowerPlay

Orchestrates prompt assembly, untrusted data isolation, Gemini API execution,
structured JSON response parsing, and database persistence.
"""

import json
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple
from src.core.config import BASE_DIR, GEMINI_TEMPERATURE
from src.core.security import wrap_untrusted_data
from src.database.db import execute_commit, query_all, query_one
from src.genai_pipeline.client import GenAIError, generate_structured_content
from src.role_matrix.matrix import get_mandatory_requirements_for_role


def load_prompt_template(filename: str) -> str:
    """Load prompt template text from prompt_templates directory."""
    path = os.path.join(BASE_DIR, "prompt_templates", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_generation_context(employee_id: str) -> Dict[str, Any]:
    """Retrieve employee details, ground-truth requirements, and relevant approved document chunks."""
    emp = query_one(
        """
        SELECT e.employee_id, e.first_name, e.last_name, e.email, e.experience_level,
               e.location, e.joining_date, e.previous_experience_years,
               jr.role_id, jr.code as role_code, jr.title as role_title,
               d.dept_id, d.name as dept_name
        FROM employees e
        JOIN job_roles jr ON e.job_role_id = jr.role_id
        JOIN departments d ON e.dept_id = d.dept_id
        WHERE e.employee_id = ?
        """,
        (employee_id,)
    )
    if not emp:
        raise ValueError(f"Employee '{employee_id}' not found.")

    # 1. Fetch Ground Truth Requirements
    mandatory_reqs = get_mandatory_requirements_for_role(emp["role_id"])
    req_context_lines = []
    for r in mandatory_reqs:
        req_context_lines.append(
            f"- [{r['requirement_code']}] {r['requirement_title']}: {r['requirement_description']} "
            f"(Source: {r['document_id']} Sec {r['section_id']}, Priority: {r['role_priority']}, Due: {r['due_stage']})"
        )
    mandatory_context_str = "\n".join(req_context_lines)

    # 2. Fetch Relevant Active Document Chunks (tagged as untrusted data)
    doc_chunks = query_all(
        """
        SELECT dc.chunk_id, dc.document_id, dc.section_number, dc.heading, dc.content
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.document_id
        WHERE d.status = 'Active'
        ORDER BY d.category ASC, dc.chunk_index ASC
        LIMIT 40
        """
    )

    sources_wrapped = []
    for chk in doc_chunks:
        wrapped = wrap_untrusted_data(
            content=chk["content"],
            doc_id=chk["document_id"],
            section=chk["section_number"]
        )
        sources_wrapped.append(
            f"DOCUMENT: {chk['document_id']} | SECTION: {chk['section_number']} | TITLE: {chk['heading']}\n{wrapped}"
        )
    sources_context_str = "\n".join(sources_wrapped)

    return {
        "employee": emp,
        "mandatory_context": mandatory_context_str,
        "sources_context": sources_context_str,
        "mandatory_reqs": mandatory_reqs
    }


def generate_employee_onboarding_plan(
    employee_id: str,
    prompt_version: str = "v1.0"
) -> Tuple[Dict[str, Any], str]:
    """
    Execute Pipeline 1: Assemble prompt, call Gemini, log execution,
    and persist generated structured onboarding plan into SQLite.
    Returns (generated_plan_json, plan_id).
    """
    ctx = build_generation_context(employee_id)
    emp = ctx["employee"]

    sys_template = load_prompt_template("onboarding_system_v1.txt")
    user_template = load_prompt_template("onboarding_generation_v1.txt")

    user_prompt = user_template.format(
        employee_id=emp["employee_id"],
        employee_name=f"{emp['first_name']} {emp['last_name']}",
        job_role_title=emp["role_title"],
        department=emp["dept_name"],
        experience_level=emp["experience_level"],
        previous_experience_years=emp["previous_experience_years"],
        location=emp["location"],
        joining_date=emp["joining_date"],
        mandatory_requirements_context=ctx["mandatory_context"],
        approved_sources_context=ctx["sources_context"]
    )

    log_id = f"LOG-{uuid.uuid4().hex[:12].upper()}"
    plan_id = f"PLAN-{emp['role_code']}-{uuid.uuid4().hex[:8].upper()}"

    try:
        plan_json, latency_ms, retries = generate_structured_content(
            system_instruction=sys_template,
            user_prompt=user_prompt,
            temperature=GEMINI_TEMPERATURE
        )
        status = "SUCCESS"
        error_msg = None
    except GenAIError as ge:
        # Log failure
        execute_commit(
            """
            INSERT INTO generation_logs (
                log_id, employee_id, job_role_id, model_name, api_provider,
                temperature, request_payload_json, latency_ms, status, retry_count, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (log_id, employee_id, emp["role_id"], "gemini-2.5-flash", "Google Gemini API",
             GEMINI_TEMPERATURE, json.dumps({"prompt": user_prompt[:1000]}), 0, "FAILED", ge.retry_count, str(ge))
        )
        raise

    # Log successful generation
    execute_commit(
        """
        INSERT INTO generation_logs (
            log_id, employee_id, job_role_id, model_name, api_provider,
            temperature, request_payload_json, response_json, latency_ms, status, retry_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (log_id, employee_id, emp["role_id"], "gemini-2.5-flash", "Google Gemini API",
         GEMINI_TEMPERATURE, json.dumps({"prompt": user_prompt[:1000]}), json.dumps(plan_json), latency_ms, "SUCCESS", retries)
    )

    # Persist Plan to Database
    plan_json["plan_id"] = plan_id
    title = plan_json.get("plan_title", f"Onboarding Plan: {emp['role_title']}")

    execute_commit(
        """
        INSERT INTO onboarding_plans (
            plan_id, employee_id, job_role_id, plan_version, title, status,
            verification_status, generated_json, generation_log_id
        ) VALUES (?, ?, ?, 1, ?, 'Draft', 'Unverified', ?, ?)
        """,
        (plan_id, employee_id, emp["role_id"], title, json.dumps(plan_json), log_id)
    )

    # Persist Modules, Objectives, Checklists, Tasks, Quizzes
    stage_map = {}
    stage_names = ["Day 1", "Week 1", "Week 2", "First 30 Days", "First 60 Days", "First 90 Days"]
    for idx, s_name in enumerate(stage_names):
        stg_id = f"STG-{plan_id}-{idx+1}"
        execute_commit(
            "INSERT INTO onboarding_stages (stage_id, plan_id, stage_name, sequence_order) VALUES (?, ?, ?, ?)",
            (stg_id, plan_id, s_name, idx + 1)
        )
        stage_map[s_name] = stg_id

    for m_idx, mod in enumerate(plan_json.get("modules", [])):
        mod_id = f"MOD-{plan_id}-{m_idx+1:02d}"
        mod["module_id"] = mod_id
        stage_name = mod.get("due_stage", "Week 1")
        stg_id = stage_map.get(stage_name, list(stage_map.values())[0])

        execute_commit(
            """
            INSERT INTO learning_modules (
                module_id, plan_id, stage_id, module_code, title, purpose, category,
                mandatory, priority, source_document_id, source_section_id,
                estimated_duration_minutes, sequence_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (mod_id, plan_id, stg_id, f"M{m_idx+1:02d}", mod.get("module_title", "Untitled"),
             mod.get("purpose", ""), mod.get("category", "General"), 1 if mod.get("mandatory", True) else 0,
             mod.get("priority", "High"), mod.get("source_document_id", "DOC-01"),
             mod.get("source_section_id", "1.0"), mod.get("estimated_duration_minutes", 60), m_idx + 1)
        )

        # Learning Objectives
        for o_idx, obj in enumerate(mod.get("learning_objectives", [])):
            execute_commit(
                "INSERT INTO learning_objectives (objective_id, module_id, objective_text, sequence_order) VALUES (?, ?, ?, ?)",
                (f"OBJ-{mod_id}-{o_idx+1}", mod_id, str(obj), o_idx + 1)
            )

        # Checklists
        for c_idx, chk in enumerate(mod.get("checklists", [])):
            execute_commit(
                """
                INSERT INTO checklists (
                    checklist_id, plan_id, module_id, activity, is_mandatory, due_stage,
                    responsible_person, source_document_id, source_section_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (f"CHK-{mod_id}-{c_idx+1}", plan_id, mod_id, chk.get("activity", "Activity"),
                 1 if chk.get("is_mandatory", True) else 0, chk.get("due_stage", stage_name),
                 chk.get("responsible_person", "Manager"), mod.get("source_document_id"), mod.get("source_section_id"))
            )

        # Practical Tasks
        for t_idx, tsk in enumerate(mod.get("tasks", [])):
            execute_commit(
                """
                INSERT INTO practical_tasks (
                    task_id, plan_id, module_id, task_code, title, description,
                    expected_outcome, completion_criteria, difficulty, due_stage, is_scenario_based
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (f"TSK-{mod_id}-{t_idx+1}", plan_id, mod_id, tsk.get("task_code", f"T-{t_idx+1}"),
                 tsk.get("title", "Task"), tsk.get("description", ""), tsk.get("expected_outcome", ""),
                 tsk.get("completion_criteria", "Complete successfully"), tsk.get("difficulty", "Intermediate"),
                 tsk.get("due_stage", stage_name), 1 if tsk.get("is_scenario_based") else 0)
            )

        # Quizzes
        quizzes = mod.get("quizzes", [])
        if quizzes:
            q_id = f"QZ-{mod_id}"
            execute_commit(
                "INSERT INTO quizzes (quiz_id, plan_id, module_id, title) VALUES (?, ?, ?, ?)",
                (q_id, plan_id, mod_id, f"Quiz: {mod.get('module_title')}")
            )
            for qn_idx, qn in enumerate(quizzes):
                execute_commit(
                    """
                    INSERT INTO quiz_questions (
                        question_id, quiz_id, question_type, question_text, options_json,
                        correct_answer, explanation, difficulty, source_document_id, source_section_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (f"QQ-{mod_id}-{qn_idx+1}", q_id, qn.get("question_type", "multiple_choice"),
                     qn.get("question_text", "Question"), json.dumps(qn.get("options", [])),
                     qn.get("correct_answer", "A"), qn.get("explanation", ""),
                     qn.get("difficulty", "Intermediate"), qn.get("source_document_id", mod.get("source_document_id")),
                     qn.get("source_section_id", mod.get("source_section_id")))
                )

    return (plan_json, plan_id)
