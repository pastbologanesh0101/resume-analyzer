"""
Skills taxonomy for the AI Resume Analyzer.

This module hand-authors a small dictionary mapping a canonical skill name
to a list of aliases/synonyms that should count as a match for that skill
(e.g. "js" or "es6" should count as a match for "javascript"). This is the
"simple alias map" used for lightweight stemming/synonym awareness without
any external NLP dependency or LLM call.

Extend SKILLS_TAXONOMY freely; the rest of the analyzer only depends on the
canonical-name -> alias-list shape.
"""

from __future__ import annotations

SKILLS_TAXONOMY: dict[str, list[str]] = {
    # --- Programming languages ---
    "python": ["python", "py"],
    "javascript": ["javascript", "js", "es6", "es2015", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", "c sharp"],
    "go": ["golang", "go lang"],
    "ruby": ["ruby"],
    "php": ["php"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "t-sql", "pl/sql"],
    "r": ["r programming", "r language"],
    "swift": ["swift"],
    "kotlin": ["kotlin"],

    # --- Web / frontend ---
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss"],
    "react": ["react", "reactjs", "react.js"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vuejs", "vue.js"],
    "node.js": ["node", "nodejs", "node.js"],
    "rest api": ["rest api", "restful api", "rest", "restful"],
    "graphql": ["graphql"],

    # --- Data / ML ---
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl", "neural networks"],
    "data analysis": ["data analysis", "data analytics", "data analytic"],
    "data visualization": ["data visualization", "data viz"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "nlp": ["nlp", "natural language processing"],
    "statistics": ["statistics", "statistical analysis"],
    "excel": ["excel", "microsoft excel", "spreadsheets"],

    # --- Cloud / DevOps ---
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker", "containerization", "containers"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment", "cicd"],
    "linux": ["linux", "unix"],
    "git": ["git", "github", "gitlab", "version control"],
    "terraform": ["terraform", "infrastructure as code", "iac"],

    # --- Databases ---
    "mongodb": ["mongodb", "mongo"],
    "nosql": ["nosql"],
    "redis": ["redis"],

    # --- Project / process ---
    "agile": ["agile", "scrum", "kanban", "sprint planning"],
    "project management": ["project management", "pm"],
    "jira": ["jira"],

    # --- Soft skills ---
    "communication": ["communication", "communicate", "communicating", "verbal communication"],
    "leadership": ["leadership", "lead", "leading", "team lead"],
    "teamwork": ["teamwork", "team player", "collaboration", "collaborative", "cross-functional"],
    "problem solving": ["problem solving", "problem-solving", "analytical skills", "critical thinking"],
    "time management": ["time management", "prioritization", "prioritize"],
    "adaptability": ["adaptability", "adaptable", "flexibility"],
    "attention to detail": ["attention to detail", "detail-oriented", "detail oriented"],
    "mentoring": ["mentoring", "mentorship", "coaching"],
    "presentation": ["presentation", "presenting", "public speaking"],
    "customer service": ["customer service", "client service", "customer support"],
}


def build_alias_lookup(taxonomy: dict[str, list[str]] = SKILLS_TAXONOMY) -> dict[str, str]:
    """Return a reverse lookup: lowercase alias text -> canonical skill name."""
    lookup: dict[str, str] = {}
    for canonical, aliases in taxonomy.items():
        for alias in aliases:
            lookup[alias.lower()] = canonical
        lookup[canonical.lower()] = canonical
    return lookup


ALIAS_LOOKUP = build_alias_lookup()
