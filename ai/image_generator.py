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
Create an extremely realistic candid smartphone photograph of Alicia,
a 21-year-old slim young woman with fair natural skin,
green eyes and a short black bob haircut.

Alicia is a real-looking young adult woman, not a model,
not a digital character and not a CGI person.

She has a natural human face with subtle asymmetry,
realistic facial proportions, visible natural skin texture,
tiny imperfections, pores, very subtle fine lines,
slightly uneven skin tone and natural lips.

Her black bob haircut should look naturally styled,
with individual hair strands and a few slightly loose strands.

She is wearing modern casual fashion clothing,
stylish but believable everyday clothing.

SCENE:
Alicia is casually walking through a real European city street
during a normal sunny afternoon.

She is looking slightly away from the camera,
with a relaxed natural facial expression and a subtle playful smile.

The photograph should feel spontaneous,
as if a friend took the photo with a modern iPhone.

REAL PHOTOGRAPHY:
natural daylight,
realistic shadows,
realistic reflections,
natural depth of field,
slight smartphone camera imperfections,
subtle exposure variation,
realistic skin tones,
realistic hair,
realistic fabric texture,
natural perspective,
authentic environmental details.

The image must look like an actual photograph taken in real life,
not an AI-generated portrait.

Avoid beauty-retouching.
Avoid perfect skin.
Avoid perfect symmetry.
Avoid studio lighting.
Avoid fashion campaign photography.
Avoid cinematic CGI appearance.

No plastic skin.
No waxy face.
No doll-like appearance.
No 3D rendering.
No illustration.
No anime.
No artificial facial features.
No excessive makeup.
No unrealistic eyes.
No over-sharpening.
No HDR effect.
No fake bokeh.

The person must look naturally photographed,
with believable human anatomy and proportions.

Vertical Instagram portrait photograph,
4:5 composition,
high photographic realism,
natural candid lifestyle photography.

No text.
No logo.
No watermark.
"""

    print("🎨 Generating realistic Alicia...")

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
