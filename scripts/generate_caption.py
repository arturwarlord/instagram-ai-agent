"""Generate a draft Instagram caption for a manually selected Alicia photo."""
import json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
import requests

SELECTED_DIR = Path("content/selected")
CAPTIONS_DIR = Path("content/captions")
MODEL = "@cf/meta/llama-3.1-8b-instruct"
API_URL_TEMPLATE = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/" + MODEL

def _safe_stem(filename):
    if not filename or Path(filename).name != filename or filename in {".", ".."}:
        raise ValueError("Provide only the image filename, not a path.")
    if not filename.lower().endswith(".png"):
        raise ValueError("Only PNG images can have captions generated.")
    return Path(filename).stem

def _extract_text(response):
    try:
        data = response.json()
    except ValueError as error:
        raise RuntimeError("Cloudflare returned an invalid response: " + response.text[:500]) from error
    result = data.get("result") or {}
    text = result.get("response") or result.get("output") or result.get("text")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("Cloudflare returned no caption text: " + json.dumps(data)[:800])
    return text.strip()

def _parse_caption(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    try:
        data = json.loads(text)
        caption = str(data.get("caption", "")).strip()
        hashtags = data.get("hashtags", [])
    except (json.JSONDecodeError, AttributeError):
        caption, hashtags = text, []
    caption = re.sub(r"\n?\s*#\w+", "", caption).strip()
    if not caption:
        raise RuntimeError("The AI returned an empty caption.")
    if not isinstance(hashtags, list):
        hashtags = []
    normalized = []
    for tag in hashtags:
        tag = re.sub(r"[^A-Za-z0-9_]", "", str(tag).lstrip("#"))
        if tag and tag.lower() not in {item.lower() for item in normalized}:
            normalized.append(tag)
        if len(normalized) >= 8:
            break
    return caption, ["#" + tag for tag in normalized]

def generate_caption(filename, selected_dir=SELECTED_DIR, captions_dir=CAPTIONS_DIR, api_key=None, account_id=None, post=None):
    stem = _safe_stem(filename)
    if not (selected_dir / filename).is_file():
        raise FileNotFoundError("Selected photo not found: " + str(selected_dir / filename))
    api_key = api_key or os.getenv("Workers_AI") or os.getenv("CLOUDFLARE_API_TOKEN")
    account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID")
    if not api_key:
        raise RuntimeError("GitHub Secret Workers_AI is not configured")
    if not account_id:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID is not configured")
    prompt = ("Write a natural Instagram caption for a fictional adult lifestyle character named Alicia. "
        "She is an AI-generated character; do not claim the photo documents a real event. "
        "Use a casual, warm, lightly playful voice. Avoid engagement bait, claims about real experiences, "
        "location assumptions, body/appearance ratings, and overly dramatic language. "
        "Write 1-3 short sentences in English, with at most one subtle emoji. Return ONLY valid JSON "
        "with keys caption and hashtags. hashtags must be an array of 5-8 relevant, non-spammy tags "
        "without the # symbol. Do not invent a specific city, product, brand, or event. Filename: " + filename)
    response = (post or requests.post)(API_URL_TEMPLATE.format(account_id=account_id),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        json={"messages":[{"role":"system","content":"Write concise truthful social captions and follow output format exactly."},{"role":"user","content":prompt}], "max_tokens":240, "temperature":0.8}, timeout=90)
    if response.status_code != 200:
        raise RuntimeError("Cloudflare Workers AI error " + str(response.status_code) + ": " + response.text[:1000])
    caption, hashtags = _parse_caption(_extract_text(response))
    captions_dir.mkdir(parents=True, exist_ok=True)
    destination = captions_dir / (stem + ".json")
    if destination.exists():
        raise FileExistsError("Caption already exists: " + str(destination) + ". Remove it manually to regenerate.")
    record = {"image":filename,"caption":caption,"hashtags":hashtags,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"status":"draft_not_published"}
    destination.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    return destination, record

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/generate_caption.py <selected-image.png>")
    try:
        destination, record = generate_caption(sys.argv[1])
    except (ValueError, FileNotFoundError, FileExistsError, RuntimeError, requests.RequestException) as error:
        raise SystemExit("Caption generation failed: " + str(error)) from error
    print("Draft caption saved: " + str(destination))
    print("Status: draft only; nothing was published.")
    print(json.dumps(record, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
