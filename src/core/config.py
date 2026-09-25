"""
SkillSprint AI - Configuration Management
Theme: OnboardVerse | Category: Generative AI PowerPlay
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
UPLOAD_DIR = BASE_DIR / "sample_documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = os.environ.get("SKILLSPRINT_DB_PATH", str(BASE_DIR / "skillsprint.db"))

# Security
SECRET_KEY = os.environ.get("SKILLSPRINT_SECRET_KEY", "dev-skillsprint-secret-key-change-in-production-2026")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in HTTPS production
PERMANENT_SESSION_LIFETIME_HOURS = 12

# File Upload Settings
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# GenAI Settings
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
DEFAULT_GEMINI_MODEL = os.environ.get("DEFAULT_GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_TEMPERATURE = 0.2
GENAI_REQUEST_TIMEOUT = 30  # seconds
GENAI_MAX_RETRIES = 2

# Validation Thresholds
MANDATORY_COVERAGE_TARGET = 100.0  # Percentage
TRACEABILITY_TARGET = 100.0       # Percentage
CONSISTENCY_THRESHOLD = 90.0      # Percentage

# Policy Precedence Defaults (Rank 1 = Highest Authority)
DEFAULT_POLICY_PRECEDENCE = [
    {"category": "Latest Approved Policy", "rank": 1},
    {"category": "Compliance Directive", "rank": 2},
    {"category": "Department SOP", "rank": 3},
    {"category": "Process Manual", "rank": 4},
    {"category": "Employee Handbook", "rank": 5},
    {"category": "FAQ", "rank": 6},
    {"category": "Informal Guidance", "rank": 7}
]
