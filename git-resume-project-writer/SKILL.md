---
name: git-resume-project-writer
description: Turn git history, changed files, and repository tech-stack signals into interview-ready resume project experience. Use when the user wants to write resume bullets from git commits, summarize a repository into project highlights, convert commit history into interview talking points, or extract responsibilities, technologies, and outcomes from code history. Support repository path, author, and date filters, then output one resume bullet, several project highlights, and a checklist of missing metrics to confirm.
---

# Git Resume Project Writer

Use git history as evidence, not as final wording. Extract what was built, what was optimized, what technologies were used, and where the work happened, then rewrite that into resume-ready project experience.

## Workflow

### 1. Clarify the scope

Confirm the minimum input first. If the user does not provide it, proceed with a stated default:

- Repository path: default to the current workspace repository
- Author scope: if the user says "my commits", prefer a git author filter
- Time range: default to full history, but prefer the user's employment period or the last 6-12 months for large repositories
- Output language: default to Chinese if the user writes in Chinese, otherwise mirror the user
- Output shape: default to one project entry plus 2-3 highlight bullets and a missing-metrics checklist
- Target role: if the user gives a JD or role direction, bias the rewrite toward those keywords

### 2. Extract evidence from git

Run `scripts/git_resume_summary.py` before drafting any resume wording.

Common commands:

```bash
python scripts/git_resume_summary.py --repo <repo-path>
python scripts/git_resume_summary.py --repo <repo-path> --author "<git author>"
python scripts/git_resume_summary.py --repo <repo-path> --author "<git author>" --since 2025-01-01 --until 2025-12-31
python scripts/git_resume_summary.py --repo <repo-path> --format json
```

Read these signals first:

- commit count, changed files, insertions, deletions
- frequently touched directories or modules
- action categories inferred from commit subjects: feature, optimization, bug fix, refactor, testing, delivery
- inferred stack from tracked files and config files
- representative commit subjects

Do not paste these signals directly into the resume. Use them only as evidence for later synthesis.

### 3. Translate git evidence into resume language

Map commit-level actions to business-facing contribution:

- `feat` / `add` / `implement` / `support` -> module delivery, platform capability build, feature rollout
- `fix` / `bug` / `hotfix` -> stability improvement, incident resolution, exception governance
- `optimize` / `perf` / `cache` -> latency, throughput, experience, or resource-efficiency improvement
- `refactor` / `cleanup` -> maintainability, architecture evolution, engineering efficiency
- `test` / `ci` / `release` / `docker` -> quality assurance, delivery automation, release efficiency

Rewrite rules:

- Start with an action, then module or scenario, then technical method, then result
- Do not copy commit subjects into the resume
- Do not emphasize commit volume unless the user explicitly asks for that
- Do not invent business data; if metrics are missing, state the technical effect and add a "need confirmation" note
- Merge scattered commits into module-level contribution instead of retelling a timeline
- Bias toward the skills that matter for the target role

### 4. Produce resume-ready output

If the user wants a single bullet, use this pattern:

```text
[Action] [module or capability], using [technical stack or key approach] to [build, optimize, refactor, or govern] [specific scope], resulting in [measured outcome or technical effect].
```

If the user accepts a standard project entry, output:

```markdown
Project:
Role:
Tech stack:
Experience:
- ...
- ...
- ...
Metrics to confirm:
- ...
```

Clearly separate:

- `Confirmed`: facts directly visible from the repository or script output
- `Inferred`: reasonable deductions from files, configs, and commit semantics
- `Need confirmation`: business background and metrics that only the user can supply

### 5. Load writing guidance when needed

Read `references/resume-project-writing.md` when the user asks how project experience should be written, why a bullet is weak, or how to make the output feel more interview-ready.

Use these rules first:

- formula: action + scenario or module + technical method + result
- emphasize contribution, not just responsibilities
- quantify results whenever possible
- keep each bullet focused on one core contribution

## Quality bar

Only return final wording when it meets these checks:

- starts with a strong action verb
- shows a clear module, workflow, or system boundary
- shows a real technical lever, not only a language name
- shows a result or at least a concrete technical effect
- matches the target role's priorities

## Example prompts

Typical triggers:

- "Write one resume project bullet from this repository's git commits"
- "Summarize my 2025 commits in this project into interview talking points"
- "I am applying for a Java backend role. Extract project highlights from this repo history"
- "Search how project experience should be written, then rewrite mine from git history"

## Resources

- `scripts/git_resume_summary.py`: extract git evidence, infer technologies, and summarize action categories
- `references/resume-project-writing.md`: project-experience writing rules, quantification guidance, rewrite examples, and source links
