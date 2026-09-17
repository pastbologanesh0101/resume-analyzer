"""
Keyword / skill extraction utilities.

Extraction is done with word-boundary-aware regular expressions built from
the alias map in `skills.py`, rather than any statistical NLP or LLM call.
Each alias (which may be multi-word, e.g. "problem solving", or contain
punctuation, e.g. "c++"/"node.js") is compiled into a regex pattern with
appropriate boundaries so that short aliases like "js", "r", or "go" do not
match inside unrelated words (e.g. "js" will not match inside "jsonify").
"""

from __future__ import annotations

import re

from .skills import ALIAS_LOOKUP, SKILLS_TAXONOMY

# Aliases built from "word" characters get a strict \b...\b boundary.
# Aliases that contain non-word characters (c++, node.js, c#, ci/cd, k8s-ish)
# get a lookaround boundary based on adjacent whitespace/punctuation instead,
# since \b does not behave usefully around symbols like "+" or "#".
_WORD_ALIAS_RE = re.compile(r"^[\w\s-]+$")


def _compile_alias_pattern(alias: str) -> re.Pattern:
    escaped = re.escape(alias.lower())
    # Allow the escaped multi-word alias's internal spaces to also match
    # runs of whitespace/hyphen (already literal after escape; fine as-is).
    if _WORD_ALIAS_RE.match(alias):
        pattern = r"(?<![\w])" + escaped + r"(?![\w])"
    else:
        pattern = r"(?<![^\W_])" + escaped + r"(?![^\W_])"
    return re.compile(pattern, re.IGNORECASE)


_ALIAS_PATTERNS: dict[str, re.Pattern] = {
    alias: _compile_alias_pattern(alias) for alias in ALIAS_LOOKUP
}


def extract_skills_from_text(
    text: str, taxonomy: dict[str, list[str]] | None = None
) -> set[str]:
    """
    Scan `text` for any alias belonging to any canonical skill in the
    taxonomy and return the set of canonical skill names found.

    Matching is case-insensitive and uses simple boundary rules so that,
    e.g., "JS" and "javascript" both resolve to the canonical skill
    "javascript" (alias/synonym awareness), and short aliases don't produce
    false positives inside longer unrelated words.
    """
    if not text:
        return set()

    found: set[str] = set()
    lowered = text.lower()

    lookup = ALIAS_LOOKUP if taxonomy is None else _build_lookup_for(taxonomy)
    patterns = _ALIAS_PATTERNS if taxonomy is None else {
        alias: _compile_alias_pattern(alias) for alias in lookup
    }

    for alias, canonical in lookup.items():
        pattern = patterns[alias]
        if pattern.search(lowered):
            found.add(canonical)

    return found


def _build_lookup_for(taxonomy: dict[str, list[str]]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for canonical, aliases in taxonomy.items():
        for alias in aliases:
            lookup[alias.lower()] = canonical
        lookup[canonical.lower()] = canonical
    return lookup


def extract_job_requirements(job_text: str) -> set[str]:
    """Extract the set of canonical skills mentioned in a job description."""
    return extract_skills_from_text(job_text, SKILLS_TAXONOMY)


def extract_resume_skills(resume_text: str) -> set[str]:
    """Extract the set of canonical skills mentioned in a resume."""
    return extract_skills_from_text(resume_text, SKILLS_TAXONOMY)
