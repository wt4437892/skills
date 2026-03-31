#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


QUESTION_RE = re.compile(r"^##\s*(Q\d+|Q)\s*[：:]\s*(.+?)\s*$", re.MULTILINE)
NOTE_META_RE = re.compile(r"^\*\*(记录日期|下次复习|上次复习|复习次数|标签)\*\*[:：]\s*(.*?)\s*$")
INDEX_LINE_RE = re.compile(
    r"^- \[(?P<note_file>[^\]]+)\] "
    r"\[标签: (?P<tags>[^\]]*)\] "
    r"\[记录日期: (?P<record_date>[^\]]*)\] "
    r"\[下次复习: (?P<next_review>[^\]]*)\] "
    r"\[上次复习: (?P<last_review>[^\]]*)\] "
    r"\[复习次数: (?P<review_count>[^\]]*)\] "
    r"(?P<question_id>Q\d+|Q)[：:](?P<title>.+?)\s*$"
)
DATE_FMT = "%Y-%m-%d"
CACHE_FILE_NAME = ".review-cache.json"


@dataclass
class ReviewItem:
    domain: str
    note_file: str
    tags: list[str]
    record_date: str
    next_review: str
    last_review: str
    review_count: int
    question_id: str
    title: str
    index_path: Path
    answer: str = ""
    explanation: str = ""

    @property
    def note_path(self) -> Path:
        return self.index_path.parent / self.note_file

    def to_dict(self, include_content: bool = False) -> dict[str, object]:
        payload = {
            "domain": self.domain,
            "note_file": self.note_file,
            "note_path": str(self.note_path),
            "tags": self.tags,
            "record_date": self.record_date,
            "next_review": self.next_review,
            "last_review": self.last_review,
            "review_count": self.review_count,
            "question_id": self.question_id,
            "title": self.title,
            "index_path": str(self.index_path),
        }
        if include_content:
            payload["answer"] = self.answer
            payload["explanation"] = self.explanation
        return payload


@dataclass
class QuestionBlock:
    question_id: str
    title: str
    heading_line: str
    body: str
    start: int
    end: int
    metadata: dict[str, str]
    answer: str
    explanation: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fast lookup for java-senior-reviewer notes.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    due = subparsers.add_parser("due", help="List due review items from cache or .index.md files.")
    due.add_argument("--notes-root", required=True)
    due.add_argument("--today", required=True)
    due.add_argument("--domain", action="append", dest="domains")
    due.add_argument("--last-domain")
    due.add_argument("--limit", type=int)
    due.add_argument("--seed", type=int, default=0)

    show = subparsers.add_parser("show", help="Show answer/explanation for a single question.")
    show.add_argument("--notes-root", required=True)
    show.add_argument("--domain", required=True)
    show.add_argument("--note-file", required=True)
    show.add_argument("--question-id", required=True)

    update = subparsers.add_parser("update", help="Update review metadata in note file, index, and cache.")
    update.add_argument("--notes-root", required=True)
    update.add_argument("--domain", required=True)
    update.add_argument("--note-file", required=True)
    update.add_argument("--question-id", required=True)
    update.add_argument("--today", required=True)
    update.add_argument("--score", type=int)
    update.add_argument("--unknown", action="store_true")

    reindex = subparsers.add_parser("reindex", help="Rebuild .index.md and .review-cache.json from note files.")
    reindex.add_argument("--notes-root", required=True)
    reindex.add_argument("--domain", action="append", dest="domains")
    reindex.add_argument("--today")

    return parser.parse_args()


def parse_date(value: str) -> date | None:
    text = (value or "").strip()
    if not text or text in {"-", "未知"}:
        return None
    try:
        return datetime.strptime(text, DATE_FMT).date()
    except ValueError:
        return None


def normalize_count(value: str) -> int:
    try:
        return int((value or "").strip())
    except ValueError:
        return 0


def parse_tags(value: str) -> list[str]:
    text = (value or "").strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def question_sort_key(question_id: str) -> tuple[int, str]:
    match = re.match(r"Q(\d+)$", question_id)
    if match:
        return (int(match.group(1)), question_id)
    return (0, question_id)


def discover_domains(notes_root: Path, requested_domains: list[str] | None) -> list[Path]:
    if requested_domains:
        return [notes_root / name for name in requested_domains if (notes_root / name).is_dir()]

    domain_dirs: list[Path] = []
    for child in sorted(notes_root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if (child / ".index.md").exists() or any(child.glob("*.md")):
            domain_dirs.append(child)
    return domain_dirs


def cache_path_for(domain_dir: Path) -> Path:
    return domain_dir / CACHE_FILE_NAME


def load_index_entries(domain_dir: Path) -> list[ReviewItem]:
    index_path = domain_dir / ".index.md"
    if not index_path.exists():
        return []

    entries: list[ReviewItem] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        match = INDEX_LINE_RE.match(line.strip())
        if not match:
            continue
        entries.append(
            ReviewItem(
                domain=domain_dir.name,
                note_file=match.group("note_file").strip(),
                tags=parse_tags(match.group("tags")),
                record_date=match.group("record_date").strip() or "未知",
                next_review=match.group("next_review").strip() or "未知",
                last_review=match.group("last_review").strip() or "-",
                review_count=normalize_count(match.group("review_count")),
                question_id=match.group("question_id").strip(),
                title=match.group("title").strip(),
                index_path=index_path,
            )
        )
    return entries


def load_cache_entries(domain_dir: Path) -> list[ReviewItem]:
    cache_path = cache_path_for(domain_dir)
    if not cache_path.exists():
        return []

    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    entries: list[ReviewItem] = []
    for item in payload.get("items", []):
        entries.append(
            ReviewItem(
                domain=item.get("domain", domain_dir.name),
                note_file=item["note_file"],
                tags=list(item.get("tags", [])),
                record_date=item.get("record_date", "未知"),
                next_review=item.get("next_review", "未知"),
                last_review=item.get("last_review", "-"),
                review_count=normalize_count(str(item.get("review_count", 0))),
                question_id=item["question_id"],
                title=item["title"],
                index_path=domain_dir / ".index.md",
                answer=item.get("answer", ""),
                explanation=item.get("explanation", ""),
            )
        )
    return entries


def load_domain_entries(domain_dir: Path) -> list[ReviewItem]:
    cached = load_cache_entries(domain_dir)
    if cached:
        return cached
    return load_index_entries(domain_dir)


def due_sort_key(entry: ReviewItem, last_domain: str | None) -> tuple[date, int, int, str, str]:
    next_review = parse_date(entry.next_review) or date.min
    domain_penalty = 1 if last_domain and entry.domain == last_domain else 0
    return (next_review, entry.review_count, domain_penalty, entry.domain, f"{entry.note_file}:{entry.question_id}")


def handle_due(args: argparse.Namespace) -> int:
    notes_root = Path(args.notes_root).resolve()
    today = datetime.strptime(args.today, DATE_FMT).date()
    domain_dirs = discover_domains(notes_root, args.domains)

    due_items: list[ReviewItem] = []
    for domain_dir in domain_dirs:
        for entry in load_domain_entries(domain_dir):
            next_review = parse_date(entry.next_review)
            if entry.next_review == "未知" or next_review is None or next_review <= today:
                due_items.append(entry)

    due_items.sort(key=lambda item: due_sort_key(item, args.last_domain))

    if args.seed and len(due_items) > 1:
        random.Random(args.seed).shuffle(due_items)
        due_items.sort(key=lambda item: due_sort_key(item, args.last_domain))

    if args.limit:
        due_items = due_items[: args.limit]

    payload = {
        "today": args.today,
        "count": len(due_items),
        "items": [item.to_dict() for item in due_items],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def parse_note_blocks(note_path: Path) -> list[QuestionBlock]:
    text = note_path.read_text(encoding="utf-8")
    matches = list(QUESTION_RE.finditer(text))
    blocks: list[QuestionBlock] = []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end]
        metadata = extract_note_metadata(body)
        answer, explanation = extract_answer_sections(body)
        blocks.append(
            QuestionBlock(
                question_id=match.group(1).strip(),
                title=match.group(2).strip(),
                heading_line=match.group(0).strip(),
                body=body,
                start=start,
                end=end,
                metadata=metadata,
                answer=answer,
                explanation=explanation,
            )
        )

    return blocks


def extract_note_metadata(body: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in body.splitlines():
        match = NOTE_META_RE.match(line.strip())
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    return metadata


def extract_answer_sections(body: str) -> tuple[str, str]:
    answer_marker = "【答案】"
    explanation_marker = "【讲解】"
    answer_index = body.find(answer_marker)
    if answer_index == -1:
        return "", ""

    explanation_index = body.find(explanation_marker, answer_index + len(answer_marker))
    if explanation_index == -1:
        return body[answer_index + len(answer_marker) :].strip(), ""

    answer = body[answer_index + len(answer_marker) : explanation_index].strip()
    explanation = body[explanation_index + len(explanation_marker) :].strip()
    return answer, explanation


def get_block(note_path: Path, question_id: str) -> QuestionBlock:
    for block in parse_note_blocks(note_path):
        if block.question_id == question_id:
            return block
    raise SystemExit(f"Question not found: {note_path} {question_id}")


def infer_record_date(note_path: Path, original_value: str | None) -> str:
    if original_value and original_value.strip():
        return original_value.strip()
    modified = datetime.fromtimestamp(note_path.stat().st_mtime).date()
    return modified.strftime(DATE_FMT)


def item_from_block(domain_dir: Path, note_path: Path, block: QuestionBlock) -> ReviewItem:
    metadata = block.metadata
    return ReviewItem(
        domain=domain_dir.name,
        note_file=note_path.name,
        tags=parse_tags(metadata.get("标签", "")),
        record_date=infer_record_date(note_path, metadata.get("记录日期", "")),
        next_review=metadata.get("下次复习", "未知") or "未知",
        last_review=metadata.get("上次复习", "-") or "-",
        review_count=normalize_count(metadata.get("复习次数", "0")),
        question_id=block.question_id,
        title=block.title,
        index_path=domain_dir / ".index.md",
        answer=block.answer,
        explanation=block.explanation,
    )


def scan_domain_notes(domain_dir: Path) -> list[ReviewItem]:
    items: list[ReviewItem] = []
    for note_path in sorted(domain_dir.glob("*.md")):
        if note_path.name == ".index.md":
            continue
        for block in parse_note_blocks(note_path):
            items.append(item_from_block(domain_dir, note_path, block))

    items.sort(key=lambda item: (item.note_file, question_sort_key(item.question_id)))
    return items


def write_cache(domain_dir: Path, items: list[ReviewItem], updated_at: str) -> Path:
    payload = {
        "domain": domain_dir.name,
        "updated_at": updated_at,
        "count": len(items),
        "items": [item.to_dict(include_content=True) for item in items],
    }
    cache_path = cache_path_for(domain_dir)
    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return cache_path


def format_index_line(item: ReviewItem) -> str:
    tags = ",".join(item.tags)
    return (
        f"- [{item.note_file}] [标签: {tags}] "
        f"[记录日期: {item.record_date}] "
        f"[下次复习: {item.next_review}] "
        f"[上次复习: {item.last_review}] "
        f"[复习次数: {item.review_count}] "
        f"{item.question_id}：{item.title}"
    )


def write_index(domain_dir: Path, items: list[ReviewItem], updated_at: str) -> Path:
    lines = [
        f"# {domain_dir.name} 题目索引",
        "",
        f"最后更新：{updated_at}",
        "",
        "## 已考察题目列表",
        "",
    ]
    for item in items:
        lines.append(format_index_line(item))
    lines.extend(["", "---", f"总计：{len(items)} 道题目"])

    index_path = domain_dir / ".index.md"
    index_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return index_path


def rebuild_domain(domain_dir: Path, updated_at: str) -> dict[str, object]:
    items = scan_domain_notes(domain_dir)
    index_path = write_index(domain_dir, items, updated_at)
    cache_path = write_cache(domain_dir, items, updated_at)
    return {
        "domain": domain_dir.name,
        "count": len(items),
        "index_path": str(index_path),
        "cache_path": str(cache_path),
    }


def handle_show(args: argparse.Namespace) -> int:
    notes_root = Path(args.notes_root).resolve()
    domain_dir = notes_root / args.domain

    cached = [
        item
        for item in load_cache_entries(domain_dir)
        if item.note_file == args.note_file and item.question_id == args.question_id
    ]
    if cached:
        item = cached[0]
        payload = {
            "domain": item.domain,
            "note_file": item.note_file,
            "note_path": str(item.note_path),
            "question_id": item.question_id,
            "title": item.title,
            "metadata": {
                "record_date": item.record_date,
                "next_review": item.next_review,
                "last_review": item.last_review,
                "review_count": item.review_count,
                "tags": item.tags,
            },
            "answer": item.answer,
            "explanation": item.explanation,
            "source": "cache",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    note_path = domain_dir / args.note_file
    block = get_block(note_path, args.question_id)
    payload = {
        "domain": args.domain,
        "note_file": args.note_file,
        "note_path": str(note_path),
        "question_id": block.question_id,
        "title": block.title,
        "metadata": {
            "record_date": infer_record_date(note_path, block.metadata.get("记录日期", "")),
            "next_review": block.metadata.get("下次复习", "未知"),
            "last_review": block.metadata.get("上次复习", "-"),
            "review_count": normalize_count(block.metadata.get("复习次数", "0")),
            "tags": parse_tags(block.metadata.get("标签", "")),
        },
        "answer": block.answer,
        "explanation": block.explanation,
        "source": "note",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def compute_next_review(today: date, prior_count: int, score: int | None, unknown: bool) -> tuple[int, str]:
    if unknown or score is None or score <= 5:
        return 0, (today + timedelta(days=2)).strftime(DATE_FMT)
    if score <= 7:
        return prior_count, (today + timedelta(days=3)).strftime(DATE_FMT)

    new_count = prior_count + 1
    if new_count == 1:
        offset = 7
    elif new_count == 2:
        offset = 15
    elif new_count == 3:
        offset = 30
    else:
        offset = 60
    return new_count, (today + timedelta(days=offset)).strftime(DATE_FMT)


def strip_leading_metadata(body: str) -> str:
    lines = body.splitlines()
    index = 0
    while index < len(lines) and not lines[index].strip():
        index += 1
    while index < len(lines) and NOTE_META_RE.match(lines[index].strip()):
        index += 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    return "\n".join(lines[index:]).strip("\n")


def rebuild_block(block: QuestionBlock, note_path: Path, today_text: str, score: int | None, unknown: bool) -> tuple[str, dict[str, object]]:
    today = datetime.strptime(today_text, DATE_FMT).date()
    record_date = infer_record_date(note_path, block.metadata.get("记录日期"))
    prior_count = normalize_count(block.metadata.get("复习次数", "0"))
    tags = parse_tags(block.metadata.get("标签", ""))
    review_count, next_review = compute_next_review(today, prior_count, score, unknown)

    metadata_lines = [
        f"**记录日期**：{record_date}",
        f"**下次复习**：{next_review}",
        f"**上次复习**：{today_text}",
        f"**复习次数**：{review_count}",
        f"**标签**：[{', '.join(tags)}]" if tags else "**标签**：[]",
    ]
    remainder = strip_leading_metadata(block.body)
    if remainder:
        updated_block = f"{block.heading_line}\n\n" + "\n".join(metadata_lines) + f"\n\n{remainder}\n"
    else:
        updated_block = f"{block.heading_line}\n\n" + "\n".join(metadata_lines) + "\n"

    payload = {
        "record_date": record_date,
        "next_review": next_review,
        "last_review": today_text,
        "review_count": review_count,
        "tags": tags,
        "title": block.title,
        "question_id": block.question_id,
    }
    return updated_block, payload


def rewrite_note(note_path: Path, question_id: str, today_text: str, score: int | None, unknown: bool) -> dict[str, object]:
    text = note_path.read_text(encoding="utf-8")
    blocks = parse_note_blocks(note_path)
    for block in blocks:
        if block.question_id != question_id:
            continue
        updated_block, payload = rebuild_block(block, note_path, today_text, score, unknown)
        updated_text = text[: block.start] + updated_block + text[block.end :]
        note_path.write_text(updated_text, encoding="utf-8")
        return payload
    raise SystemExit(f"Question not found: {note_path} {question_id}")


def handle_update(args: argparse.Namespace) -> int:
    if not args.unknown and args.score is None:
        raise SystemExit("Either --score or --unknown is required.")

    notes_root = Path(args.notes_root).resolve()
    domain_dir = notes_root / args.domain
    note_path = domain_dir / args.note_file

    metadata = rewrite_note(note_path, args.question_id, args.today, args.score, args.unknown)
    rebuild_domain(domain_dir, args.today)

    payload = {
        "domain": args.domain,
        "note_file": args.note_file,
        "note_path": str(note_path),
        "index_path": str(domain_dir / ".index.md"),
        "cache_path": str(cache_path_for(domain_dir)),
        "question_id": metadata["question_id"],
        "title": metadata["title"],
        "record_date": metadata["record_date"],
        "next_review": metadata["next_review"],
        "last_review": metadata["last_review"],
        "review_count": metadata["review_count"],
        "tags": metadata["tags"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def handle_reindex(args: argparse.Namespace) -> int:
    notes_root = Path(args.notes_root).resolve()
    updated_at = args.today or datetime.now().strftime(DATE_FMT)
    domain_dirs = discover_domains(notes_root, args.domains)
    payload = {
        "updated_at": updated_at,
        "domains": [rebuild_domain(domain_dir, updated_at) for domain_dir in domain_dirs],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "due":
        return handle_due(args)
    if args.command == "show":
        return handle_show(args)
    if args.command == "update":
        return handle_update(args)
    if args.command == "reindex":
        return handle_reindex(args)
    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
