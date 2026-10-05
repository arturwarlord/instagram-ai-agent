import base64
import json
import os
import re
from pathlib import Path

import requests


OUTPUT_DIR = Path("content/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_IMAGE = Path("character/reference/alicia.jpg")
API_URL = "https://gen.pollinations.ai/v1/images/edits"
MODEL = "black-forest-labs/flux.1-kontext-pro"


def _extract_image(response):
    content_type = response.headers.get("content-type", "").lower()

    if content_type.startswith("image/"):
        return response.content

    try:
        data = response.json()
    except ValueError as error:
        raise RuntimeError(
            f"❌ Pollinations returned an unexpected response: "
            f"{response.text[:1000]}"
        ) from error

    items = data.get("data") or []
    if not items:
        raise RuntimeError(
            f"❌ Pollinations returned no image: {json.dumps(data)[:1500]}"
        )

    item = items[0]

    b64 = item.get("b64_json")
    if b64:
        return base64.b64decode(b64)

    image_url = item.get("url")
    if image_url:
        image_response = requests.get(image_url, timeout=180)
        image_response.raise_for_status()
        return image_response.content

    raise RuntimeError(
        f"❌ Pollinations response does not contain an image: "
        f"{json.dumps(item)[:1500]}"
    )


def generate_image():
    api_key = os.getenv("POLLINATIONS_API_KEY")

    if not api_key:
        raise RuntimeError("❌ POLLINATIONS_API_KEY is not configured")

    if not REFERENCE_IMAGE.exists():
        raise RuntimeError(
            f"❌ Alicia reference image not found: {REFERENCE_IMAGE}"
        )

    prompt = """
Use the supplied reference photo as the identity reference for Alicia.

Create a new photorealistic everyday smartphone photograph of the SAME
adult woman from the reference image.

IDENTITY PRIORITY:
Preserve her recognizable identity from the reference:
same face, same natural facial proportions, same eyes, same nose, same lips,
same eyebrows, same skin tone, same dark-brown medium-length hair and the
same overall natural appearance.

Do NOT redesign her face.
Do NOT make her more beautiful.
Do NOT make her younger or older.
Do NOT turn her into a model, celebrity or generic AI woman.

The reference image is the source of truth for her appearance.

NEW SCENE:
Alicia is walking through a quiet European city street in early autumn.
She has just left a small cafe and is casually holding a takeaway coffee.
She wears a simple dark oversized knit sweater, straight jeans and minimal
silver jewelry.

She is not posing for a professional photoshoot. The photo looks like a
friend casually took it with a modern smartphone.

PHOTOGRAPHY:
Natural daylight, realistic ambient light, ordinary smartphone perspective,
natural exposure, realistic colors, slight natural photographic softness,
realistic skin texture, subtle pores and small natural imperfections.

FACE AND SKIN:
Keep the natural face from the reference exactly as the identity anchor.
Natural eyes and eyelids, natural nose, natural lips, natural eyebrows.
Real human skin with normal texture and tiny imperfections.
No beauty filter, no airbrushing, no plastic or porcelain skin,
no excessive smoothing, no face enhancement.

HAIR:
Keep the same dark-brown medium-length hair identity from the reference.
Natural everyday styling, slightly imperfect, not salon-perfect.

IMPORTANT:
Only change the scene, pose, clothing details and environment.
The person herself must remain recognizably the same Alicia.

No CGI, no illustration, no 3D render, no fashion campaign,
no studio portrait, no glamour retouching, no exaggerated facial features,
no text, no logo, no watermark.

Vertical 4:5 composition suitable for an Instagram feed.
"""

    print("🎨 Generating a new Alicia photo using the reference image...")
    print(f"🧬 Identity reference: {REFERENCE_IMAGE}")

    try:
        with REFERENCE_IMAGE.open("rb") as image_file:
            files = {
                "image": (
                    REFERENCE_IMAGE.name,
                    image_file,
                    "image/jpeg",
                )
            }

            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
                data={
                    "model": MODEL,
                    "prompt": " ".join(prompt.split()),
                    "size": "1024x1280",
                    "response_format": "b64_json",
                },
                files=files,
                timeout=300,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"❌ Pollinations error {response.status_code}: "
                f"{response.text[:1500]}"
            )

        image_bytes = _extract_image(response)

        if not image_bytes:
            raise RuntimeError("❌ Pollinations returned an empty image")

        output_file = OUTPUT_DIR / "alicia_test.jpg"
        output_file.write_bytes(image_bytes)

        print(f"✅ Image saved: {output_file}")
        print(
            f"📦 Size: {output_file.stat().st_size / 1024:.1f} KB"
        )

    except requests.RequestException as error:
        raise RuntimeError(
            f"❌ Network error while generating image: {error}"
        ) from error


if __name__ == "__main__":
    generate_image()
