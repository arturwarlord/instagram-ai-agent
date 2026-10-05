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
An authentic unedited photograph of a real 21-year-old adult woman
named Alicia.

She is a naturally attractive young woman
with short straight black bob hair,
green eyes,
fair skin,
and a slim natural figure.

IMPORTANT:

Her face must look like a real individual human face,
not a generic beauty-model face.

She has natural individual facial characteristics.

Her facial features are slightly asymmetrical,
subtle and ordinary.

Her eyes are naturally positioned
with small realistic differences between the two sides of the face.

Her nose has natural individual proportions.

Her lips have natural shape and volume.

Her cheeks and jaw have natural human asymmetry.

Her face is not perfectly symmetrical.

Her facial proportions should look ordinary and believable,
like a real person photographed casually.

Do not make her face exceptionally perfect.

Do not make her look like a fashion model.

Do not make her look like a beauty advertisement.

Do not exaggerate any facial feature.

Do not create an idealized female face.

Do not create a generic AI influencer face.

Do not create an overly symmetrical face.

Do not create huge eyes.

Do not create a tiny nose.

Do not create perfectly shaped lips.

Do not create a perfectly defined jawline.

Do not create porcelain skin.

The face should have the natural complexity
and subtle irregularity of an actual human face.

SCENE:

Alicia is sitting outside a small European cafe
on an ordinary afternoon.

A friend is casually taking a photograph of her
with a modern smartphone.

She is not posing for a professional photoshoot.

Her body is naturally relaxed.

Her shoulders are slightly uneven.

Her head is turned slightly to one side.

She is looking just beside the camera.

She has a small natural smile.

Her expression is relaxed and spontaneous.

CLOTHING:

Simple modern casual clothing.

A fitted neutral top,
casual jeans,
minimal accessories.

Fashionable but ordinary.

LIGHT:

Natural outdoor daylight.

Soft light from the side.

Natural shadows across the face.

Slight variation in illumination.

No studio lighting.

No beauty lighting.

No glamour lighting.

No cinematic lighting.

CAMERA:

Normal modern smartphone camera.

Natural 35mm equivalent perspective.

Realistic smartphone exposure.

Natural colors.

Natural dynamic range.

Very subtle digital camera noise.

Very subtle photographic grain.

No HDR.

No excessive sharpening.

No beauty mode.

No portrait mode skin processing.

No face enhancement.

No artificial skin smoothing.

The photograph should look like
an ordinary photograph from someone's phone.

BACKGROUND:

Real European cafe and street.

Tables.

Chairs.

Buildings.

Cars.

A few distant pedestrians.

Natural environmental details.

Moderate depth of field.

The background is recognizable
but not distracting.

PHOTOGRAPHIC RESULT:

Real individual person.

Real human face.

Natural facial asymmetry.

Natural expression.

Natural skin.

Natural hair.

Natural anatomy.

Natural proportions.

Natural lighting.

Natural environment.

Unedited smartphone photograph.

The image should feel completely ordinary
and believable.

It should look like a photograph of a real person
rather than a generated portrait.

Vertical 4:5 Instagram photograph.

No text.
No logo.
No watermark.
"""

    print("🎨 Generating natural Alicia...")

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
