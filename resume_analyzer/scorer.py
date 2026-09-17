"""
Match-score calculation: how well a resume's extracted skills cover the
skills required by a job description.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .extractor import extract_job_requirements, extract_resume_skills


@dataclass
class MatchResult:
    required_skills: set[str] = field(default_factory=set)
    matched_skills: set[str] = field(default_factory=set)
    missing_skills: set[str] = field(default_factory=set)
    score: float = 0.0

    @property
    def matched_count(self) -> int:
        return len(self.matched_skills)

    @property
    def required_count(self) -> int:
        return len(self.required_skills)


def calculate_match(resume_text: str, job_text: str) -> MatchResult:
    """
    Compare skills mentioned in the job description against skills found in
    the resume and compute a percentage match score.

    Score = (# required skills also found in resume) / (# required skills) * 100

    If the job description contains no recognizable skills, the score is
    defined as 0.0 (there is nothing to measure a match against), and both
    matched/missing sets are empty.
    """
    required = extract_job_requirements(job_text)
    found_in_resume = extract_resume_skills(resume_text)

    if not required:
        return MatchResult(required_skills=set(), matched_skills=set(), missing_skills=set(), score=0.0)

    matched = required & found_in_resume
    missing = required - found_in_resume
    score = round((len(matched) / len(required)) * 100, 2)

    return MatchResult(
        required_skills=required,
        matched_skills=matched,
        missing_skills=missing,
        score=score,
    )
