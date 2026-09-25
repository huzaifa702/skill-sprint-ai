"""
SkillSprint AI - Document Upload & Integrity Validator
Theme: OnboardVerse | Category: Generative AI PowerPlay

Validates file type, size, duplicate status (via SHA-256 hash),
version structure, effective/expiry date consistency, and adversarial prompt content.
"""

import hashlib
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from src.core.config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
from src.core.security import detect_prompt_injection
from src.database.db import query_one

VALID_CATEGORIES = {
    "Policy", "SOP", "Handbook", "FAQ", "Compliance", "Process Manual", "Role Description", "Guidelines"
}


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 checksum of a file for duplicate detection."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_document_upload(
    file_path: str,
    doc_code: str,
    title: str,
    category: str,
    version_tag: str,
    effective_date: Optional[str] = None,
    expiry_date: Optional[str] = None,
    dept_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate uploaded file against enterprise compliance rules.
    Returns status: bool, errors: list, warnings: list, and metadata.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. File existence and size check
    if not os.path.exists(file_path):
        return {"is_valid": False, "errors": ["File does not exist on server."], "warnings": []}

    file_size = os.path.getsize(file_path)
    if file_size == 0:
        errors.append("File is empty (0 bytes).")
    elif file_size > MAX_CONTENT_LENGTH:
        errors.append(f"File exceeds maximum allowed size ({MAX_CONTENT_LENGTH // (1024*1024)}MB).")

    # 2. File extension check
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        errors.append(f"Unsupported file extension '.{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # 3. Document code & title format
    if not doc_code or not re.match(r"^[A-Z0-9\-\_]{3,30}$", doc_code):
        errors.append("Document Code must be 3-30 uppercase alphanumeric characters or hyphens (e.g. POL-SEC-01).")

    if not title or len(title.strip()) < 3:
        errors.append("Document Title must be at least 3 characters long.")

    # 4. Category check
    if category not in VALID_CATEGORIES:
        errors.append(f"Invalid category '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}")

    # 5. Version tag check (e.g., v1.0, v2.1, 1.0)
    if not re.match(r"^v?\d+(\.\d+)*$", version_tag):
        errors.append("Version must be in standard semantic or numbered format (e.g., v1.0, v2.1, 1.0).")

    # 6. Dates consistency
    eff_dt, exp_dt = None, None
    if effective_date:
        try:
            eff_dt = datetime.strptime(effective_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Effective date must be in YYYY-MM-DD format.")

    if expiry_date:
        try:
            exp_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Expiry date must be in YYYY-MM-DD format.")

    if eff_dt and exp_dt and eff_dt > exp_dt:
        errors.append("Effective date cannot be after Expiry date.")

    # 7. Duplicate file content check via SHA-256
    file_hash = calculate_file_hash(file_path)
    existing_hash = query_one(
        "SELECT document_code, title, active_version FROM documents WHERE file_hash = ?",
        (file_hash,)
    )
    if existing_hash:
        warnings.append(
            f"File content is identical to existing document '{existing_hash['document_code']}' "
            f"({existing_hash['title']}, {existing_hash['active_version']})."
        )

    # 8. Check for adversarial injection in text
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            sample_txt = f.read(50000)
            injection_res = detect_prompt_injection(sample_txt)
            if injection_res["is_suspicious"]:
                warnings.append(f"Security Alert: {injection_res['risk_summary']}")
    except Exception:
        pass

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "file_hash": file_hash,
        "file_size": file_size,
        "file_type": ext
    }
