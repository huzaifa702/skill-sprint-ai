"""
SkillSprint AI - Automated Test Suite: Independent Python Ground Truth Validation
Theme: OnboardVerse | Category: Generative AI PowerPlay
"""

import pytest
from src.python_validation.engine import (
    calculate_jaccard_similarity,
    detect_duplicates,
    run_ground_truth_validation,
    validate_learning_sequence_and_prerequisites,
    validate_mandatory_coverage,
    validate_source_traceability
)


def test_jaccard_similarity_calculation():
    s1 = "All flight telemetry data must be encrypted with AES-256."
    s2 = "Flight telemetry data must be encrypted using AES-256."
    sim = calculate_jaccard_similarity(s1, s2)
    assert sim > 0.70
    assert calculate_jaccard_similarity("completely different", "unrelated text") == 0.0


def test_duplicate_module_detection():
    plan_with_dups = {
        "modules": [
            {"module_id": "M1", "module_title": "Telemetry Encryption", "purpose": "Encrypt flight data with AES-256", "tasks": []},
            {"module_id": "M2", "module_title": "Telemetry Encryption", "purpose": "Encrypt flight data with AES-256", "tasks": []}
        ]
    }
    dup_count, issues = detect_duplicates(plan_with_dups)
    assert dup_count >= 1
    assert any("DUPLICATE_MODULE_DETECTED" in iss.rule_name for iss in issues)


def test_sequence_validator_flags_late_security_basics():
    bad_sequence_plan = {
        "modules": [
            {
                "module_id": "M1",
                "module_title": "Information Security Basics",
                "due_stage": "First 90 Days",
                "learning_objectives": ["Understand security"]
            }
        ]
    }
    issues = validate_learning_sequence_and_prerequisites(bad_sequence_plan)
    assert any("INCORRECT_PREREQUISITE_SEQUENCE" in iss.rule_name for iss in issues)


def test_traceability_flags_obsolete_source_document():
    plan_citing_obsolete = {
        "modules": [
            {
                "module_id": "M1",
                "module_title": "Outdated Policy Training",
                "source_document_id": "POL-SEC-01-V1",
                "source_section_id": "1.1"
            }
        ]
    }
    docs_map = {
        "POL-SEC-01-V1": {"status": "Superseded", "sections": ["1.1"]}
    }
    score, issues = validate_source_traceability(plan_citing_obsolete, docs_map)
    assert score == 0.0
    assert any("OUTDATED_SOURCE_VERSION" in iss.rule_name for iss in issues)


def test_coverage_score_computes_exact_ratio():
    # Test plan with zero coverage
    empty_plan = {"modules": []}
    score, total, covered, issues, comp = validate_mandatory_coverage(empty_plan, "ROLE-FSE")
    assert score == 0.0
    assert total > 0
    assert covered == 0
    assert len(issues) == total
