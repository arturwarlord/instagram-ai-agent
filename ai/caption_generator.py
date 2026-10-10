import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://gen.pollinations.ai/v1/chat/completions"
MODEL = "openai/gpt-5.4-nano"
POSTS_DIR = Path("content/posts")
HISTORY_FILE = Path("data/caption_history.json")


def _load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _clean_caption(text):
    text = (text or "").strip()
    text = re.sub(r"^\s*\`\`\`(?:text)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*\`\`\`\s*$", "", text)
    return text.strip().strip('"').strip()


def generate_caption(image_info):
    api_key = os.getenv("POLLINATIONS_API_KEY")
    if not api_key:
        raise RuntimeError("❌ POLLINATIONS_API_KEY is not configured")

    history = _load_history()
    previous = "\n".join(
        f"- {item.get('caption', '')}" for item in history[-20:] if item.get("caption")
    ) or "- пока нет"

    system_prompt = """
Ты — редактор Instagram Алисии, 21-летней вымышленной девушки.
Пиши от первого лица, как реальная современная девушка.

Стиль: живой разговорный русский, естественно, легко, иногда с лёгкой
самоиронией. Не рекламный текст и не литературная поэзия.
Не описывай фотографию буквально. Не используй клише вроде
«ловлю моменты», «маленькие радости жизни», «наслаждаюсь каждым мгновением».
Не упоминай ИИ. Не повторяй прошлые подписи.
Максимум 2–3 эмодзи. В конце 3–5 уместных хэштегов.
Верни только готовую подпись без пояснений.
""".strip()

    user_prompt = f"""
Новая фотография:
Сцена: {image_info["scene"]}
Действие: {image_info["action"]}
Настроение: {image_info["mood"]}
Одежда: {image_info["outfit"]}

Последние подписи, которые нельзя повторять:
{previous}

Сделай одну свежую подпись, которая звучит как обычный пост Алисии.
""".strip()

    print("✍️ Generating Alicia caption...")

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.9,
                "max_tokens": 220,
            },
            timeout=120,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"❌ Pollinations caption error {response.status_code}: {response.text[:1500]}"
            )

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"❌ No caption returned: {json.dumps(data)[:1500]}")

        caption = _clean_caption(
            choices[0].get("message", {}).get("content", "")
        )
        if not caption:
            raise RuntimeError("❌ Pollinations returned an empty caption")

        POSTS_DIR.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now(timezone.utc).isoformat()

        post = {
            **image_info,
            "caption": caption,
            "created_at": created_at,
        }

        post_file = POSTS_DIR / "alicia_test.json"
        post_file.write_text(
            json.dumps(post, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        history.append({"caption": caption, "created_at": created_at})
        _save_history(history)

        print("✅ Caption generated:")
        print(caption)
        print(f"📝 Post saved: {post_file}")

        return post

    except requests.RequestException as error:
        raise RuntimeError(
            f"❌ Network error while generating caption: {error}"
        ) from error
