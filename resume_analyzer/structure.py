"""
Basic resume structure checks: common section headers, contact info
(email/phone), and word-count sanity bounds.
"""

from __future__ import annotations

import re

# Canonical section name -> header text variants that count as that section
# being present. Matched as whole "header-ish" words/phrases, case-insensitive.
SECTION_KEYWORDS: dict[str, list[str]] = {
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
    ],
    "education": ["education", "academic background"],
    "skills": ["skills", "technical skills", "core competencies"],
    "projects": ["projects", "personal projects"],
    "summary": ["summary", "professional summary", "objective", "profile"],
}

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(
    r"(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"
)

MIN_WORD_COUNT = 150
MAX_WORD_COUNT = 1200


def detect_sections(resume_text: str) -> dict[str, bool]:
    """Return {section_name: found_bool} for each known section keyword."""
    lowered = (resume_text or "").lower()
    result: dict[str, bool] = {}
    for section, variants in SECTION_KEYWORDS.items():
        result[section] = any(
            re.search(r"(?<![\w])" + re.escape(v) + r"(?![\w])", lowered)
            for v in variants
        )
    return result


def missing_sections(resume_text: str) -> list[str]:
    """Return canonical names of sections not found in the resume."""
    sections = detect_sections(resume_text)
    return [name for name, found in sections.items() if not found]


def detect_contact_info(resume_text: str) -> dict[str, bool]:
    """Return {'email': bool, 'phone': bool} for whether contact info was found."""
    text = resume_text or ""
    return {
        "email": bool(EMAIL_REGEX.search(text)),
        "phone": bool(PHONE_REGEX.search(text)),
    }


def word_count(text: str) -> int:
    return len((text or "").split())


def length_issues(resume_text: str) -> list[str]:
    """Return human-readable issues about resume length, if any."""
    count = word_count(resume_text)
    issues: list[str] = []
    if count == 0:
        issues.append("Resume appears to be empty.")
    elif count < MIN_WORD_COUNT:
        issues.append(
            f"Resume is quite short ({count} words); consider expanding on "
            f"experience and skills (aim for at least {MIN_WORD_COUNT})."
        )
    elif count > MAX_WORD_COUNT:
        issues.append(
            f"Resume is quite long ({count} words); consider trimming to "
            f"the most relevant, recent experience (aim for under {MAX_WORD_COUNT})."
        )
    return issues


_METRIC_PATTERN = re.compile(
    r"\d+%|\$\d|\b\d+x\b|\bincreased\b|\bdecreased\b|\breduced\b|\bimproved\b"
    r"|\bgrew\b|\bsaved\b|\bboosted\b|\bcut\b|\bgenerated\b",
    re.IGNORECASE,
)


def has_quantifiable_achievements(resume_text: str) -> bool:
    """Heuristic check for numbers/metrics that suggest quantified impact."""
    return bool(_METRIC_PATTERN.search(resume_text or ""))
