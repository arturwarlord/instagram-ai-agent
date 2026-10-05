import os
from pathlib import Path
from urllib.parse import quote


import requests


OUTPUT_DIR = Path("content/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "https://gen.pollinations.ai/image"


def generate_image():
    api_key = os.getenv("POLLINATIONS_API_KEY")

    if not api_key:
        raise RuntimeError(
            "❌ POLLINATIONS_API_KEY is not configured"
        )

    prompt = """
A casual unposed photograph of a 21-year-old woman named Alicia.

She has:
short straight black bob haircut,
green eyes,
fair skin,
slim natural body,
soft youthful facial features.

She is wearing simple modern everyday clothes:
a fitted neutral-colored top and casual jeans.

Alicia is standing outside a small cafe on an ordinary European city street
in the afternoon.

She is not posing for a photoshoot.
She is not looking directly at the camera.
Her body is slightly turned away.
Her expression is relaxed and spontaneous,
with a very subtle natural smile.

The photograph looks like a normal photo taken by a friend
using a recent smartphone.

Natural overcast daylight.
Normal street lighting.
Natural shadows.
Natural colors.
Realistic skin.
Natural hair.
Natural clothing folds.
Natural human proportions.

The composition is slightly imperfect,
like a real spontaneous photograph.

Medium shot from approximately chest level.
35mm smartphone camera perspective.
Moderate depth of field.

Everyday street background with cafes,
cars and pedestrians slightly out of focus.

Authentic lifestyle photography.
Natural candid photography.
Unedited photographic appearance.

No studio.
No professional photoshoot.
No glamour photography.
No beauty campaign.
No fashion editorial.

Vertical 4:5 photograph.
No text.
No logo.
No watermark.
"""

    print("🎨 Generating Alicia...")

    encoded_prompt = quote(" ".join(prompt.split()))

    url = (
        f"{API_URL}/{encoded_prompt}"
        "?model=flux"
        "&width=1024"
        "&height=1280"
        "&nologo=true"
    )

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            timeout=180,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"❌ Pollinations error "
                f"{response.status_code}: {response.text[:1000]}"
            )

        if not response.content:
            raise RuntimeError(
                "❌ Pollinations returned an empty image"
            )

        output_file = OUTPUT_DIR / "alicia_test.jpg"
        output_file.write_bytes(response.content)

        print(f"✅ Image saved: {output_file}")
        print(
            f"📦 Size: "
            f"{output_file.stat().st_size / 1024:.1f} KB"
        )

    except requests.RequestException as error:
        raise RuntimeError(
            f"❌ Network error while generating image: {error}"
        ) from error


if __name__ == "__main__":
    generate_image()
