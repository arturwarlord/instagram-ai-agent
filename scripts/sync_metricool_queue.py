"""Submit explicitly enabled Alicia photo queue entries to Metricool."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

API_BASE = "https://app.metricool.com/api"
QUEUE_DIR = Path("content/queue")
SELECTED_DIR = Path("content/selected")
IMAGE_BASE = "https://raw.githubusercontent.com/arturwarlord/instagram-ai-agent/main/content/selected"
PENDING_STATUSES = {"queued_for_metricool", "queued_not_published"}


def parse_scheduled_time(value, now=None):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Queue entry has no scheduled_at_utc timestamp.")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        scheduled = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("scheduled_at_utc must be an ISO 8601 UTC timestamp.") from exc
    if scheduled.tzinfo is None or scheduled.utcoffset() is None:
        raise ValueError("scheduled_at_utc must include a timezone, preferably Z.")
    if scheduled.utcoffset().total_seconds() != 0:
        raise ValueError("scheduled_at_utc must use UTC (Z or +00:00).")
    scheduled = scheduled.astimezone(timezone.utc)
    current = now or datetime.now(timezone.utc)
    if scheduled <= current.astimezone(timezone.utc):
        raise ValueError("The scheduled time must still be in the future.")
    return scheduled


def build_image_url(filename, base_url=IMAGE_BASE):
    if not filename or Path(filename).name != filename or filename in {".", ".."}:
        raise ValueError("Image must be a filename, not a path.")
    if not filename.lower().endswith(".png"):
        raise ValueError("Only selected PNG photos can be scheduled.")
    return base_url.rstrip("/") + "/" + quote(filename, safe="")


def caption_text(record):
    caption = record.get("caption")
    hashtags = record.get("hashtags", [])
    if not isinstance(caption, str) or not caption.strip():
        raise ValueError("Queue entry has no caption.")
    if not isinstance(hashtags, list) or any(not isinstance(tag, str) for tag in hashtags):
        raise ValueError("Queue entry hashtags must be a list of strings.")
    tags = [tag.strip() for tag in hashtags if tag.strip()]
    output = caption.strip() + (("\n\n" + " ".join(tags)) if tags else "")
    if len(output) > 2200:
        raise ValueError("Instagram caption exceeds 2,200 characters.")
    return output


def credentials(env=None):
    env = env or os.environ
    values = {
        "METRICOOL_API_TOKEN": (env.get("METRICOOL_API_TOKEN") or "").strip(),
        "METRICOOL_USER_ID": (env.get("METRICOOL_USER_ID") or "").strip(),
        "METRICOOL_BLOG_ID": (env.get("METRICOOL_BLOG_ID") or "").strip(),
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing GitHub Actions secrets: " + ", ".join(missing) +
            ". Metricool API access requires an Advanced or Custom plan."
        )
    return values["METRICOOL_API_TOKEN"], values["METRICOOL_USER_ID"], values["METRICOOL_BLOG_ID"]


def api_request(session, method, path, token, user_id, blog_id, params=None, body=None):
    query = {"userId": user_id, "blogId": blog_id}
    query.update(params or {})
    response = session.request(
        method, API_BASE + path, params=query,
        headers={"X-Mc-Auth": token, "Accept": "application/json", "Content-Type": "application/json"},
        json=body, timeout=45,
    )
    if response.status_code >= 400:
        raise RuntimeError(
            f"Metricool API returned HTTP {response.status_code}; check the plan, token, IDs, and request settings."
        )
    try:
        return response.json()
    except (ValueError, AttributeError) as exc:
        raise RuntimeError("Metricool API returned a non-JSON response.") from exc


def find_id(data, keys):
    if isinstance(data, dict):
        for key in keys:
            if data.get(key) is not None and str(data[key]).strip():
                return str(data[key])
        for value in data.values():
            result = find_id(value, keys)
            if result:
                return result
    if isinstance(data, list):
        for value in data:
            result = find_id(value, keys)
            if result:
                return result
    return None


def sync_queue(queue_dir=QUEUE_DIR, selected_dir=SELECTED_DIR, env=None, dry_run=False,
               now=None, session=requests, image_base_url=IMAGE_BASE):
    now = now or datetime.now(timezone.utc)
    queue_dir, selected_dir = Path(queue_dir), Path(selected_dir)
    result = {"submitted": 0, "dry_run": 0, "skipped": 0, "errors": []}
    if not queue_dir.exists():
        print("No queue directory yet; nothing to schedule.")
        return result

    pending = []
    for path in sorted(queue_dir.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(record, dict):
                raise ValueError("Queue JSON must contain an object.")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            result["errors"].append(f"{path.name}: unreadable queue entry ({exc})")
            continue
        if (record.get("publishing_enabled") is True
                and record.get("status") in PENDING_STATUSES):
            pending.append((path, record))
        else:
            result["skipped"] += 1

    if not pending:
        print("No explicitly enabled, unsubmitted Metricool queue entries.")
        return result
    auth = None if dry_run else credentials(env)

    for path, record in pending:
        try:
            filename = record.get("image")
            if not isinstance(filename, str) or not (selected_dir / filename).is_file():
                raise FileNotFoundError(f"Selected image is missing: {filename or '(invalid filename)'}")
            scheduled = parse_scheduled_time(record.get("scheduled_at_utc"), now=now)
            text = caption_text(record)
            image_url = build_image_url(filename, image_base_url)
            if dry_run:
                print(f"DRY RUN: would schedule {filename} for {scheduled.isoformat()}.")
                result["dry_run"] += 1
                continue

            token, user_id, blog_id = auth
            media = api_request(session, "GET", "/actions/normalize/image/url",
                                token, user_id, blog_id, params={"url": image_url})
            media_id = find_id(media, ("mediaId", "media_id", "id"))
            if not media_id:
                raise RuntimeError("Metricool image normalization returned no media ID; verify that the PNG is public.")

            body = {
                "publicationDate": {"dateTime": scheduled.strftime("%Y-%m-%dT%H:%M:%S"), "timezone": "UTC"},
                "text": text,
                "providers": [{"network": "instagram"}],
                "media": {"mediaId": media_id},
                "autoPublish": True,
                "draft": False,
                "saveExternalMediaFiles": True,
                "instagramData": {"autoPublish": True},
            }
            created = api_request(session, "POST", "/v2/scheduler/posts",
                                  token, user_id, blog_id, body=body)
            post_id = find_id(created, ("id", "postId", "post_id", "uuid"))
            if not post_id:
                raise RuntimeError("Metricool returned no scheduled post ID; entry was not marked submitted.")

            record["status"] = "submitted_to_metricool"
            record["metricool_post_id"] = post_id
            record["submitted_at_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            record["metricool_auto_publish"] = True
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Scheduled in Metricool: {filename} at {scheduled.isoformat()} (post ID {post_id}).")
            result["submitted"] += 1
        except (ValueError, OSError, RuntimeError) as exc:
            message = f"{path.name}: {exc}"
            result["errors"].append(message)
            print("ERROR: " + message)
    return result


def main():
    dry_run = os.getenv("DRY_RUN", "false").strip().lower() in {"1", "true", "yes"}
    try:
        result = sync_queue(dry_run=dry_run)
    except RuntimeError as exc:
        print("Metricool queue sync failed: " + str(exc))
        raise SystemExit(1) from exc
    print("Metricool sync: submitted={submitted}, dry_run={dry_run}, skipped={skipped}, errors={errors}".format(
        submitted=result["submitted"], dry_run=result["dry_run"], skipped=result["skipped"],
        errors=len(result["errors"])))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
