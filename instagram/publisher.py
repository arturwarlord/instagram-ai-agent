import os
import time
from pathlib import Path

import requests


GRAPH_API_VERSION = os.getenv("INSTAGRAM_GRAPH_API_VERSION", "v23.0")
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

IMAGE_PATH = Path("content/generated/alicia_test.jpg")


def _request(method, url, **kwargs):
    response = requests.request(method, url, timeout=60, **kwargs)
    if response.status_code >= 400:
        raise RuntimeError(
            f"❌ Instagram API {response.status_code}: {response.text[:2000]}"
        )
    return response.json()


def publish_post(post):
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = os.getenv("INSTAGRAM_USER_ID")

    if not access_token or not ig_user_id:
        print("ℹ️ Instagram credentials are not configured. Publishing skipped.")
        return None

    public_image_url = os.getenv("INSTAGRAM_IMAGE_URL")
    if not public_image_url:
        raise RuntimeError(
            "❌ INSTAGRAM_IMAGE_URL is not configured. "
            "The image must be publicly reachable by Meta."
        )

    caption = post["caption"]

    print("📤 Creating Instagram media container...")

    container = _request(
        "POST",
        f"{GRAPH_URL}/{ig_user_id}/media",
        data={
            "image_url": public_image_url,
            "caption": caption,
            "access_token": access_token,
        },
    )

    creation_id = container.get("id")
    if not creation_id:
        raise RuntimeError(f"❌ Instagram returned no creation ID: {container}")

    print(f"✅ Container created: {creation_id}")
    print("⏳ Waiting for Instagram container to become ready...")

    for _ in range(12):
        status = _request(
            "GET",
            f"{GRAPH_URL}/{creation_id}",
            params={
                "fields": "status_code",
                "access_token": access_token,
            },
        )

        status_code = status.get("status_code")
        if status_code == "FINISHED":
            break
        if status_code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(
                f"❌ Instagram container failed: {status}"
            )

        time.sleep(5)
    else:
        raise RuntimeError("❌ Instagram container did not become ready in time")

    print("📨 Publishing Instagram post...")

    published = _request(
        "POST",
        f"{GRAPH_URL}/{ig_user_id}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": access_token,
        },
    )

    media_id = published.get("id")
    if not media_id:
        raise RuntimeError(f"❌ Instagram returned no media ID: {published}")

    print(f"🎉 Instagram post published: {media_id}")
    return media_id
