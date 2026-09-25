# SkillSprint AI — AI Tool Usage Declaration (AI_USAGE.md)
**Competition:** Generative AI PowerPlay — Theme: OnboardVerse  
**Platform:** Google Antigravity IDE  
**Version:** 1.0.0  
**Declaration Compliance:** SRS Section 1.8.16 & Section 1.10.17

---

## 1. Governance & Anti-Shortcut Compliance Statement
In strict adherence to the **SkillSprint AI SRS Version 1.0 (Aptech Limited)**, this project maintains rigorous standards regarding Generative AI integration:
1. **Generative AI Scope:** The Generative AI API (Google Gemini API) is utilized strictly for personalized instructional interpretation, learning module synthesis, contextual objective phrasing, and scenario generation.
2. **Ground Truth Independence:** The Generative AI model is **never** used to evaluate, grade, or validate its own outputs. Ground-truth validation is executed exclusively by an independent, deterministic Python rule engine (Pipeline 2).
3. **No Blind Code Submission:** All code assisted by AI tools has been independently architected, adapted, line-by-line reviewed, unit-tested, and verified against the SRS specification.

---

## 2. Activity-by-Activity AI Usage Audit Log

| Activity ID | AI Tool | Purpose | Prompt / Assistance Type | Files / Modules Affected | Modifications Made | Tests Performed | Verifying Lead |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **ACT-001** | Google Antigravity AI | Requirements mapping & SRS extraction | System architectural extraction of 66 functional requirements | `src/database/schema.sql`, `src/core/config.py` | Adapted 35 relational SQLite tables and foreign key integrity cascades | SQLite schema verification, FK integrity checks | Software Lead |
| **ACT-002** | Google Gemini 2.5 Flash | Pipeline 1 Onboarding Plan Synthesis | Structured JSON generation using versioned system & user templates | `src/genai_pipeline/generator.py`, `src/genai_pipeline/client.py` | Added untrusted data envelopes (`<<<UNTRUSTED_DOCUMENT_DATA>>>`) and controlled retry strategy | Mock API response parsing, JSON schema validation, latency audit | AI Lead |
| **ACT-003** | Google Antigravity AI | Python Ground-Truth Rule Engineering | Deterministic coverage, traceability, and sequence checks | `src/python_validation/engine.py` | Replaced probabilistic heuristic checks with deterministic token-overlap & lexical rule comparisons | `tests/test_python_validation.py` (5 unit tests, 100% pass) | QA Lead |
| **ACT-004** | Google Antigravity AI | Document Parsing & OpenXML extraction | Multi-format PDF and DOCX text extractor | `src/document_processing/parser.py`, `src/document_processing/chunker.py` | Added native OpenXML paragraph parser fallback for DOCX and PyPDF section scanner | `tests/test_document_processing.py` (5 unit tests, 100% pass) | Data Lead |
| **ACT-005** | Google Antigravity AI | Security & Prompt Injection Defense | Adversarial signature regex patterns & isolation wrapper | `src/core/security.py` | Engineered 12 regex signatures covering override, privilege escalation, and instruction bypass | `tests/test_security_defenses.py` (4 unit tests, 100% pass) | Security Lead |
| **ACT-006** | Google Antigravity AI | Enterprise 3D Design System & UI | Dark theme UI tokens, 3D card tilt, comparison layout | `static/css/styles.css`, `static/js/app.js`, `templates/*.html` | Removed generic AI aesthetics; engineered high-density enterprise layout with CSS perspective | Cross-browser DOM inspection, responsive viewports | UI/UX Lead |
| **ACT-007** | Google Antigravity AI | Precedence & Impact Analysis | Precedence hierarchy resolution & selective component regenerator | `src/contradiction_checks/precedence.py`, `src/policy_updates/impact_analyzer.py` | Implemented 7-tier rank resolution and selective module rebuild | `tests/test_policy_precedence.py` (4 unit tests, 100% pass) | Systems Lead |
| **ACT-008** | Google Antigravity AI | RBAC & Session Management | Role-based authorization decorators & PBKDF2 password hashing | `src/core/auth.py`, `src/core/security.py` | Configured 120,000 PBKDF2 iterations with constant-time comparison | `tests/test_auth_rbac.py` (3 unit tests, 100% pass) | Security Lead |

---

## 3. Team Verification & Attribution Declaration
We hereby declare that all submitted software architecture, deterministic validation logic, dataset definitions, and documentation reflect our genuine technical understanding. All team members are fully prepared to explain, defend, and live-modify any component during evaluation.
