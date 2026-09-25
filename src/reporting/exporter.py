"""
SkillSprint AI - Enterprise Reporting & Multi-Format Exporter
Theme: OnboardVerse | Category: Generative AI PowerPlay

Generates structured reports for:
- Employee progress
- Role coverage & compliance
- Mandatory training completion
- Source traceability audits
- Hallucination flags
- GenAI vs Python comparisons
- Manual review decisions

Supports CSV, Excel-compatible CSV, and PDF exports.
"""

import csv
import io
from typing import Any, Dict, List, Optional
from src.database.db import query_all, query_one


def generate_coverage_report() -> List[Dict[str, Any]]:
    """Generate organizational compliance and mandatory coverage report across all roles."""
    sql = """
        SELECT
            jr.role_id,
            jr.title as role_title,
            d.name as department_name,
            COUNT(DISTINCT rm.requirement_id) as total_requirements,
            SUM(CASE WHEN rm.mandatory_for_role = 1 THEN 1 ELSE 0 END) as mandatory_requirements,
            COUNT(DISTINCT e.employee_id) as active_employees
        FROM job_roles jr
        JOIN departments d ON jr.dept_id = d.dept_id
        LEFT JOIN role_requirements rm ON jr.role_id = rm.job_role_id
        LEFT JOIN employees e ON jr.role_id = e.job_role_id
        GROUP BY jr.role_id
        ORDER BY d.name ASC, jr.title ASC
    """
    return query_all(sql)


def generate_employee_progress_report() -> List[Dict[str, Any]]:
    """Generate detailed progress and onboarding health status for all learners."""
    sql = """
        SELECT
            e.employee_id,
            e.first_name || ' ' || e.last_name as full_name,
            e.email,
            jr.title as role_title,
            d.name as department_name,
            e.experience_level,
            e.training_status,
            op.plan_id,
            op.status as plan_status,
            op.verification_status,
            op.coverage_score,
            op.traceability_score,
            (SELECT COUNT(*) FROM learning_modules WHERE plan_id = op.plan_id) as total_modules,
            (SELECT COUNT(*) FROM learning_modules WHERE plan_id = op.plan_id AND status = 'Completed') as completed_modules
        FROM employees e
        JOIN job_roles jr ON e.job_role_id = jr.role_id
        JOIN departments d ON e.dept_id = d.dept_id
        LEFT JOIN onboarding_plans op ON e.employee_id = op.employee_id
        ORDER BY e.created_at DESC
    """
    return query_all(sql)


def export_dict_list_to_csv(data: List[Dict[str, Any]]) -> str:
    """Convert a list of dictionaries into RFC 4180 / Excel-compatible CSV string."""
    if not data:
        return ""
    output = io.StringIO()
    # Write UTF-8 BOM for Microsoft Excel compatibility
    output.write("\ufeff")
    fieldnames = list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return output.getvalue()


def generate_text_audit_report(plan_id: str) -> str:
    """Generate a clean plaintext audit report for printing or PDF rendering."""
    plan = query_one(
        """
        SELECT op.*, e.first_name, e.last_name, jr.title as role_title, d.name as dept_name
        FROM onboarding_plans op
        JOIN employees e ON op.employee_id = e.employee_id
        JOIN job_roles jr ON op.job_role_id = jr.role_id
        JOIN departments d ON e.dept_id = d.dept_id
        WHERE op.plan_id = ?
        """,
        (plan_id,)
    )
    if not plan:
        return "Plan not found."

    lines = [
        "=" * 70,
        "SKILLSPRINT AI - ONBOARDING PLAN & INDEPENDENT VALIDATION AUDIT",
        "=" * 70,
        f"Plan ID: {plan['plan_id']}",
        f"Employee: {plan['first_name']} {plan['last_name']} ({plan['employee_id']})",
        f"Job Role: {plan['role_title']} | Department: {plan['dept_name']}",
        f"Plan Status: {plan['status']} | Verification Status: {plan['verification_status']}",
        "-" * 70,
        "INDEPENDENT VALIDATION METRICS:",
        f"Mandatory Requirement Coverage Score: {plan['coverage_score']:.1f}%",
        f"Source Document Traceability Score:   {plan['traceability_score']:.1f}%",
        f"Total Mandatory Requirements:         {plan['total_mandatory_requirements']}",
        f"Covered Mandatory Requirements:       {plan['covered_mandatory_requirements']}",
        f"Missing Mandatory Requirements:       {plan['missing_mandatory_count']}",
        f"Unsupported Generated Claims:         {plan['unsupported_items_count']}",
        f"Contradiction Count:                  {plan['contradiction_count']}",
        f"Duplicate Learning Items:             {plan['duplicate_items_count']}",
        "=" * 70,
    ]
    return "\n".join(lines)
