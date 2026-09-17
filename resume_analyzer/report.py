"""
Builds and formats the full analysis report combining skill match score,
structural checks, and actionable suggestions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .scorer import MatchResult, calculate_match
from .structure import (
    detect_contact_info,
    has_quantifiable_achievements,
    length_issues,
    missing_sections,
    word_count,
)


@dataclass
class AnalysisReport:
    match: MatchResult
    missing_sections: list[str] = field(default_factory=list)
    contact_info: dict[str, bool] = field(default_factory=dict)
    length_issues: list[str] = field(default_factory=list)
    has_quantifiable_achievements: bool = False
    resume_word_count: int = 0
    suggestions: list[str] = field(default_factory=list)


def build_report(resume_text: str, job_text: str) -> AnalysisReport:
    match = calculate_match(resume_text, job_text)
    missing = missing_sections(resume_text)
    contact = detect_contact_info(resume_text)
    length_probs = length_issues(resume_text)
    has_metrics = has_quantifiable_achievements(resume_text)
    wc = word_count(resume_text)

    suggestions: list[str] = []

    if match.required_count == 0:
        suggestions.append(
            "No recognizable skills/keywords were found in the job description; "
            "add specific technologies, tools, or competencies to the job text."
        )
    elif match.missing_skills:
        missing_list = ", ".join(sorted(match.missing_skills))
        suggestions.append(
            f"Missing skills relative to the job description: {missing_list}. "
            "If you genuinely have this experience, add it explicitly."
        )

    if not has_metrics:
        suggestions.append(
            "Add quantifiable achievements (numbers, percentages, or metrics, "
            "e.g. 'reduced load time by 30%') to strengthen impact."
        )

    for section in missing:
        suggestions.append(
            f"Resume section '{section.title()}' not found; consider adding it."
        )

    if not contact.get("email"):
        suggestions.append("No email address detected; add contact info near the top of the resume.")
    if not contact.get("phone"):
        suggestions.append("No phone number detected; add contact info near the top of the resume.")

    suggestions.extend(length_probs)

    return AnalysisReport(
        match=match,
        missing_sections=missing,
        contact_info=contact,
        length_issues=length_probs,
        has_quantifiable_achievements=has_metrics,
        resume_word_count=wc,
        suggestions=suggestions,
    )


def format_report(report: AnalysisReport) -> str:
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("AI RESUME ANALYZER - REPORT")
    lines.append("=" * 60)
    lines.append(f"Match Score: {report.match.score}%")
    lines.append(
        f"Matched {report.match.matched_count} / {report.match.required_count} "
        "required skills from the job description"
    )
    lines.append("")

    lines.append("Matched Skills:")
    if report.match.matched_skills:
        for skill in sorted(report.match.matched_skills):
            lines.append(f"  [x] {skill}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append("Missing Skills:")
    if report.match.missing_skills:
        for skill in sorted(report.match.missing_skills):
            lines.append(f"  [ ] {skill}")
    else:
        lines.append("  (none)")
    lines.append("")

    lines.append(f"Resume word count: {report.resume_word_count}")
    lines.append(f"Contact info found - email: {report.contact_info.get('email', False)}, "
                  f"phone: {report.contact_info.get('phone', False)}")
    lines.append(f"Quantifiable achievements detected: {report.has_quantifiable_achievements}")
    lines.append("")

    lines.append("Suggestions:")
    if report.suggestions:
        for suggestion in report.suggestions:
            lines.append(f"  - {suggestion}")
    else:
        lines.append("  - Looks good! No major issues detected.")
    lines.append("=" * 60)

    return "\n".join(lines)
