#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


QUESTION_RE = re.compile(r"^##\s*(Q\d+|Q)\s*[：:]\s*(.+?)\s*$", re.MULTILINE)
NOTE_META_RE = re.compile(r"^\*\*(记录日期|下次复习|上次复习|复习次数|标签)\*\*[:：]\s*(.*?)\s*$")
DATE_FMT = "%Y-%m-%d"
CACHE_FILE_NAME = ".review-cache.json"
DAILY_TRACKER_FILE_NAME = ".daily-question-count.json"


@dataclass
class NoteItem:
    domain: str
    note_file: str
    question_id: str
    title: str
    tags: list[str]
    record_date: str
    next_review: str
    last_review: str
    review_count: int
    answer: str
    explanation: str

    def to_cache_dict(self, note_root: Path) -> dict[str, object]:
        return {
            "domain": self.domain,
            "note_file": self.note_file,
            "note_path": str(note_root / self.domain / self.note_file),
            "question_id": self.question_id,
            "title": self.title,
            "tags": self.tags,
            "record_date": self.record_date,
            "next_review": self.next_review,
            "last_review": self.last_review,
            "review_count": self.review_count,
            "answer": self.answer,
            "explanation": self.explanation,
        }

    def to_list_dict(self) -> dict[str, object]:
        return {
            "domain": self.domain,
            "note_file": self.note_file,
            "question_id": self.question_id,
            "title": self.title,
            "tags": self.tags,
            "record_date": self.record_date,
            "next_review": self.next_review,
            "last_review": self.last_review,
            "review_count": self.review_count,
        }


def note_item_key(domain: str, note_file: str, question_id: str) -> str:
    return f"{domain}/{note_file}#{question_id}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and query fast cache for java-senior-interviewer notes.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync = subparsers.add_parser("sync", help="Rebuild .index.md and .review-cache.json from note files.")
    sync.add_argument("--notes-root", required=True)
    sync.add_argument("--domain", required=True)
    sync.add_argument("--today", required=True)

    listing = subparsers.add_parser("list", help="List existing questions via cache.")
    listing.add_argument("--notes-root", required=True)
    listing.add_argument("--domain", required=True)
    listing.add_argument("--sync-if-missing", action="store_true")
    listing.add_argument("--today")

    return parser.parse_args()


def parse_tags(value: str) -> list[str]:
    text = (value or "").strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def normalize_count(value: str) -> int:
    try:
        return int((value or "").strip())
    except ValueError:
        return 0


def infer_record_date(note_path: Path, raw: str | None, prior_value: str | None = None) -> str:
    if raw and raw.strip():
        return raw.strip()
    if prior_value and prior_value.strip() and prior_value.strip() != "未知":
        return prior_value.strip()
    return "未知"


def question_sort_key(question_id: str) -> tuple[int, str]:
    match = re.match(r"Q(\d+)$", question_id)
    if match:
        return (int(match.group(1)), question_id)
    return (0, question_id)


def extract_metadata(body: str) -> dict[str, str]:
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


def scan_domain(domain_dir: Path, prior_record_dates: dict[tuple[str, str], str] | None = None) -> list[NoteItem]:
    items: list[NoteItem] = []
    prior_record_dates = prior_record_dates or {}
    for note_path in sorted(domain_dir.glob("*.md")):
        if note_path.name == ".index.md":
            continue
        text = note_path.read_text(encoding="utf-8")
        matches = list(QUESTION_RE.finditer(text))
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end]
            metadata = extract_metadata(body)
            answer, explanation = extract_answer_sections(body)
            items.append(
                NoteItem(
                    domain=domain_dir.name,
                    note_file=note_path.name,
                    question_id=match.group(1).strip(),
                    title=match.group(2).strip(),
                    tags=parse_tags(metadata.get("标签", "")),
                    record_date=infer_record_date(
                        note_path,
                        metadata.get("记录日期"),
                        prior_record_dates.get((note_path.name, match.group(1).strip())),
                    ),
                    next_review=metadata.get("下次复习", "未知") or "未知",
                    last_review=metadata.get("上次复习", "-") or "-",
                    review_count=normalize_count(metadata.get("复习次数", "0")),
                    answer=answer,
                    explanation=explanation,
                )
            )
    items.sort(key=lambda item: (item.note_file, question_sort_key(item.question_id)))
    return items


def write_index(domain_dir: Path, items: list[NoteItem], today: str) -> Path:
    lines = [
        f"# {domain_dir.name} 题目索引",
        "",
        f"最后更新：{today}",
        "",
        "## 已考察题目列表",
        "",
    ]
    for item in items:
        tags = ",".join(item.tags)
        lines.append(
            f"- [{item.note_file}] [标签: {tags}] "
            f"[记录日期: {item.record_date}] "
            f"[下次复习: {item.next_review}] "
            f"[上次复习: {item.last_review}] "
            f"[复习次数: {item.review_count}] "
            f"{item.question_id}：{item.title}"
        )
    lines.extend(["", "---", f"总计：{len(items)} 道题目"])
    index_path = domain_dir / ".index.md"
    index_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return index_path


def write_cache(notes_root: Path, domain_dir: Path, items: list[NoteItem], today: str) -> Path:
    payload = {
        "domain": domain_dir.name,
        "updated_at": today,
        "count": len(items),
        "items": [item.to_cache_dict(notes_root) for item in items],
    }
    cache_path = domain_dir / CACHE_FILE_NAME
    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return cache_path


def sync_domain(notes_root: Path, domain: str, today: str) -> dict[str, object]:
    domain_dir = notes_root / domain
    items = scan_domain(domain_dir, load_prior_record_dates(notes_root, domain))
    index_path = write_index(domain_dir, items, today)
    cache_path = write_cache(notes_root, domain_dir, items, today)
    daily_tracker = update_daily_tracker_for_domain(notes_root, today, domain, items)
    return {
        "domain": domain,
        "count": len(items),
        "index_path": str(index_path),
        "cache_path": str(cache_path),
        "daily_tracker_path": str(tracker_path_for(notes_root)),
        "recorded_today_count": daily_tracker["count"],
    }


def load_cache(notes_root: Path, domain: str) -> dict[str, object] | None:
    cache_path = notes_root / domain / CACHE_FILE_NAME
    if not cache_path.exists():
        return None
    return json.loads(cache_path.read_text(encoding="utf-8"))


def load_prior_record_dates(notes_root: Path, domain: str) -> dict[tuple[str, str], str]:
    cache = load_cache(notes_root, domain)
    if cache is None:
        return {}

    prior_dates: dict[tuple[str, str], str] = {}
    for item in cache.get("items", []):
        note_file = item.get("note_file")
        question_id = item.get("question_id")
        record_date = (item.get("record_date") or "").strip()
        if not note_file or not question_id or not record_date or record_date == "未知":
            continue
        prior_dates[(note_file, question_id)] = record_date
    return prior_dates


def discover_domains(notes_root: Path) -> list[Path]:
    domain_dirs: list[Path] = []
    for child in sorted(notes_root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if (child / ".index.md").exists() or any(child.glob("*.md")):
            domain_dirs.append(child)
    return domain_dirs


def tracker_path_for(notes_root: Path) -> Path:
    return notes_root / DAILY_TRACKER_FILE_NAME


def load_daily_tracker(notes_root: Path) -> dict[str, object] | None:
    tracker_path = tracker_path_for(notes_root)
    if not tracker_path.exists():
        return None
    return json.loads(tracker_path.read_text(encoding="utf-8"))


def write_daily_tracker(notes_root: Path, payload: dict[str, object]) -> Path:
    tracker_path = tracker_path_for(notes_root)
    tracker_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return tracker_path


def cache_items_to_note_items(domain: str, items: list[dict[str, object]]) -> list[NoteItem]:
    return [
        NoteItem(
            domain=item.get("domain", domain),
            note_file=item["note_file"],
            question_id=item["question_id"],
            title=item["title"],
            tags=list(item.get("tags", [])),
            record_date=item.get("record_date", "未知"),
            next_review=item.get("next_review", "未知"),
            last_review=item.get("last_review", "-"),
            review_count=normalize_count(str(item.get("review_count", 0))),
            answer=item.get("answer", ""),
            explanation=item.get("explanation", ""),
        )
        for item in items
    ]


def collect_today_entries(notes_root: Path, today: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for domain_dir in discover_domains(notes_root):
        cache = load_cache(notes_root, domain_dir.name)
        if cache is None:
            items = scan_domain(domain_dir, load_prior_record_dates(notes_root, domain_dir.name))
        else:
            items = cache_items_to_note_items(domain_dir.name, list(cache.get("items", [])))

        for item in items:
            if item.record_date != today:
                continue
            entries.append(
                {
                    "key": note_item_key(item.domain, item.note_file, item.question_id),
                    "domain": item.domain,
                    "note_file": item.note_file,
                    "question_id": item.question_id,
                    "title": item.title,
                    "record_date": item.record_date,
                }
            )
    entries.sort(key=lambda item: str(item["key"]))
    return entries


def refresh_daily_tracker(notes_root: Path, today: str) -> dict[str, object]:
    tracker = load_daily_tracker(notes_root)
    tracker_path = tracker_path_for(notes_root)
    if tracker is not None and tracker.get("today") == today:
        return tracker

    if tracker is not None and tracker_path.exists():
        tracker_path.unlink()

    items = collect_today_entries(notes_root, today)
    payload = {
        "today": today,
        "count": len(items),
        "items": items,
    }
    write_daily_tracker(notes_root, payload)
    return payload


def update_daily_tracker_for_domain(notes_root: Path, today: str, domain: str, items: list[NoteItem]) -> dict[str, object]:
    tracker = refresh_daily_tracker(notes_root, today)
    preserved_items = [item for item in tracker.get("items", []) if item.get("domain") != domain]

    current_domain_items = [
        {
            "key": note_item_key(item.domain, item.note_file, item.question_id),
            "domain": item.domain,
            "note_file": item.note_file,
            "question_id": item.question_id,
            "title": item.title,
            "record_date": item.record_date,
        }
        for item in items
        if item.record_date == today
    ]

    merged: dict[str, dict[str, object]] = {}
    for entry in preserved_items + current_domain_items:
        merged[str(entry["key"])] = entry

    payload = {
        "today": today,
        "count": len(merged),
        "items": [merged[key] for key in sorted(merged)],
    }
    write_daily_tracker(notes_root, payload)
    return payload


def handle_sync(args: argparse.Namespace) -> int:
    notes_root = Path(args.notes_root).resolve()
    payload = sync_domain(notes_root, args.domain, args.today)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def handle_list(args: argparse.Namespace) -> int:
    notes_root = Path(args.notes_root).resolve()
    cache = load_cache(notes_root, args.domain)
    if cache is None and args.sync_if_missing:
        today = args.today or datetime.now().strftime(DATE_FMT)
        sync_domain(notes_root, args.domain, today)
        cache = load_cache(notes_root, args.domain)

    if cache is None:
        payload = {
            "domain": args.domain,
            "count": 0,
            "recorded_today_count": refresh_daily_tracker(notes_root, args.today)["count"] if args.today else None,
            "items": [],
            "source": "missing",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    items = [
        item.to_list_dict()
        for item in cache_items_to_note_items(args.domain, list(cache.get("items", [])))
    ]

    recorded_today_count = None
    if args.today:
        recorded_today_count = refresh_daily_tracker(notes_root, args.today)["count"]

    payload = {
        "domain": args.domain,
        "count": len(items),
        "recorded_today_count": recorded_today_count,
        "items": items,
        "source": "cache",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "sync":
        return handle_sync(args)
    if args.command == "list":
        return handle_list(args)
    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
