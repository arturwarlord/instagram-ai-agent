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
A highly realistic casual lifestyle photograph of Alicia,
a 21-year-old adult woman and attractive modern Instagram influencer.

Alicia has:
short straight black bob haircut,
natural green eyes,
fair skin,
slim feminine body,
soft attractive facial features.

She looks like a real young adult woman photographed
during an ordinary day.

FACE AND SKIN:

Natural healthy young adult skin.

The skin has realistic photographic texture
and natural variation across the face.

Subtle natural pores and fine skin texture
are visible when viewed closely.

Slight natural variation in skin tone.

Very subtle natural redness around the cheeks and nose.

Small natural imperfections that occur on real human skin.

The skin is healthy and attractive,
but NOT perfectly smooth.

The face has natural texture,
natural highlights and natural shadows.

Very light everyday makeup,
not heavy makeup.

Natural lips.
Natural eyebrows.
Natural eyelashes.

The face should look attractive without looking retouched.

IMPORTANT SKIN STYLE:

No beauty filter.

No airbrushing.

No skin smoothing.

No porcelain skin.

No plastic skin.

No waxy skin.

No perfectly uniform skin tone.

No flawless artificial complexion.

No excessive makeup.

Do not make the skin look older than 21.

The skin should look like real skin
captured by a good smartphone camera
with no beauty filter.

HAIR:

Short straight black bob haircut.

Individual natural hair strands.

A few slightly loose strands around the face.

Natural hair volume.

No perfectly arranged salon hairstyle.

CLOTHING:

She is wearing a stylish modern casual outfit:
a fitted elegant top,
high-waisted jeans,
minimal fashionable accessories.

The outfit is fashionable and flattering,
but appropriate for a lifestyle Instagram account.

SCENE:

Alicia is sitting at an outdoor cafe
on a beautiful European city street.

She is relaxed and confident.

Her posture is natural and feminine.

She is slightly turned toward the camera.

She has a subtle confident smile
and a relaxed expressive look.

She looks comfortable rather than posed.

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

Realistic smartphone camera rendering.

Slight natural photographic imperfections.

Moderate depth of field.

Natural perspective.

The background contains a real European cafe,
tables, chairs, pedestrians and city architecture.

The environment should feel authentic
and naturally photographed.

The photograph should resemble
a genuine Instagram photo taken in everyday life.

CAMERA:

Modern smartphone camera.

Natural exposure.

Natural dynamic range.

No artificial HDR look.

No excessive sharpening.

No beauty mode.

No portrait mode skin smoothing.

No artificial face enhancement.

No glamour retouching.

The image should look like the original photograph
straight from the smartphone camera.

OVERALL APPEARANCE:

Beautiful but believable.

Attractive but natural.

Well-groomed but not artificially perfect.

Real human face.

Real human skin.

Real human hair.

Real human proportions.

Authentic everyday Instagram lifestyle photography.

Do not make her look like a CGI character.

Do not make her look like a 3D render.

Do not make her look like an illustration.

Do not make her look like an AI-generated beauty portrait.

Do not make the photograph look like a professional advertising campaign.

Vertical Instagram photograph.
4:5 aspect ratio.

No text.
No logo.
No watermark.
"""

    print("🎨 Generating natural-looking Alicia...")

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
