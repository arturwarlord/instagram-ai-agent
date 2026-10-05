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
Photorealistic Instagram lifestyle photograph of Alicia,
a 21-year-old slim young woman with fair skin,
black short bob haircut and green eyes.

She has a playful, bold and confident personality.

She is wearing modern casual fashion clothing.

Alicia is walking through a beautiful European city,
natural daylight, realistic photography,
natural skin texture, realistic facial features,
high-end Instagram lifestyle photography,
candid natural pose.

The same person must remain visually consistent.

Vertical Instagram portrait,
4:5 composition.

No text.
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

    output_file = OUTPUT_DIR / "alicia_test.jpg"
    output_file.write_bytes(response.content)

    print(f"✅ Image saved: {output_file}")
    print(f"📦 Size: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    generate_image()
