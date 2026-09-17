# AI Resume Analyzer

An ATS-style resume vs. job-description matcher, written in pure Python
(standard library only) with **no LLM/API calls**. It extracts skills and
keywords from a job description, checks which of them appear in a resume
(with basic alias/synonym awareness), scores the match as a percentage, and
flags common structural problems (missing sections, missing contact info,
resume too short/long).

## How it works (methodology)

1. **Skills taxonomy** (`resume_analyzer/skills.py`): a hand-authored
   dictionary mapping ~50 canonical skills (languages, frameworks, cloud/
   DevOps tools, databases, process, and soft skills) to a list of aliases
   and synonyms, e.g. `"javascript": ["javascript", "js", "es6", ...]` or
   `"kubernetes": ["kubernetes", "k8s"]`. This is the "small alias map" used
   for lightweight stemming/synonym matching instead of a full NLP pipeline.

2. **Extraction** (`resume_analyzer/extractor.py`): every alias is compiled
   into a boundary-aware regular expression (word-boundary for plain
   alphanumeric aliases, punctuation-aware boundaries for aliases like
   `c++`, `node.js`, `c#`) and matched case-insensitively against the input
   text. A short alias like `"r"` or `"js"` will not accidentally match
   inside unrelated words such as `"server"` or `"jsonify"`.

3. **Scoring** (`resume_analyzer/scorer.py`): the set of canonical skills
   found in the job description is the "required" set; the set found in the
   resume is checked against it.

   ```
   score = (required skills also found in resume) / (required skills) * 100
   ```

   If the job description contains no recognizable skills, the score is
   defined as `0.0` and reported as such (there's nothing to measure a
   match against) rather than raising a division-by-zero error.

4. **Structure checks** (`resume_analyzer/structure.py`):
   - Common section headers (`Experience`, `Education`, `Skills`,
     `Projects`, `Summary`) are searched for; any missing ones are flagged.
   - An email regex and a phone-number regex check for basic contact info.
   - Word count is checked against sane lower/upper bounds (too short/long).
   - A small metric-word/percentage/dollar-sign heuristic checks whether the
     resume contains any quantifiable achievements (e.g. "reduced load time
     by 30%"); if not, a suggestion is added.

5. **Report** (`resume_analyzer/report.py`): combines all of the above into
   matched skills, missing skills, and a list of actionable suggestions.

This is intentionally a transparent, rule-based system — every score and
suggestion can be traced back to a specific regex match or word-count
threshold, with no external API calls and no non-determinism.

## Installation

Requires Python 3.11+. No third-party dependencies are required for the
core `.txt` workflow (pure standard library).

```bash
git clone https://github.com/pastbologanesh0101/resume-analyzer.git
cd resume-analyzer
```

Optional: to analyze `.docx` files in addition to `.txt`, install
python-docx:

```bash
pip install python-docx
```

## Usage

```bash
python analyze.py resume.txt job.txt
```

Example files are included under `examples/`:

```bash
python analyze.py examples/resume.txt examples/job.txt
```

## Example output

```
============================================================
AI RESUME ANALYZER - REPORT
============================================================
Match Score: 60.0%
Matched 9 / 15 required skills from the job description

Matched Skills:
  [x] agile
  [x] communication
  [x] docker
  [x] git
  [x] python
  [x] react
  [x] rest api
  [x] sql
  [x] teamwork

Missing Skills:
  [ ] aws
  [ ] data analysis
  [ ] kubernetes
  [ ] leadership
  [ ] machine learning
  [ ] mentoring

Resume word count: 110
Contact info found - email: True, phone: True
Quantifiable achievements detected: True

Suggestions:
  - Missing skills relative to the job description: aws, data analysis, kubernetes, leadership, machine learning, mentoring. If you genuinely have this experience, add it explicitly.
  - Resume section 'Projects' not found; consider adding it.
  - Resume is quite short (110 words); consider expanding on experience and skills (aim for at least 150).
============================================================
```

## Running the tests

```bash
python -m unittest discover -s tests -v
```

or, if you have pytest installed:

```bash
python -m pytest tests/ -v
```

The test suite covers skill extraction from a job description, alias/
synonym matching (e.g. `JS` -> `javascript`, `k8s` -> `kubernetes`), match
score calculation for fully-matched, partially-matched, and non-overlapping
skill sets, missing-section detection, contact-info detection, and edge
cases (empty resume, empty job description, both empty).

Continuous integration (`.github/workflows/tests.yml`) runs the same suite
on every push and pull request against Python 3.11 and 3.12.

## Project layout

```
resume_analyzer/
  skills.py       # skills taxonomy + alias map
  extractor.py     # regex-based keyword/skill extraction
  scorer.py        # match-score calculation
  structure.py     # section/contact-info/length checks
  report.py        # combines everything into a report
  loaders.py       # .txt (required) / .docx (optional) file loading
analyze.py         # CLI entry point
tests/              # unit tests
examples/           # sample resume.txt / job.txt
```

## License

MIT - see [LICENSE](LICENSE).
