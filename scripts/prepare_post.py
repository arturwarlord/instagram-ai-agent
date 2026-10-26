"""Prepare a reviewed Instagram post and optionally enable Metricool scheduling."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SELECTED_DIR = Path("content/selected")
CAPTIONS_DIR = Path("content/captions")
QUEUE_DIR = Path("content/queue")


def _parse_utc(value, now=None):
    try:
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        parsed = datetime.fromisoformat(normalized)
    except (AttributeError, ValueError) as error:
        raise ValueError("Use an ISO timestamp such as 2026-10-28T15:00:00Z.") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("The schedule must include a timezone, preferably Z for UTC.")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError("Use a UTC time ending in Z or +00:00.")
    parsed = parsed.astimezone(timezone.utc)
    current = now or datetime.now(timezone.utc)
    if parsed <= current:
        raise ValueError("The scheduled time must be in the future.")
    return parsed


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n", ""}:
        return False
    raise ValueError("Automatic publishing option must be true or false.")


def prepare_post(filename, scheduled_at, selected_dir=SELECTED_DIR,
                 captions_dir=CAPTIONS_DIR, queue_dir=QUEUE_DIR, now=None,
                 publishing_enabled=False):
    if not filename or Path(filename).name != filename or filename in {".", ".."}:
        raise ValueError("Provide only the image filename, not a path.")
    if not filename.lower().endswith(".png"):
        raise ValueError("Only PNG images can be queued.")
    publishing_enabled = _parse_bool(publishing_enabled)
    image_path = selected_dir / filename
    if not image_path.is_file():
        raise FileNotFoundError("Selected photo not found: " + str(image_path))
    caption_path = captions_dir / (Path(filename).stem + ".json")
    if not caption_path.is_file():
        raise FileNotFoundError("Caption draft not found: " + str(caption_path))
    try:
        caption_record = json.loads(caption_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Caption draft is unreadable or invalid JSON.") from error
    if not isinstance(caption_record, dict):
        raise ValueError("Caption draft must contain a JSON object.")
    if caption_record.get("image") != filename:
        raise ValueError("Caption draft references a different image.")
    if caption_record.get("status") != "draft_not_published":
        raise ValueError("Only unpublished caption drafts can be queued.")
    caption = caption_record.get("caption")
    hashtags = caption_record.get("hashtags")
    if not isinstance(caption, str) or not caption.strip():
        raise ValueError("Caption draft has no usable caption text.")
    if not isinstance(hashtags, list) or any(not isinstance(tag, str) for tag in hashtags):
        raise ValueError("Caption draft hashtags must be a list of strings.")
    scheduled = _parse_utc(scheduled_at, now=now)
    queue_dir.mkdir(parents=True, exist_ok=True)
    destination = queue_dir / (Path(filename).stem + ".json")
    if destination.exists():
        raise FileExistsError("Queue entry already exists: " + str(destination))
    created = now or datetime.now(timezone.utc)
    record = {
        "image": filename,
        "caption": caption.strip(),
        "hashtags": hashtags,
        "scheduled_at_utc": scheduled.isoformat().replace("+00:00", "Z"),
        "status": "queued_for_metricool" if publishing_enabled else "queued_not_published",
        "publishing_enabled": publishing_enabled,
        "created_at_utc": created.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    destination.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination, record


def main():
    if len(sys.argv) not in {3, 4}:
        raise SystemExit(
            "Usage: python scripts/prepare_post.py <selected-image.png> "
            "<scheduled-at-UTC> [enable-metricool-publishing true|false]"
        )
    try:
        enabled = _parse_bool(sys.argv[3]) if len(sys.argv) == 4 else False
        destination, record = prepare_post(sys.argv[1], sys.argv[2],
                                           publishing_enabled=enabled)
    except (ValueError, FileNotFoundError, FileExistsError) as error:
        raise SystemExit("Queue preparation failed: " + str(error)) from error
    print("Queue entry saved: " + str(destination))
    if record["publishing_enabled"]:
        print("Status: enabled for Metricool scheduling; it will be submitted by the Metricool sync workflow.")
    else:
        print("Status: draft only; no publishing is enabled.")
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
