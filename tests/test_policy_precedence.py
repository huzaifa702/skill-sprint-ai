"""
SkillSprint AI - Automated Test Suite: Policy Precedence, Contradictions & Updates
Theme: OnboardVerse | Category: Generative AI PowerPlay
"""

import pytest
from src.contradiction_checks.precedence import check_conflicting_clauses, resolve_precedence
from src.policy_updates.impact_analyzer import perform_policy_impact_analysis
from src.policy_updates.selective_regenerator import selectively_regenerate_plan_components


def test_precedence_resolution_favors_latest_policy_over_faq():
    winner = resolve_precedence("FAQ", "Latest Approved Policy")
    assert winner == "Latest Approved Policy"


def test_precedence_resolution_favors_sop_over_handbook():
    winner = resolve_precedence("Department SOP", "Employee Handbook")
    assert winner == "Department SOP"


def test_contradiction_detector_flags_deprecated_remote_work():
    claim = "Employees may take up to 4 days remote work per week under informal policy."
    conflicts = check_conflicting_clauses(claim, [])
    assert len(conflicts) >= 1
    assert conflicts[0]["higher_precedence_source"] == "Latest Approved Policy"
    assert conflicts[0]["deprecated_source"] == "FAQ"


def test_policy_impact_analysis_identifies_affected_entities():
    res = perform_policy_impact_analysis(
        document_id="DOC-POL-SEC-01",
        old_version="v1.0",
        new_version="v2.0",
        change_summary="Mandatory 7-year telemetry retention",
        user_id="USR-ADMIN-01"
    )
    assert res["affected_requirements_count"] > 0
    assert "event_id" in res
