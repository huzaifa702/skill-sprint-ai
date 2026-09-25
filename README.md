# SkillSprint AI — Enterprise Onboarding & Training Intelligence Platform

**Competition Theme:** OnboardVerse  
**Category:** Generative AI PowerPlay  
**Target Specification:** SkillSprint AI Software Requirements Specification (SRS) Version 1.0  
**Built With:** Python 3.11, Flask, SQLite, Google Gemini API, Vanilla HTML5/CSS3/JavaScript  

---

## 1. Executive Summary & Problem Definition

Traditional enterprise onboarding requires HR teams, trainers, and department leads to manually sift through dozens of complex policy documents, SOPs, safety directives, and process manuals. This manual process causes:
- **Inconsistent role preparation:** Generic training paths that fail to address role-specific safety or technical requirements.
- **Compliance gaps:** Critical mandatory requirements omitted from training schedules.
- **Stale curricula:** Onboarding materials become outdated whenever organizational policies change.
- **Untrusted GenAI risks:** Unverified LLM outputs containing hallucinations, obsolete policies, or vulnerability to adversarial prompt injections.

**SkillSprint AI** introduces a **Dual-Pipeline Architecture**:
1. **Pipeline 1 — GenAI Generation Pipeline (Google Gemini API):** Analyzes relevant approved organizational documents and employee profiles to synthesize personalized, role-specific, multi-stage onboarding plans returned in structured RFC 8259 JSON.
2. **Pipeline 2 — Independent Python Ground-Truth Validation Pipeline:** An isolated deterministic Python rule engine that verifies the AI output against an independent **Role Requirement Matrix**, calculates coverage and traceability scores, detects contradictions, identifies ungrounded claims, and enforces learning sequence rules **without using GenAI to validate itself**.

---

## 2. Core Architecture & Pipeline Flow

```
ORGANIZATIONAL DOCUMENTS (PDF / DOCX)
        │
        ▼
[ Document Upload & SHA-256 Validation ]
        │
        ▼
[ Document Parsing (PyPDF & OpenXML) ] ──► [ Traceable Chunking with Chunk IDs ]
        │                                                     │
        ▼                                                     ▼
[ Deterministic Requirement Extraction ] ──► [ Role Requirement Matrix (Ground Truth) ]
        │                                                     │
        ▼                                                     │
[ Prompt Assembly & Untrusted Data Isolation ]                │
        │                                                     │
        ▼                                                     │
[ PIPELINE 1: Google Gemini API Generation ]                  │
        │                                                     │
        ▼                                                     │
[ Structured JSON Schema Validation ]                         │
        │                                                     │
        ▼                                                     ▼
[ PIPELINE 2: Independent Python Ground-Truth Validation Engine ]
        ├── 1. Mandatory Coverage Score Calculation
        ├── 2. Source Traceability & Version Verification
        ├── 3. Hallucination & Unsupported Claim Detection
        ├── 4. Policy Precedence & Contradiction Resolution
        ├── 5. Duplicate Learning Item Detection
        └── 6. Prerequisite & Sequence Order Checking
        │
        ▼
[ Side-by-Side Dual-Pipeline Comparison Workspace ]
        │
        ▼
[ Human Review Queue & Reviewer Override (Audit Trail) ]
        │
        ▼
[ Final Verified Multi-Stage Onboarding Plan ]
```

---

## 3. Technology Stack & Minimalist Engineering

In strict compliance with SRS Section 3 and 4, dependencies are strictly kept minimal, robust, and fully explainable:
- **Backend:** Python 3.11, Flask 3.1, Werkzeug
- **Database:** SQLite (Direct SQL with WAL journal mode, parameterized execution, foreign key cascades, and indexing)
- **Generative AI:** Google Gemini API (`google-genai` SDK with fallback HTTP client)
- **Document Processing:** `pypdf` for PDF parsing; native Python OpenXML parser (`zipfile` + `xml.etree.ElementTree`) and `python-docx` for DOCX
- **Validation Engine:** Independent deterministic Python rule engine, regex parsers, and Jaccard token similarity
- **Frontend:** Vanilla HTML5, modern CSS3 with 3D perspective layers, Vanilla JavaScript (Zero bloated frameworks like React, Next.js, or Tailwind)
- **Reporting & Export:** RFC 4180 / Excel-compatible CSV generator, ReportLab / plaintext audit format
- **Testing:** `pytest` (21 automated test cases, 100% pass rate)

---

## 4. Fictional Enterprise Dataset: AeroPulse Technologies

To satisfy SRS Section 11–14, a completely original aerospace and autonomous robotics company was created:
- **Company Name:** AeroPulse Avionics & Autonomous Systems Inc.
- **Industry:** Industrial UAVs, Avionics Flight Software, Mission Control & Defense Logistics
- **10 Distinct Departments:** Flight Software, Avionics Hardware, QA & Flight Testing, Mission Control, Regulatory Airworthiness, Cyber Defense, Field Operations, Defense Procurement, HR, Aviation Safety
- **10 Distinct Job Roles:**
  1. Flight Software Engineer (`ROLE-FSE`)
  2. Avionics QA & Test Technician (`ROLE-QAT`)
  3. Mission Control Operations Specialist (`ROLE-MCO`)
  4. Airworthiness Compliance Analyst (`ROLE-ACA`)
  5. Cyber Security Operations Analyst (`ROLE-SEC`)
  6. Field Deployment Engineer (`ROLE-FDE`)
  7. Hardware Assembly Specialist (`ROLE-HAS`)
  8. Customer Mission Support Lead (`ROLE-CSL`)
  9. Defense Procurement Specialist (`ROLE-DPS`)
  10. Aviation Safety & Training Officer (`ROLE-AST`)
- **22 Physical Documents:** Valid binary PDF and DOCX files in `sample_documents/` covering policies, SOPs, handbooks, FAQs, legacy versions, and adversarial test documents.
- **165 Identifiable Requirements:** 116 mandatory, 49 optional/recommended, with 207 role-mapped ground-truth requirements and 5 prerequisite dependency chains.

---

## 5. Prerequisites & Installation

### Prerequisites
- Python 3.10+ (Tested on Python 3.11.15)
- Git

### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/your-username/skill-sprint-ai.git
cd skill-sprint-ai

# 2. Create virtual environment
python -m venv venv

# Windows activate:
.\venv\Scripts\Activate.ps1
# Linux/macOS activate:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY (optional for local mock/offline mode)
```

---

## 6. Database Setup & Sample Document Generation

To initialize the SQLite database, populate all 10 roles, seed 165 requirements, and build the physical PDF and DOCX documents:

```bash
# Set PYTHONPATH to project root
# Windows PowerShell:
$env:PYTHONPATH="."
# Linux/macOS:
export PYTHONPATH="."

# Generate physical sample documents (PDF & DOCX)
python scripts/generate_sample_documents.py

# Initialize and seed database
python -m src.database.seed_data

# (Optional) Pre-generate verified onboarding plans for all 10 roles
python scripts/generate_all_role_plans.py
```

---

## 7. Starting the Application

```bash
python app.py
```
Open your browser and navigate to:  
**`http://127.0.0.1:5000`**

---

## 8. Role-Based User Accounts (Evaluator Quick Logins)

The application supports 5 distinct RBAC roles. Use the 1-click login buttons on the login page or enter credentials manually:

| Role | Username | Password | Purpose |
|:---|:---|:---|:---|
| **Administrator** | `admin` | `Admin@12345!` | Full system administration, RBAC, document management |
| **Training Manager** | `training_mgr` | `Train@12345!` | Role requirement matrix, curricula, learning paths |
| **Reviewer** | `reviewer` | `Review@12345!` | Audit queue, manual reviewer overrides, conflict resolution |
| **Manager** | `manager` | `Manage@12345!` | Department oversight, employee onboarding health |
| **Employee** | `employee` | `Employ@12345!` | Learner experience, modules, checklists, quizzes |

---

## 9. Step-by-Step Evaluator Workflow

### Step 1: Document Upload & Ingestion
1. Navigate to **Documents** (`/documents`).
2. Click **+ Upload Document**. Select a `.pdf` or `.docx` file.
3. System automatically calculates SHA-256 hash (duplicate detection), extracts sections/headings, and generates traceable chunk IDs.
4. Click **Inspect Sections** on any document to view extracted paragraphs and page citations.

### Step 2: Role Requirement Matrix (Ground Truth)
1. Navigate to **Requirement Matrix** (`/matrix`).
2. Filter by any of the 10 job roles (e.g., `Flight Software Engineer` vs. `Customer Mission Support Lead`).
3. Notice how different roles receive distinct mandatory policies, due stages, priorities, and source citations.
4. Click **Export Matrix (CSV)** to download the audit spreadsheet.

### Step 3: Dual-Pipeline Personalized Onboarding Generation
1. Navigate to **Learners** (`/employees`).
2. Select an employee (e.g. `Alex Chen`, Flight Software Engineer) and click **Generate Plan**.
3. Inspect the learner context and mandatory ground truth requirements.
4. Click **⚡ Generate & Independently Verify Onboarding Plan**.
5. Watch the **Live Stepper** execute each real backend step:
   - Untrusted data encapsulation
   - Gemini API generation
   - JSON schema validation
   - Independent Python Ground-Truth validation
   - Comparison matrix generation
   - Persistence & Verification Status

### Step 4: Plan Explorer & Multi-Stage Timeline
1. Inspect the resulting multi-stage plan (`/onboarding/plan/<plan_id>`).
2. Browse stages: `Day 1`, `Week 1`, `Week 2`, `First 30 Days`, `First 60 Days`, `First 90 Days`.
3. Verify that every mandatory module cites an approved document and section ID.
4. Inspect practical tasks, checklists, and grounded quizzes.

### Step 5: Side-by-Side Dual-Pipeline Comparison
1. Click **Side-by-Side Verification Audit** (`/onboarding/plan/<plan_id>/comparison`).
2. Compare Python Expected Ground Truth (left column) against GenAI Output (right column).
3. View color-coded match status: `MATCH` (Green), `MISSING IN AI` (Amber), `OUTDATED` (Red), `CONTRADICTION` (Red).
4. Click **Export Comparison (CSV)**.

### Step 6: Human Review Queue & Reviewer Override
1. Navigate to **Review Queue** (`/review-queue`).
2. Inspect flagged items (plans with warnings, contradictions, or missing mandatory items).
3. Enter reviewer comments and execute **Approve (Override)**, **Regenerate**, or **Reject**.
4. Full audit trail is immutably recorded in `audit_logs` and `reviewer_decisions`.

### Step 7: Security & Adversarial Defense Console
1. Navigate to **Security & Defenses** (`/security-tests`).
2. Run live verification checks for:
   - Direct prompt injection in uploaded document text
   - Fake administrator command override
   - Unsupported hidden topic request (refusal & flag)
   - Obsolete/superseded document citation rejection
   - Conflicting policy precedence resolution

---

## 10. Automated Testing & Verification

Run the full pytest suite:
```bash
# Windows PowerShell:
$env:PYTHONPATH="."
pytest -v

# Output:
# 21 passed in 1.66s (100% pass rate)
```

Test Coverage Includes:
- `test_document_processing.py`: PDF & DOCX parsing, chunking, upload validation.
- `test_python_validation.py`: Coverage score, traceability score, duplicate detection, sequencing, prerequisites.
- `test_security_defenses.py`: Prompt injection signatures, untrusted data wrapper, password hashing.
- `test_policy_precedence.py`: 7-tier precedence hierarchy, contradiction detection, impact analysis.
- `test_auth_rbac.py`: Protected routes, session handling, RBAC role restrictions.

---

## 11. Security & Compliance Implementation

1. **Prompt Injection Defense:** Document content is strictly isolated within `<<<UNTRUSTED_DOCUMENT_DATA>>>` envelopes with explicit system directives. Document instructions can never override application rules or modify scoring.
2. **Deterministic Ground Truth:** Python validation rules run independently in native runtime. The GenAI model is never used to validate itself.
3. **Zero Plaintext Passwords:** Cryptographic password hashing using PBKDF2-HMAC-SHA256 with 120,000 iterations and unique 16-byte salts.
4. **Zero Hardcoded Secrets:** All secrets, keys, and tokens are read exclusively from environment variables or `.env`. `.env.example` contains placeholder tokens only.
5. **Audit Logging:** Every administrative action, reviewer override, and generation attempt is timestamped and recorded in `audit_logs`.

---

## 12. Deliverable Documentation Artifacts

- **`AI_USAGE.md`**: Complete AI tool usage declaration matching SRS Section 1.10.17.
- **`documentation/PROJECT_REPORT.md`**: 100+ section project report with architectural diagrams and specifications.
- **`documentation/VALIDATION_REPORT.md`**: Validation evidence report across all 10 roles.
- **`documentation/SECURITY_TESTING_REPORT.md`**: Adversarial test cases and security audit evidence.
- **`documentation/TECHNICAL_BLOG.md`**: 2,000+ word engineering blog post.
- **`reports/BATCH_ONBOARDING_EVIDENCE_SUMMARY.json`**: Pre-computed comparison results covering 207 requirement-level evaluations.

---

## 13. License
Apache License 2.0. Copyright (c) 2026 AeroPulse Technologies & SkillSprint AI Team.
