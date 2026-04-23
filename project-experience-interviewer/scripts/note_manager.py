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
QUESTION_SECTION_RE = re.compile(r"(?ms)^##\s*题目\s*\n(?P<question>.*?)(?=^##\s*参考回答\s*$|\Z)")
ANSWER_SECTION_RE = re.compile(r"(?ms)^##\s*参考回答\s*\n(?P<answer>.*)\Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Persist shared output directory and manage markdown question/answer files for project-experience interviewer and interviewee."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_config = subparsers.add_parser("get-config", help="Read saved output directory for a project.")
    get_config.add_argument("--project-root", required=True)

    set_config = subparsers.add_parser("set-config", help="Persist output directory for a project.")
    set_config.add_argument("--project-root", required=True)
    set_config.add_argument("--output-dir", required=True)

    write_question = subparsers.add_parser("write-question", help="Write a markdown question file.")
    write_question.add_argument("--project-root", required=True)
    write_question.add_argument("--source-json", required=True, help="JSON file path or '-' for stdin.")
    write_question.add_argument("--output-dir", help="Optional override for the output directory.")
    write_question.add_argument("--filename", help="Optional target filename, must end with .md.")

    read_question = subparsers.add_parser("read-question", help="Read a markdown question file.")
    read_question.add_argument("--project-root", required=True)
    read_question.add_argument("--input-path", help="Explicit markdown file path.")
    read_question.add_argument("--latest", action="store_true", help="Read the latest markdown file under the configured output directory.")

    write_answer = subparsers.add_parser("write-answer", help="Write answer back to an existing markdown question file.")
    write_answer.add_argument("--project-root", required=True)
    write_answer.add_argument("--source-json", required=True, help="JSON file path or '-' for stdin.")
    write_answer.add_argument("--input-path", help="Explicit markdown file path.")
    write_answer.add_argument("--latest", action="store_true", help="Write answer to the latest markdown file under the configured output directory.")

    write_note = subparsers.add_parser("write-note", help="Write a markdown file containing both question and answer.")
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


def normalize_markdown(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"


def question_from_payload(payload: dict[str, object]) -> str:
    question = str(payload.get("question", "")).strip()
    if not question:
        raise ValueError("source payload must contain non-empty question")
    return question


def answer_from_payload(payload: dict[str, object]) -> str:
    answer = str(payload.get("answer", "")).strip()
    if not answer:
        raise ValueError("source payload must contain non-empty answer")
    return answer


def markdown_question(question: str) -> str:
    return f"## 题目\n{question}\n"


def markdown_note(question: str, answer: str) -> str:
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


def list_markdown_files(output_dir: Path) -> list[Path]:
    if not output_dir.exists():
        return []
    files = [path for path in output_dir.iterdir() if path.is_file() and path.suffix.lower() == ".md"]
    files.sort(key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
    return files


def resolve_input_path(project_root: Path, input_path: str | None, latest: bool) -> Path:
    if input_path:
        path = Path(input_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"input markdown file does not exist: {path}")
        return path

    output_dir, _ = resolve_output_dir(project_root, None)
    candidates = list_markdown_files(output_dir)
    if not candidates:
        raise FileNotFoundError(f"no markdown files found in configured output directory: {output_dir}")
    if latest or not input_path:
        return candidates[0]
    raise FileNotFoundError("either --input-path or --latest is required")


def parse_markdown(markdown: str) -> dict[str, str]:
    normalized = normalize_markdown(markdown)
    question_match = QUESTION_SECTION_RE.search(normalized)
    if not question_match:
        raise ValueError("markdown file does not contain a valid '## 题目' section")

    answer_match = ANSWER_SECTION_RE.search(normalized)
    result = {
        "question": question_match.group("question").strip(),
        "answer": answer_match.group("answer").strip() if answer_match else "",
    }
    return result


def build_result(
    project_root: Path,
    output_dir: Path | None,
    target_path: Path,
    question: str,
    answer: str = "",
    config_path: Path | None = None,
) -> dict[str, object]:
    return {
        "project_root": str(project_root),
        "output_dir": str(output_dir) if output_dir else None,
        "output_path": str(target_path),
        "filename": target_path.name,
        "config_path": str(config_path) if config_path else None,
        "question": question,
        "has_answer": bool(answer),
        "answer": answer,
    }


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


def handle_write_question(project_root: Path, source_json: str, explicit_output_dir: str | None, filename: str | None) -> int:
    payload = read_source_payload(source_json)
    question = question_from_payload(payload)
    output_dir, config_path = resolve_output_dir(project_root, explicit_output_dir)
    ensure_directory(output_dir)

    final_filename = filename.strip() if filename else filename_from_payload(payload)
    if not final_filename.lower().endswith(".md"):
        final_filename = f"{final_filename}.md"
    final_filename = sanitize_stem(Path(final_filename).stem) + ".md"

    target_path = unique_path(output_dir / final_filename)
    target_path.write_text(markdown_question(question), encoding="utf-8")

    print_json(build_result(project_root, output_dir, target_path, question, config_path=config_path))
    return 0


def handle_read_question(project_root: Path, input_path: str | None, latest: bool) -> int:
    target_path = resolve_input_path(project_root, input_path, latest)
    parsed = parse_markdown(target_path.read_text(encoding="utf-8"))
    output_dir = target_path.parent
    config_path = config_path_for(project_root) if load_config(project_root) else None
    print_json(build_result(project_root, output_dir, target_path, parsed["question"], parsed["answer"], config_path))
    return 0


def handle_write_answer(project_root: Path, source_json: str, input_path: str | None, latest: bool) -> int:
    payload = read_source_payload(source_json)
    answer = answer_from_payload(payload)
    target_path = resolve_input_path(project_root, input_path, latest)
    parsed = parse_markdown(target_path.read_text(encoding="utf-8"))
    target_path.write_text(markdown_note(parsed["question"], answer), encoding="utf-8")

    output_dir = target_path.parent
    config_path = config_path_for(project_root) if load_config(project_root) else None
    print_json(build_result(project_root, output_dir, target_path, parsed["question"], answer, config_path))
    return 0


def handle_write_note(project_root: Path, source_json: str, explicit_output_dir: str | None, filename: str | None) -> int:
    payload = read_source_payload(source_json)
    question = question_from_payload(payload)
    answer = answer_from_payload(payload)
    output_dir, config_path = resolve_output_dir(project_root, explicit_output_dir)
    ensure_directory(output_dir)

    final_filename = filename.strip() if filename else filename_from_payload(payload)
    if not final_filename.lower().endswith(".md"):
        final_filename = f"{final_filename}.md"
    final_filename = sanitize_stem(Path(final_filename).stem) + ".md"

    target_path = unique_path(output_dir / final_filename)
    target_path.write_text(markdown_note(question, answer), encoding="utf-8")

    print_json(build_result(project_root, output_dir, target_path, question, answer, config_path))
    return 0


def main() -> int:
    args = parse_args()
    project_root = normalize_project_root(args.project_root)

    if args.command == "get-config":
        return handle_get_config(project_root)
    if args.command == "set-config":
        return handle_set_config(project_root, args.output_dir)
    if args.command == "write-question":
        return handle_write_question(project_root, args.source_json, args.output_dir, args.filename)
    if args.command == "read-question":
        return handle_read_question(project_root, args.input_path, args.latest)
    if args.command == "write-answer":
        return handle_write_answer(project_root, args.source_json, args.input_path, args.latest)
    if args.command == "write-note":
        return handle_write_note(project_root, args.source_json, args.output_dir, args.filename)
    raise ValueError(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
