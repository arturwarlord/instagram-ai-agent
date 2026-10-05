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
A highly realistic lifestyle photograph of Alicia,
a 21-year-old adult woman and attractive modern Instagram influencer.

Alicia has:
short straight black bob haircut,
natural green eyes,
fair skin,
slim feminine body,
soft attractive facial features,
natural youthful appearance.

She has a naturally beautiful face,
balanced facial proportions,
subtle facial asymmetry,
natural lips,
natural eyebrows,
realistic eyes,
healthy natural skin texture.

Her appearance is attractive and polished,
but still believable and human.

She is wearing a stylish modern casual outfit:
a fitted elegant top,
high-waisted jeans,
minimal fashionable accessories.

The outfit is fashionable and flattering,
but completely appropriate for a lifestyle Instagram account.

SCENE:

Alicia is sitting at an outdoor cafe
on a beautiful European city street.

She is relaxed and confident.

Her posture is natural and feminine.
She is slightly turned toward the camera.

She has a subtle confident smile
and a relaxed expressive look.

She looks like a real young adult woman
who is naturally comfortable in front of a camera.

PHOTOGRAPHY:

The photograph was taken casually by a friend
using a modern smartphone.

Natural afternoon daylight.

Realistic exposure.
Natural shadows.
Natural reflections.
Natural skin tones.
Natural hair texture.
Natural fabric texture.

Slightly imperfect smartphone photography.

Realistic camera perspective.

Moderate depth of field.

The background contains a real European cafe,
tables, chairs, pedestrians and city architecture.

The environment should feel completely authentic
and naturally photographed.

The photograph should resemble
a genuine Instagram photo taken in everyday life.

IMPORTANT:

Natural human appearance.
Natural skin.
Natural facial proportions.
Natural body proportions.
Natural hair strands.
Natural clothing folds.
Natural lighting.

Do not make her look like a professional fashion model.

Do not make the image look like a commercial advertising campaign.

Do not use excessive beauty retouching.

Do not make the skin perfectly smooth.

Do not make the face perfectly symmetrical.

Do not use artificial studio lighting.

Do not use dramatic cinematic lighting.

Do not use exaggerated makeup.

Do not use plastic-looking skin.

Do not use doll-like facial features.

Do not use CGI aesthetics.

Do not use 3D rendering.

Do not use illustration.

Do not use anime style.

Do not use fantasy aesthetics.

Do not use excessive HDR.

Do not use excessive sharpening.

Do not create an artificial perfect Instagram influencer look.

The result should look like an authentic photograph
of a real adult woman taken spontaneously
during an ordinary day in Europe.

Vertical Instagram photograph.
4:5 aspect ratio.

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
