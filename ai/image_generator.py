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
A realistic everyday smartphone photograph
of a real 21-year-old adult woman named Alicia.

She looks like a normal young woman
in an ordinary everyday situation.

She does not look like a model,
celebrity or influencer.

APPEARANCE:

21-year-old woman.

Medium-length dark brown hair.

Brown eyes.

Fair skin.

Slim natural body.

Ordinary facial proportions.

Her appearance is normal and believable.

She should look like a real individual person,
not an idealized beauty.

HAIR:

Medium-length dark brown hair.

Simple natural everyday hairstyle.

Straight natural hair.

The hair should look normal and believable
for an ordinary young woman.

No elaborate hairstyle.
No salon styling.
No dramatic volume.
No perfectly arranged hair.
No exaggerated individual hair strands.

FACE:

Ordinary young woman's face.

Natural normal facial proportions.

Normal nose.

Normal lips.

Normal eyes.

Natural eyebrows.

The facial features should look
like normal human features.

Do not emphasize the cheekbones.

Do not sculpt the cheeks.

Do not create sharp cheekbones.

Do not create a strongly defined jawline.

Do not create a model-like face.

Do not create a beauty-model face.

Do not create a celebrity face.

Do not create a generic AI beauty face.

The face should simply look
like a normal real person.

NOSE:

Normal human nose.

Natural ordinary shape.

Normal width and length.

The nose should not attract
special attention in the image.

No tiny nose.
No extremely narrow nose.
No sculpted nose.
No cosmetic-surgery appearance.

LIPS:

Natural ordinary human lips.

Normal lip proportions.

Natural lip shape.

The lips should not attract
special attention in the image.

No oversized lips.
No exaggerated volume.
No filler-like appearance.
No glossy artificial lips.

SKIN:

Normal real human skin.

Natural skin color.

Natural photographic appearance.

The skin should look like
ordinary skin in a smartphone photograph.

No beauty filter.
No airbrushing.
No retouching.
No porcelain skin.
No waxy skin.
No plastic skin.
No artificial skin effect.
No excessive smoothing.

CLOTHING:

Simple everyday casual clothing.

Plain T-shirt.

Light casual jacket.

Simple jeans.

Minimal accessories.

Normal everyday outfit.

No luxury fashion.
No designer clothing.
No glamorous styling.

SCENE:

A normal European city street.

Small outdoor cafe nearby.

Ordinary buildings.

Cars parked nearby.

A few distant pedestrians.

Normal everyday environment.

Nothing spectacular.

The photograph looks like
a friend casually photographed her
while they were walking around the city.

She is not posing for a professional photoshoot.

CAMERA:

Modern smartphone camera.

Ordinary smartphone photograph.

Natural smartphone perspective.

Natural exposure.

Natural colors.

Natural contrast.

Normal smartphone image quality.

Slight natural photographic softness.

No professional photography.

No studio photography.

No fashion photography.

No cinematic photography.

No HDR.

No excessive sharpening.

No beauty mode.

No face enhancement.

No artificial bokeh.

LIGHTING:

Ordinary natural daylight.

Soft daylight.

Natural shadows.

Natural illumination.

No studio lighting.

No dramatic lighting.

No glamour lighting.

No cinematic lighting.

No artificial glow.

OVERALL:

The most important goal is
a believable ordinary human photograph.

The woman should look like
a real person photographed casually
with a smartphone.

The image should not look
like a beauty advertisement.

The image should not look
like a fashion campaign.

The image should not look
like an AI-generated influencer.

Keep the face, hair and skin
simple and natural.

Do not exaggerate facial features.

Do not exaggerate hair.

Do not exaggerate skin texture.

No CGI.

No 3D rendering.

No illustration.

No digital painting.

No fantasy.

No text.

No logo.

No watermark.

Vertical 4:5 photograph.
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
