import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from huggingface_hub import InferenceClient

MODEL = "openai/gpt-oss-20b:fastest"
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
    api_key = os.getenv("HF_TOKEN")
    if not api_key:
        raise RuntimeError("❌ HF_TOKEN is not configured")

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
        client = InferenceClient(
            provider="auto",
            api_key=api_key,
        )
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
            max_tokens=220,
        )
        caption = _clean_caption(response.choices[0].message.content or "")
        if not caption:
            raise RuntimeError("❌ Hugging Face returned an empty caption")

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

    except Exception as error:
        message = str(error)
        if "402" in message or "credit" in message.lower() or "payment" in message.lower():
            raise RuntimeError(
                "❌ Hugging Face inference credits may be exhausted or this model requires paid credits. "
                "No paid fallback is configured. Details: " + message[:1200]
            ) from error
        raise RuntimeError(f"❌ Hugging Face caption generation failed: {message[:1500]}") from error