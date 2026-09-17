#!/usr/bin/env python3
"""
AI Resume Analyzer CLI.

Usage:
    python analyze.py resume.txt job.txt

Prints the ATS-style match score and full report to stdout. Pure Python,
no LLM/API calls - all matching is done via a hand-authored skills
taxonomy/alias map and simple structural heuristics.
"""

from __future__ import annotations

import argparse
import sys

from resume_analyzer.loaders import load_text
from resume_analyzer.report import build_report, format_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="ATS-style resume vs job description analyzer."
    )
    parser.add_argument("resume", help="Path to resume file (.txt or .docx)")
    parser.add_argument("job", help="Path to job description file (.txt or .docx)")
    args = parser.parse_args(argv)

    try:
        resume_text = load_text(args.resume)
        job_text = load_text(args.job)
    except (FileNotFoundError, ImportError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report = build_report(resume_text, job_text)
    print(format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
