#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path


INVALID_FILENAME_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
WHITESPACE_RE = re.compile(r"\s+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Persist note output directory and write markdown notes for project-experience-interview."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_config = subparsers.add_parser("get-config", help="Read saved note output directory for a project.")
    get_config.add_argument("--project-root", required=True)

    set_config = subparsers.add_parser("set-config", help="Persist note output directory for a project.")
    set_config.add_argument("--project-root", required=True)
    set_config.add_argument("--output-dir", required=True)

    write_note = subparsers.add_parser("write-note", help="Write a markdown note using saved or explicit output directory.")
    write_note.add_argument("--project-root", required=True)
    write_note.add_argument("--source-json", required=True, help="JSON file path or '-' for stdin.")
    write_note.add_argument("--output-dir", help="Optional override for the output directory.")
    write_note.add_argument("--filename", help="Optional target filename, must end with .md.")

    return parser.parse_args()


def memory_root() -> Path:
    return Path.home() / ".codex" / "memories" / "project-experience-interview"


def normalize_project_root(project_root: str) -> Path:
    return Path(project_root).expanduser().resolve()


def project_key(project_root: Path) -> str:
    normalized = str(project_root).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def config_path_for(project_root: Path) -> Path:
    return memory_root() / "projects" / f"{project_key(project_root)}.json"


def load_config(project_root: Path) -> dict[str, object] | None:
    config_path = config_path_for(project_root)
    if not config_path.exists():
        return None
    return json.loads(config_path.read_text(encoding="utf-8"))


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_config(project_root: Path, output_dir: Path) -> dict[str, object]:
    config_path = config_path_for(project_root)
    ensure_directory(config_path.parent)
    ensure_directory(output_dir)
    payload = {
        "project_root": str(project_root),
        "output_dir": str(output_dir),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def sanitize_stem(raw: str) -> str:
    candidate = (raw or "").strip()
    candidate = candidate.replace("\r", " ").replace("\n", " ")
    candidate = INVALID_FILENAME_CHARS_RE.sub(" ", candidate)
    candidate = WHITESPACE_RE.sub(" ", candidate).strip(" .")
    if not candidate:
        candidate = "project-experience-note"
    return candidate[:80].rstrip(" .")


def unique_path(target: Path) -> Path:
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    index = 2
    while True:
        candidate = target.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def read_source_payload(source_json: str) -> dict[str, object]:
    if source_json == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(source_json).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("source payload must be a JSON object")
    return payload


def markdown_from_payload(payload: dict[str, object]) -> str:
    question = str(payload.get("question", "")).strip()
    answer = str(payload.get("answer", "")).strip()
    if not question or not answer:
        raise ValueError("source payload must contain non-empty question and answer")
    return f"## 题目\n{question}\n\n## 参考回答\n{answer}\n"


def filename_from_payload(payload: dict[str, object]) -> str:
    title = str(payload.get("title", "")).strip()
    question = str(payload.get("question", "")).strip()
    base = title or question.splitlines()[0]
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"{timestamp}-{sanitize_stem(base)}.md"


def resolve_output_dir(project_root: Path, explicit_output_dir: str | None) -> tuple[Path, Path | None]:
    if explicit_output_dir:
        return Path(explicit_output_dir).expanduser().resolve(), None

    config = load_config(project_root)
    if not config:
        raise FileNotFoundError("note output directory is not configured for this project")
    output_dir = Path(str(config["output_dir"])).expanduser().resolve()
    return output_dir, config_path_for(project_root)


def handle_get_config(project_root: Path) -> int:
    config = load_config(project_root)
    payload: dict[str, object] = {
        "project_root": str(project_root),
        "config_path": str(config_path_for(project_root)),
        "configured": bool(config),
    }
    if config:
        payload["output_dir"] = config["output_dir"]
        payload["updated_at"] = config.get("updated_at")
    print_json(payload)
    return 0


def handle_set_config(project_root: Path, output_dir_raw: str) -> int:
    output_dir = Path(output_dir_raw).expanduser().resolve()
    payload = save_config(project_root, output_dir)
    payload["configured"] = True
    payload["config_path"] = str(config_path_for(project_root))
    print_json(payload)
    return 0


def handle_write_note(project_root: Path, source_json: str, explicit_output_dir: str | None, filename: str | None) -> int:
    payload = read_source_payload(source_json)
    output_dir, config_path = resolve_output_dir(project_root, explicit_output_dir)
    ensure_directory(output_dir)

    final_filename = filename.strip() if filename else filename_from_payload(payload)
    if not final_filename.lower().endswith(".md"):
        final_filename = f"{final_filename}.md"
    final_filename = sanitize_stem(Path(final_filename).stem) + ".md"

    target_path = unique_path(output_dir / final_filename)
    markdown = markdown_from_payload(payload)
    target_path.write_text(markdown, encoding="utf-8")

    result: dict[str, object] = {
        "project_root": str(project_root),
        "output_dir": str(output_dir),
        "output_path": str(target_path),
        "filename": target_path.name,
        "config_path": str(config_path) if config_path else None,
    }
    print_json(result)
    return 0


def main() -> int:
    args = parse_args()
    project_root = normalize_project_root(args.project_root)

    if args.command == "get-config":
        return handle_get_config(project_root)
    if args.command == "set-config":
        return handle_set_config(project_root, args.output_dir)
    if args.command == "write-note":
        return handle_write_note(project_root, args.source_json, args.output_dir, args.filename)
    raise ValueError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
