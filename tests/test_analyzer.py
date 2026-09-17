"""
Unit tests for the AI Resume Analyzer.

Run with:
    python -m pytest tests/
or:
    python -m unittest discover -s tests
"""

from __future__ import annotations

import unittest

from resume_analyzer.extractor import extract_job_requirements, extract_resume_skills
from resume_analyzer.report import build_report
from resume_analyzer.scorer import calculate_match
from resume_analyzer.structure import (
    detect_contact_info,
    detect_sections,
    missing_sections,
    word_count,
)


class SkillExtractionTests(unittest.TestCase):
    def test_extracts_multiple_skills_from_job_description(self):
        job_text = (
            "We need a Backend Engineer with strong Python and SQL skills, "
            "experience with Docker and AWS, and good communication skills."
        )
        skills = extract_job_requirements(job_text)
        self.assertIn("python", skills)
        self.assertIn("sql", skills)
        self.assertIn("docker", skills)
        self.assertIn("aws", skills)
        self.assertIn("communication", skills)

    def test_no_false_positive_for_unrelated_text(self):
        job_text = "We enjoy hiking, coffee, and quiet mornings at the office."
        skills = extract_job_requirements(job_text)
        self.assertEqual(skills, set())


class AliasSynonymMatchingTests(unittest.TestCase):
    def test_js_alias_matches_javascript_canonical(self):
        resume_text = "Built dashboards using JS and modern ES6 features."
        skills = extract_resume_skills(resume_text)
        self.assertIn("javascript", skills)

    def test_k8s_alias_matches_kubernetes_canonical(self):
        resume_text = "Deployed microservices to k8s clusters in production."
        skills = extract_resume_skills(resume_text)
        self.assertIn("kubernetes", skills)

    def test_short_alias_does_not_match_inside_other_word(self):
        # "r" is an alias for the R language; make sure it doesn't fire on
        # unrelated words like "learning" or "server".
        resume_text = "Experienced with server administration and learning new tools."
        skills = extract_resume_skills(resume_text)
        self.assertNotIn("r", skills)


class MatchScoreTests(unittest.TestCase):
    def test_full_match_scores_100_percent(self):
        job_text = "Looking for a Python developer with SQL and Git experience."
        resume_text = "I have used Python, SQL, and Git extensively in my projects."
        result = calculate_match(resume_text, job_text)
        self.assertEqual(result.required_skills, {"python", "sql", "git"})
        self.assertEqual(result.missing_skills, set())
        self.assertEqual(result.score, 100.0)

    def test_partial_match_scores_and_reports_missing_skills(self):
        job_text = "Need Python, SQL, AWS, and Kubernetes experience."
        resume_text = "I know Python and SQL well."
        result = calculate_match(resume_text, job_text)
        self.assertEqual(result.required_skills, {"python", "sql", "aws", "kubernetes"})
        self.assertEqual(result.matched_skills, {"python", "sql"})
        self.assertEqual(result.missing_skills, {"aws", "kubernetes"})
        self.assertEqual(result.score, 50.0)

    def test_zero_match_when_no_overlap(self):
        job_text = "Need experience with Kubernetes and Terraform."
        resume_text = "I am skilled in painting and gardening."
        result = calculate_match(resume_text, job_text)
        self.assertEqual(result.matched_skills, set())
        self.assertEqual(result.score, 0.0)


class SectionDetectionTests(unittest.TestCase):
    def test_detects_missing_sections(self):
        resume_text = "Skills\nPython, SQL, Git\n"
        missing = missing_sections(resume_text)
        self.assertIn("experience", missing)
        self.assertIn("education", missing)
        self.assertNotIn("skills", missing)

    def test_detects_all_common_sections_when_present(self):
        resume_text = (
            "Summary\nExperienced engineer.\n"
            "Experience\nDid engineering things.\n"
            "Education\nB.S. Computer Science.\n"
            "Skills\nPython, SQL.\n"
            "Projects\nBuilt a thing.\n"
        )
        sections = detect_sections(resume_text)
        self.assertTrue(all(sections.values()))
        self.assertEqual(missing_sections(resume_text), [])


class ContactInfoTests(unittest.TestCase):
    def test_detects_email_and_phone_when_present(self):
        resume_text = "Contact: jane.doe@example.com, (555) 123-4567"
        contact = detect_contact_info(resume_text)
        self.assertTrue(contact["email"])
        self.assertTrue(contact["phone"])

    def test_reports_missing_email_and_phone(self):
        resume_text = "Experienced backend engineer with no contact details listed."
        contact = detect_contact_info(resume_text)
        self.assertFalse(contact["email"])
        self.assertFalse(contact["phone"])


class EdgeCaseTests(unittest.TestCase):
    def test_empty_resume_does_not_crash_and_scores_zero_match(self):
        job_text = "Need Python and SQL skills."
        result = calculate_match("", job_text)
        self.assertEqual(result.matched_skills, set())
        self.assertEqual(result.missing_skills, {"python", "sql"})
        self.assertEqual(result.score, 0.0)

        report = build_report("", job_text)
        self.assertEqual(word_count(""), 0)
        self.assertIn("Resume appears to be empty.", report.length_issues)

    def test_empty_job_description_yields_zero_required_skills(self):
        resume_text = "I know Python, SQL, and Git very well."
        result = calculate_match(resume_text, "")
        self.assertEqual(result.required_skills, set())
        self.assertEqual(result.matched_skills, set())
        self.assertEqual(result.missing_skills, set())
        self.assertEqual(result.score, 0.0)

    def test_both_empty_inputs_do_not_crash(self):
        report = build_report("", "")
        self.assertEqual(report.match.score, 0.0)
        self.assertIsInstance(report.suggestions, list)
        self.assertTrue(len(report.suggestions) > 0)


if __name__ == "__main__":
    unittest.main()
