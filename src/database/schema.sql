-- SkillSprint AI - Enterprise Onboarding Intelligence Database Schema
-- Theme: OnboardVerse | Category: Generative AI PowerPlay
-- Engine: SQLite with Foreign Key Support

PRAGMA foreign_keys = ON;

-- 1. User Roles & System Permissions
CREATE TABLE IF NOT EXISTS system_roles (
    role_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
    permission_id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS system_role_permissions (
    role_id TEXT NOT NULL,
    permission_id TEXT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES system_roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE
);

-- 2. System Users (Admin, Training Manager, Reviewer, Manager, Employee)
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    system_role_id TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    FOREIGN KEY (system_role_id) REFERENCES system_roles(role_id)
);

-- 3. Departments & Organizational Structure
CREATE TABLE IF NOT EXISTS departments (
    dept_id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    head_of_department TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Job Roles (Organizational Competency Profiles)
CREATE TABLE IF NOT EXISTS job_roles (
    role_id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    dept_id TEXT NOT NULL,
    description TEXT,
    experience_level_default TEXT DEFAULT 'Intermediate', -- Beginner, Intermediate, Advanced
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 5. Employee Profiles
CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    job_role_id TEXT NOT NULL,
    dept_id TEXT NOT NULL,
    experience_level TEXT NOT NULL, -- Beginner, Intermediate, Advanced
    location TEXT NOT NULL,
    joining_date DATE NOT NULL,
    reporting_manager TEXT,
    previous_experience_years REAL DEFAULT 0.0,
    training_status TEXT DEFAULT 'On Track', -- On Track, Requires Attention, Behind Schedule, Assessment Required, Completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (job_role_id) REFERENCES job_roles(role_id),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 6. Document Categories & Precedence Hierarchy
CREATE TABLE IF NOT EXISTS policy_precedence_rules (
    precedence_id TEXT PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE, -- e.g., 'Latest Approved Policy', 'Department SOP', 'Compliance Directive', 'FAQ', 'Informal Guidance'
    precedence_rank INTEGER NOT NULL, -- Lower number = higher authoritative precedence (1 = highest)
    description TEXT,
    is_active INTEGER DEFAULT 1
);

-- 7. Organizational Documents & Version Control
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    document_code TEXT NOT NULL UNIQUE, -- e.g., POL-SEC-01, SOP-ENG-03
    title TEXT NOT NULL,
    category TEXT NOT NULL, -- Policy, SOP, Handbook, FAQ, Compliance, Process Manual
    dept_id TEXT,
    file_type TEXT NOT NULL, -- pdf, docx, txt, md
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    file_hash TEXT NOT NULL,
    active_version TEXT NOT NULL,
    effective_date DATE,
    expiry_date DATE,
    status TEXT DEFAULT 'Active', -- Active, Superseded, Obsolete, Draft
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

CREATE TABLE IF NOT EXISTS document_versions (
    version_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    version_tag TEXT NOT NULL, -- e.g., v1.0, v2.0
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    effective_date DATE NOT NULL,
    expiry_date DATE,
    changelog TEXT,
    status TEXT NOT NULL, -- Active, Superseded, Obsolete, Draft
    superseded_by_version TEXT,
    uploaded_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS document_sections (
    section_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    version_tag TEXT NOT NULL,
    section_number TEXT NOT NULL, -- e.g., '1.2', '3.1.4'
    heading TEXT NOT NULL,
    page_reference TEXT, -- e.g., 'Page 4', 'Para 12-15'
    content TEXT NOT NULL,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id TEXT PRIMARY KEY,
    section_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    version_tag TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    heading TEXT NOT NULL,
    source_location TEXT NOT NULL,
    content TEXT NOT NULL,
    token_count_approx INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES document_sections(section_id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

-- 8. Policy & Process Requirements (Independent Ground Truth Extraction)
CREATE TABLE IF NOT EXISTS requirements (
    requirement_id TEXT PRIMARY KEY, -- Stable ID e.g., REQ-POL-SEC-001
    code TEXT NOT NULL UNIQUE,
    document_id TEXT NOT NULL,
    section_id TEXT NOT NULL,
    version_tag TEXT NOT NULL,
    category TEXT NOT NULL, -- Security, Safety, HR, Compliance, Technical SOP, Quality
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    requirement_type TEXT NOT NULL, -- Must Know, Must Complete, Must Demonstrate, Must Acknowledge, Recommended, Optional
    is_mandatory INTEGER NOT NULL DEFAULT 1, -- 1 for mandatory, 0 for optional
    priority TEXT NOT NULL DEFAULT 'High', -- Critical, High, Medium, Low
    compliance_ref TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

-- 9. Role Requirement Matrix (Ground Truth Mapping)
CREATE TABLE IF NOT EXISTS role_requirements (
    mapping_id TEXT PRIMARY KEY,
    job_role_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    mandatory_for_role INTEGER NOT NULL DEFAULT 1,
    role_priority TEXT NOT NULL DEFAULT 'High',
    due_stage TEXT NOT NULL DEFAULT 'Week 1', -- Day 1, Week 1, Week 2, First 30 Days, First 60 Days, First 90 Days
    assessment_required INTEGER DEFAULT 1,
    practical_task_required INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_role_id) REFERENCES job_roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (requirement_id) REFERENCES requirements(requirement_id) ON DELETE CASCADE,
    UNIQUE(job_role_id, requirement_id)
);

-- 10. Requirement Prerequisites (Dependency Graph)
CREATE TABLE IF NOT EXISTS requirement_prerequisites (
    prereq_id TEXT PRIMARY KEY,
    requirement_id TEXT NOT NULL,
    prerequisite_requirement_id TEXT NOT NULL,
    rationale TEXT,
    FOREIGN KEY (requirement_id) REFERENCES requirements(requirement_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_requirement_id) REFERENCES requirements(requirement_id) ON DELETE CASCADE,
    UNIQUE(requirement_id, prerequisite_requirement_id)
);

-- 11. Prompts & Prompt Version Control
CREATE TABLE IF NOT EXISTS prompt_templates (
    template_id TEXT PRIMARY KEY,
    template_name TEXT NOT NULL,
    version_tag TEXT NOT NULL, -- e.g., v1.0, v2.0
    purpose TEXT NOT NULL,
    system_instruction TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,
    expected_schema_name TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_name, version_tag)
);

CREATE TABLE IF NOT EXISTS generation_logs (
    log_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    job_role_id TEXT NOT NULL,
    prompt_template_id TEXT,
    model_name TEXT NOT NULL,
    api_provider TEXT NOT NULL,
    temperature REAL,
    request_payload_json TEXT NOT NULL,
    response_raw_text TEXT,
    response_json TEXT,
    latency_ms INTEGER,
    status TEXT NOT NULL, -- SUCCESS, RETRY, FAILED, TIMEOUT
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (job_role_id) REFERENCES job_roles(role_id)
);

-- 12. Onboarding Plans
CREATE TABLE IF NOT EXISTS onboarding_plans (
    plan_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    job_role_id TEXT NOT NULL,
    plan_version INTEGER DEFAULT 1,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Draft', -- Draft, Verified, Verified with Warning, Incomplete, Unsupported, Contradictory, Manual Review Required, Approved, Active
    verification_status TEXT DEFAULT 'Unverified',
    coverage_score REAL DEFAULT 0.0,
    traceability_score REAL DEFAULT 0.0,
    consistency_score REAL DEFAULT 100.0,
    total_mandatory_requirements INTEGER DEFAULT 0,
    covered_mandatory_requirements INTEGER DEFAULT 0,
    missing_mandatory_count INTEGER DEFAULT 0,
    unsupported_items_count INTEGER DEFAULT 0,
    contradiction_count INTEGER DEFAULT 0,
    duplicate_items_count INTEGER DEFAULT 0,
    generated_json TEXT,
    generation_log_id TEXT,
    created_by TEXT,
    approved_by TEXT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (job_role_id) REFERENCES job_roles(role_id),
    FOREIGN KEY (generation_log_id) REFERENCES generation_logs(log_id)
);

-- 13. Onboarding Stages & Modules
CREATE TABLE IF NOT EXISTS onboarding_stages (
    stage_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    stage_name TEXT NOT NULL, -- Day 1, Week 1, Week 2, First 30 Days, First 60 Days, First 90 Days
    sequence_order INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_modules (
    module_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    stage_id TEXT NOT NULL,
    module_code TEXT NOT NULL, -- e.g., MOD-01
    title TEXT NOT NULL,
    purpose TEXT NOT NULL,
    category TEXT,
    mandatory INTEGER DEFAULT 1,
    priority TEXT DEFAULT 'High',
    source_document_id TEXT NOT NULL,
    source_section_id TEXT NOT NULL,
    estimated_duration_minutes INTEGER DEFAULT 60,
    completion_criteria TEXT,
    sequence_order INTEGER NOT NULL,
    status TEXT DEFAULT 'Pending', -- Pending, In Progress, Completed
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (stage_id) REFERENCES onboarding_stages(stage_id) ON DELETE CASCADE,
    FOREIGN KEY (source_document_id) REFERENCES documents(document_id)
);

CREATE TABLE IF NOT EXISTS learning_objectives (
    objective_id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    objective_text TEXT NOT NULL,
    sequence_order INTEGER NOT NULL,
    FOREIGN KEY (module_id) REFERENCES learning_modules(module_id) ON DELETE CASCADE
);

-- 14. Checklists & Practical Tasks
CREATE TABLE IF NOT EXISTS checklists (
    checklist_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    module_id TEXT,
    activity TEXT NOT NULL,
    is_mandatory INTEGER DEFAULT 1,
    due_stage TEXT NOT NULL,
    responsible_person TEXT,
    source_document_id TEXT,
    source_section_id TEXT,
    is_completed INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES learning_modules(module_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS practical_tasks (
    task_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    task_code TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    expected_outcome TEXT NOT NULL,
    source_requirement_id TEXT,
    completion_criteria TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'Intermediate', -- Beginner, Intermediate, Advanced
    due_stage TEXT NOT NULL,
    is_scenario_based INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Pending', -- Pending, Submitted, Evaluated, Passed, Revision Required
    score REAL,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES learning_modules(module_id) ON DELETE CASCADE,
    FOREIGN KEY (source_requirement_id) REFERENCES requirements(requirement_id)
);

-- 15. Quizzes, Questions & Distractor Grounding
CREATE TABLE IF NOT EXISTS quizzes (
    quiz_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    title TEXT NOT NULL,
    passing_percentage REAL DEFAULT 80.0,
    max_attempts INTEGER DEFAULT 3,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES learning_modules(module_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quiz_questions (
    question_id TEXT PRIMARY KEY,
    quiz_id TEXT NOT NULL,
    question_type TEXT NOT NULL, -- multiple_choice, multiple_response, true_false, scenario_based
    question_text TEXT NOT NULL,
    options_json TEXT NOT NULL, -- JSON array of option objects [{"key":"A","text":"..."},...]
    correct_answer TEXT NOT NULL, -- e.g., 'A' or '["A","C"]'
    explanation TEXT NOT NULL,
    difficulty TEXT DEFAULT 'Intermediate',
    source_document_id TEXT NOT NULL,
    source_section_id TEXT NOT NULL,
    source_verified INTEGER DEFAULT 1,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    FOREIGN KEY (source_document_id) REFERENCES documents(document_id)
);

-- 16. Assessments & Structured Rubrics
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    title TEXT NOT NULL,
    assessment_type TEXT NOT NULL, -- Knowledge, Practical, Scenario, Role-Specific
    description TEXT NOT NULL,
    pass_condition TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES learning_modules(module_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assessment_rubrics (
    rubric_id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    criterion TEXT NOT NULL,
    weight_percentage REAL NOT NULL,
    expected_performance TEXT NOT NULL,
    pass_condition TEXT NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id) ON DELETE CASCADE
);

-- 17. Independent Python Validation Results
CREATE TABLE IF NOT EXISTS validation_results (
    validation_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    status TEXT NOT NULL, -- PASS, WARNING, FAIL
    severity TEXT NOT NULL, -- CRITICAL, HIGH, MEDIUM, LOW, INFO
    target_type TEXT NOT NULL, -- REQUIREMENT, MODULE, TASK, QUIZ, SEQUENCE, SOURCE
    target_id TEXT,
    message TEXT NOT NULL,
    details_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE
);

-- 18. GenAI vs Python Ground Truth Comparison Engine
CREATE TABLE IF NOT EXISTS comparison_results (
    comparison_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    job_role_id TEXT NOT NULL,
    python_expected_text TEXT NOT NULL,
    genai_generated_text TEXT,
    match_status TEXT NOT NULL, -- MATCH, MISMATCH, MISSING_IN_AI, UNSUPPORTED_IN_AI, OUTDATED_SOURCE, CONTRADICTION
    source_document_id TEXT,
    source_section_id TEXT,
    coverage_status TEXT NOT NULL, -- Covered, Uncovered, Partial
    traceability_status TEXT NOT NULL, -- Fully Traceable, Untraceable, Invalid Section
    validation_status TEXT NOT NULL, -- Verified, Warning, Flagged
    disagreement_explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (requirement_id) REFERENCES requirements(requirement_id)
);

-- 19. Manual Review Queue & Reviewer Decisions
CREATE TABLE IF NOT EXISTS manual_reviews (
    review_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    item_type TEXT NOT NULL, -- OnboardingPlan, Module, Task, QuizQuestion, Contradiction, Hallucination
    item_id TEXT NOT NULL,
    flag_reason TEXT NOT NULL, -- Low Coverage, Contradiction Detected, Hallucination Suspected, Disagreement, Malicious Prompt
    severity TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending', -- Pending, In Review, Resolved, Overridden
    assigned_reviewer_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_reviewer_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS reviewer_decisions (
    decision_id TEXT PRIMARY KEY,
    review_id TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    action TEXT NOT NULL, -- Approve, Reject, Edit, Regenerate, Override
    previous_state_json TEXT NOT NULL,
    new_state_json TEXT NOT NULL,
    comments TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES manual_reviews(review_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id)
);

-- 20. Comprehensive Audit Trail
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id TEXT PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    old_value_json TEXT,
    new_value_json TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 21. Policy Change Events & Impact Analysis
CREATE TABLE IF NOT EXISTS policy_change_events (
    event_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    old_version_tag TEXT NOT NULL,
    new_version_tag TEXT NOT NULL,
    change_summary TEXT NOT NULL,
    detected_by_user_id TEXT NOT NULL,
    impact_analyzed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id),
    FOREIGN KEY (detected_by_user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS policy_impact_records (
    impact_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    affected_entity_type TEXT NOT NULL, -- Requirement, Plan, Module, Task, QuizQuestion, Employee
    affected_entity_id TEXT NOT NULL,
    impact_severity TEXT NOT NULL, -- Breaking, Modified, Informational
    change_description TEXT NOT NULL,
    regeneration_required INTEGER DEFAULT 1,
    regeneration_status TEXT DEFAULT 'Pending', -- Pending, Completed, Ignored
    FOREIGN KEY (event_id) REFERENCES policy_change_events(event_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS selective_regeneration_jobs (
    job_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    affected_module_ids_json TEXT NOT NULL, -- JSON array of module IDs
    status TEXT NOT NULL DEFAULT 'Queued', -- Queued, In Progress, Completed, Failed
    result_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES policy_change_events(event_id),
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id)
);

-- 22. Learner Progress Records & Adaptive Recommendations
CREATE TABLE IF NOT EXISTS progress_records (
    record_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    item_type TEXT NOT NULL, -- Module, Checklist, Task, Quiz, Assessment
    item_id TEXT NOT NULL,
    status TEXT NOT NULL, -- Not Started, In Progress, Completed, Failed
    score REAL,
    attempts INTEGER DEFAULT 1,
    time_spent_minutes INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS adaptive_recommendations (
    recommendation_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    trigger_type TEXT NOT NULL, -- Quiz Failure, Task Difficulty, Weak Area, Fast Progress
    trigger_detail TEXT NOT NULL,
    recommended_action TEXT NOT NULL, -- Revision Module, Additional Quiz, Additional Task, Advanced Module, Manager Review
    action_detail TEXT NOT NULL,
    status TEXT DEFAULT 'Proposed', -- Proposed, Accepted, Dismissed, Completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES onboarding_plans(plan_id) ON DELETE CASCADE
);

-- Indexes for Speed, Scalability, and Efficient Querying
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_employees_role ON employees(job_role_id);
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(dept_id);
CREATE INDEX IF NOT EXISTS idx_docs_code ON documents(document_code);
CREATE INDEX IF NOT EXISTS idx_docs_cat ON documents(category);
CREATE INDEX IF NOT EXISTS idx_doc_chunks_doc ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_requirements_doc ON requirements(document_id);
CREATE INDEX IF NOT EXISTS idx_role_reqs_role ON role_requirements(job_role_id);
CREATE INDEX IF NOT EXISTS idx_role_reqs_req ON role_requirements(requirement_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_plans_emp ON onboarding_plans(employee_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_plans_status ON onboarding_plans(status);
CREATE INDEX IF NOT EXISTS idx_validation_results_plan ON validation_results(plan_id);
CREATE INDEX IF NOT EXISTS idx_comparison_results_plan ON comparison_results(plan_id);
CREATE INDEX IF NOT EXISTS idx_progress_records_emp ON progress_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_name, entity_id);
