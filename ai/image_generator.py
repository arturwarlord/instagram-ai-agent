import os
from pathlib import Path

import fal_client
import requests


OUTPUT_DIR = Path("content/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_image():
    prompt = """
    Photorealistic Instagram lifestyle photo of Alicia,
    a 21-year-old slim woman with fair skin, black short bob haircut
    and green eyes.

    She has a playful, bold and confident personality.

    Modern casual fashion outfit.
    She is standing in a stylish European city street,
    natural daylight, realistic photography,
    natural skin texture, realistic face,
    high-end Instagram photography,
    candid lifestyle shot.

    Vertical portrait composition, 4:5 aspect ratio.
    No text, no watermark.
    """

    print("🎨 Generating image...")

    result = fal_client.subscribe(
        "fal-ai/flux-pro/kontext",
        arguments={
            "prompt": prompt,
            "aspect_ratio": "4:5"
        }
    )

    images = result.get("images", [])

    if not images:
        raise RuntimeError("❌ FAL returned no images")

    image_url = images[0]["url"]

    print(f"🖼️ Image URL: {image_url}")

    response = requests.get(image_url, timeout=120)
    response.raise_for_status()

    output_file = OUTPUT_DIR / "alicia_test.jpg"
    output_file.write_bytes(response.content)

    print(f"✅ Image saved: {output_file}")


if __name__ == "__main__":
    generate_image()
