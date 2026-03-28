#!/usr/bin/env python3
"""
Summarize git history into resume-writing evidence.

This script extracts objective signals from a repository:
- commit volume and diff stats
- dominant change areas
- inferred technology stack
- action categories inferred from commit subjects
- representative commits

It does not try to produce the final resume wording. A higher-level agent
should translate the evidence into business-facing resume bullets.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ACTION_KEYWORDS = {
    "feature_development": (
        "feat",
        "feature",
        "add",
        "added",
        "implement",
        "implemented",
        "create",
        "created",
        "support",
        "enable",
        "launch",
    ),
    "bug_fixing": ("fix", "bug", "hotfix", "patch", "resolve", "repair"),
    "performance_optimization": (
        "optimize",
        "optimization",
        "perf",
        "performance",
        "cache",
        "faster",
        "latency",
        "throughput",
    ),
    "refactoring": (
        "refactor",
        "cleanup",
        "clean",
        "simplify",
        "restructure",
        "rename",
        "decouple",
    ),
    "testing_quality": ("test", "qa", "coverage", "mock", "assert", "validate", "lint"),
    "delivery_operations": (
        "deploy",
        "release",
        "docker",
        "k8s",
        "kubernetes",
        "ci",
        "cd",
        "pipeline",
        "ops",
        "helm",
    ),
    "documentation": ("docs", "doc", "readme", "comment", "wiki"),
}

ACTION_HINTS = {
    "feature_development": "Translate into module delivery, platform capability build, or core workflow development.",
    "bug_fixing": "Translate into stability improvement, incident resolution, or exception governance.",
    "performance_optimization": "Translate into latency, throughput, resource efficiency, or experience optimization.",
    "refactoring": "Translate into maintainability, architecture evolution, or delivery efficiency improvement.",
    "testing_quality": "Translate into quality assurance, defect prevention, or regression risk reduction.",
    "delivery_operations": "Translate into CI/CD, deployment automation, or release efficiency.",
    "documentation": "Translate only if documentation changed engineering efficiency, onboarding, or standards.",
    "maintenance": "Translate into ongoing iteration, module ownership, or daily engineering support.",
}

TECH_BY_EXTENSION = {
    ".java": "Java",
    ".kt": "Kotlin",
    ".groovy": "Groovy",
    ".py": "Python",
    ".go": "Go",
    ".js": "JavaScript",
    ".jsx": "React",
    ".ts": "TypeScript",
    ".tsx": "React",
    ".vue": "Vue",
    ".rs": "Rust",
    ".php": "PHP",
    ".cs": "C#",
    ".scala": "Scala",
    ".sql": "SQL",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".tf": "Terraform",
    ".yml": "YAML",
    ".yaml": "YAML",
}

TECH_BY_FILENAME = {
    "pom.xml": "Maven",
    "build.gradle": "Gradle",
    "build.gradle.kts": "Gradle",
    "settings.gradle": "Gradle",
    "package.json": "Node.js",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "Yarn",
    "package-lock.json": "npm",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
    "Gemfile": "Ruby",
    "composer.json": "Composer",
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "Jenkinsfile": "Jenkins",
}

CONTENT_KEYWORDS = {
    "Spring Boot": ("spring-boot", "springframework.boot"),
    "Spring": ("springframework",),
    "MyBatis": ("mybatis",),
    "MySQL": ("mysql",),
    "PostgreSQL": ("postgres", "postgresql"),
    "Redis": ("redis",),
    "Kafka": ("kafka",),
    "RocketMQ": ("rocketmq",),
    "Elasticsearch": ("elasticsearch", "es."),
    "MongoDB": ("mongodb", "mongo"),
    "React": ("react",),
    "Vue": ("vue",),
    "Next.js": ("next", "nextjs"),
    "NestJS": ("nestjs", "@nestjs"),
    "Express": ("express",),
    "FastAPI": ("fastapi",),
    "Django": ("django",),
    "Flask": ("flask",),
    "Gin": ("gin-gonic/gin",),
    "Kubernetes": ("kubernetes", "helm", "ingress"),
    "GitHub Actions": (".github/workflows",),
}

GENERIC_PATH_PARTS = {
    "src",
    "main",
    "test",
    "tests",
    "java",
    "kotlin",
    "python",
    "app",
    "lib",
    "cmd",
    "pkg",
    "internal",
    "backend",
    "frontend",
    "server",
    "client",
}


def run_git(repo: Path, args: list[str]) -> str:
    command = ["git", "-C", str(repo), *args]
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def ensure_repo(repo: Path) -> None:
    try:
        output = run_git(repo, ["rev-parse", "--is-inside-work-tree"]).strip()
    except RuntimeError as exc:
        raise SystemExit(f"Not a git repository: {repo}\n{exc}") from exc
    if output != "true":
        raise SystemExit(f"Not a git repository: {repo}")


def collect_tracked_files(repo: Path) -> list[str]:
    output = run_git(repo, ["ls-files"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def read_text_if_small(path: Path, max_bytes: int = 200_000) -> str:
    try:
        if not path.exists() or path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def collect_commits(
    repo: Path,
    author: str | None,
    since: str | None,
    until: str | None,
    max_commits: int,
    include_merges: bool,
) -> list[dict]:
    pretty = "%H%x1f%ad%x1f%an%x1f%s"
    args = ["log", "--date=short", f"--max-count={max_commits}", f"--pretty=format:{pretty}", "--numstat"]
    if not include_merges:
        args.append("--no-merges")
    if author:
        args.append(f"--author={author}")
    if since:
        args.append(f"--since={since}")
    if until:
        args.append(f"--until={until}")

    raw = run_git(repo, args)
    commits = []
    current = None
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "\x1f" in line:
            if current:
                current["changed_files"] = len(current["files"])
                commits.append(current)
            meta = line.split("\x1f")
            if len(meta) < 4:
                current = None
                continue
            current = {
                "hash": meta[0],
                "date": meta[1],
                "author": meta[2],
                "subject": meta[3].strip(),
                "files": [],
                "insertions": 0,
                "deletions": 0,
                "changed_files": 0,
            }
            continue
        if current is None:
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, file_path = parts
        added_count = int(added) if added.isdigit() else 0
        deleted_count = int(deleted) if deleted.isdigit() else 0
        current["files"].append(file_path)
        current["insertions"] += added_count
        current["deletions"] += deleted_count
    if current:
        current["changed_files"] = len(current["files"])
        commits.append(current)
    return commits


def classify_action(subject: str) -> str:
    lower = subject.lower()
    for action, keywords in ACTION_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return action
    return "maintenance"


def pick_focus_label(path: str) -> str:
    parts = [part for part in Path(path).parts if part not in (".", "")]
    if not parts:
        return "(repo-root)"
    if parts[0] not in GENERIC_PATH_PARTS:
        return parts[0]
    if len(parts) > 1:
        return "/".join(parts[:2])
    return parts[0]


def infer_tech_stack(repo: Path, tracked_files: list[str]) -> list[str]:
    detected = []
    seen = set()

    def add(label: str) -> None:
        if label not in seen:
            seen.add(label)
            detected.append(label)

    for rel in tracked_files:
        path = Path(rel)
        tech = TECH_BY_EXTENSION.get(path.suffix.lower())
        if tech:
            add(tech)
        tech = TECH_BY_FILENAME.get(path.name)
        if tech:
            add(tech)

    content_candidates = []
    for rel in tracked_files:
        lower = rel.lower()
        if any(
            token in lower
            for token in (
                "pom.xml",
                "build.gradle",
                "build.gradle.kts",
                "package.json",
                "requirements.txt",
                "pyproject.toml",
                "go.mod",
                "docker-compose",
                "dockerfile",
                "application.yml",
                "application.yaml",
                "application.properties",
                ".github/workflows",
                "helm",
            )
        ):
            content_candidates.append(rel)

    for rel in content_candidates[:30]:
        content = read_text_if_small(repo / rel).lower()
        if not content:
            continue
        for tech, keywords in CONTENT_KEYWORDS.items():
            if any(keyword in content or keyword in rel.lower() for keyword in keywords):
                add(tech)

    return detected[:12]


def summarize(repo: Path, commits: list[dict], tracked_files: list[str]) -> dict:
    action_counts = Counter()
    focus_counts = Counter()
    file_counter = Counter()
    author_counter = Counter()
    total_insertions = 0
    total_deletions = 0

    for commit in commits:
        action_counts[classify_action(commit["subject"])] += 1
        author_counter[commit["author"]] += 1
        total_insertions += commit["insertions"]
        total_deletions += commit["deletions"]
        for file_path in commit["files"]:
            file_counter[file_path] += 1
            focus_counts[pick_focus_label(file_path)] += 1

    representative_commits = sorted(
        commits,
        key=lambda item: (item["changed_files"], item["insertions"] + item["deletions"], item["date"]),
        reverse=True,
    )[:8]

    top_actions = [
        {"action": action, "count": count, "resume_hint": ACTION_HINTS[action]}
        for action, count in action_counts.most_common(5)
    ]
    top_focus_areas = [{"area": area, "count": count} for area, count in focus_counts.most_common(6)]
    top_files = [{"path": path, "count": count} for path, count in file_counter.most_common(8)]
    tech_stack = infer_tech_stack(repo, tracked_files)

    dominant_actions = [item["action"] for item in top_actions[:2]] or ["maintenance"]
    dominant_areas = [item["area"] for item in top_focus_areas[:3]]
    tech_preview = ", ".join(tech_stack[:4]) if tech_stack else "relevant technologies"
    area_preview = ", ".join(dominant_areas) if dominant_areas else "core modules"

    return {
        "repository": repo.name,
        "repository_path": str(repo),
        "commit_count": len(commits),
        "authors": [{"author": author, "count": count} for author, count in author_counter.most_common(5)],
        "insertions": total_insertions,
        "deletions": total_deletions,
        "unique_files_changed": len(file_counter),
        "tech_stack_inferred": tech_stack,
        "top_actions": top_actions,
        "top_focus_areas": top_focus_areas,
        "top_files": top_files,
        "representative_commits": [
            {
                "date": item["date"],
                "author": item["author"],
                "subject": item["subject"],
                "changed_files": item["changed_files"],
                "insertions": item["insertions"],
                "deletions": item["deletions"],
            }
            for item in representative_commits
        ],
        "writing_prompts": [
            "Treat git history as evidence, not resume text.",
            "Use the formula: Action + module or scenario + technical method + measurable result.",
            "Do not invent business numbers. Mark missing metrics for confirmation.",
        ],
        "draft_bullet_shells": [
            (
                f"Own {area_preview} work using {tech_preview}; describe the concrete module delivered "
                "or optimized and add a measured outcome if available."
            ),
            (
                f"Frame the contribution around {', '.join(dominant_actions)}; replace commit-level detail "
                "with module scope, technical solution, and business-facing impact."
            ),
            "If metrics are missing, state the technical effect first and ask the user to confirm numbers such as latency, QPS, cost, defect rate, or delivery time.",
        ],
    }


def to_markdown(summary: dict, args: argparse.Namespace) -> str:
    lines = [
        "# Git Resume Evidence",
        "",
        "## Scope",
        f"- Repository: {summary['repository']}",
        f"- Path: {summary['repository_path']}",
        f"- Author filter: {args.author or 'none'}",
        f"- Since: {args.since or 'none'}",
        f"- Until: {args.until or 'none'}",
        f"- Commit limit: {args.max_commits}",
        "",
        "## Quantitative Signals",
        f"- Commits analyzed: {summary['commit_count']}",
        f"- Unique files changed: {summary['unique_files_changed']}",
        f"- Insertions: +{summary['insertions']}",
        f"- Deletions: -{summary['deletions']}",
        "",
        "## Inferred Tech Stack",
    ]
    if summary["tech_stack_inferred"]:
        lines.extend(f"- {tech}" for tech in summary["tech_stack_inferred"])
    else:
        lines.append("- No strong signal detected from tracked files")

    lines.extend(["", "## Dominant Action Categories"])
    if summary["top_actions"]:
        for item in summary["top_actions"]:
            lines.append(f"- {item['action']}: {item['count']} commits. {item['resume_hint']}")
    else:
        lines.append("- No commits matched the selected filters")

    lines.extend(["", "## Focus Areas"])
    if summary["top_focus_areas"]:
        for item in summary["top_focus_areas"]:
            lines.append(f"- {item['area']}: {item['count']} touched files")
    else:
        lines.append("- No changed areas detected")

    lines.extend(["", "## Representative Commits"])
    if summary["representative_commits"]:
        for item in summary["representative_commits"]:
            lines.append(
                "- {date} | {author} | {subject} "
                "(files={changed_files}, +{insertions}/-{deletions})".format(**item)
            )
    else:
        lines.append("- No commits available")

    lines.extend(["", "## Resume Drafting Hints"])
    lines.extend(f"- {item}" for item in summary["writing_prompts"])
    lines.extend(["", "## Draft Bullet Shells"])
    lines.extend(f"- {item}" for item in summary["draft_bullet_shells"])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize git history into resume evidence.")
    parser.add_argument("--repo", required=True, help="Path to the git repository")
    parser.add_argument("--author", help="Optional git author filter")
    parser.add_argument("--since", help="Optional git since date, for example 2025-01-01")
    parser.add_argument("--until", help="Optional git until date, for example 2025-12-31")
    parser.add_argument("--max-commits", type=int, default=200, help="Maximum number of commits to analyze")
    parser.add_argument("--include-merges", action="store_true", help="Include merge commits")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"Repository path does not exist: {repo}", file=sys.stderr)
        return 1

    ensure_repo(repo)
    commits = collect_commits(
        repo=repo,
        author=args.author,
        since=args.since,
        until=args.until,
        max_commits=args.max_commits,
        include_merges=args.include_merges,
    )
    tracked_files = collect_tracked_files(repo)
    summary = summarize(repo, commits, tracked_files)

    if args.format == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(to_markdown(summary, args), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
