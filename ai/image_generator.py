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
A genuine everyday smartphone photograph of Alicia,
a 21-year-old adult woman.

Alicia has short straight black bob hair,
green eyes,
fair skin,
and a slim natural figure.

She is an attractive young woman,
but her appearance is completely natural and believable.

She is sitting at a small outdoor cafe
on an ordinary European city street.

A friend is taking a spontaneous photograph of her
with a normal modern smartphone.

This is NOT a portrait session.

This is NOT a professional photoshoot.

The photograph feels accidental and spontaneous,
like a real photo that someone would upload to Instagram
without editing it.

Alicia is wearing a simple fashionable everyday outfit:
a fitted casual top and jeans.

She is relaxed in her chair.
Her shoulders are in a natural position.
Her posture is slightly imperfect.
She is looking just beside the camera.

She has a small relaxed smile.

NATURAL HUMAN SKIN:

Her skin looks like the skin of a real young adult woman
photographed with a smartphone.

Visible natural skin texture.

Very subtle pores.

Subtle variation in skin tone.

Very slight natural redness around the cheeks,
nose and lips.

Tiny natural imperfections.

The skin is not perfectly uniform.

The forehead, cheeks and nose have slightly different texture.

Natural highlights from daylight are visible on the skin.

The skin has realistic fine texture
instead of a smooth digital surface.

No beauty filter.

No skin retouching.

No airbrushing.

No skin smoothing.

No porcelain skin.

No waxy skin.

No plastic skin.

No perfectly flawless complexion.

No artificially blurred skin.

No artificial facial enhancement.

No glamour retouching.

No makeup filter.

Very light natural makeup only.

Her face should have the subtle irregularities
normally visible in an unedited smartphone photograph.

HAIR:

Short black bob haircut.

Natural individual hair strands.

Some strands are slightly out of place.

A few small loose hairs near her face.

Natural hair texture.

No perfectly arranged hairstyle.

LIGHT:

Ordinary natural daylight.

Soft daylight coming from one side.

Slightly uneven illumination across her face.

Natural shadows around the nose,
cheeks and jaw.

The lighting is not perfectly controlled.

There are small natural differences
between illuminated and shadowed areas of her skin.

No studio lighting.

No beauty lighting.

No professional portrait lighting.

No cinematic lighting.

No dramatic rim light.

No artificial glow.

CAMERA:

Modern smartphone camera.

Natural smartphone lens perspective.

Approximately 35mm equivalent perspective.

Normal dynamic range.

Natural exposure.

Slightly imperfect exposure.

Natural digital camera noise.

Very subtle photographic grain.

Natural color rendering.

No HDR effect.

No excessive sharpening.

No beauty mode.

No portrait-mode skin processing.

No artificial bokeh.

No excessive background blur.

The image should look like the original camera photograph
before Instagram filters are applied.

BACKGROUND:

Real European street.

Small cafe.

Tables and chairs.

Several distant pedestrians.

Cars in the background.

Natural buildings.

Realistic environmental details.

The background should contain enough detail
to make the photograph feel like a real location.

Moderate depth of field,
but not excessive blur.

OVERALL:

Authentic smartphone photography.

Unedited lifestyle photograph.

Natural young adult woman.

Natural face.

Natural skin.

Natural hair.

Natural body proportions.

Natural lighting.

Natural environment.

The image should feel ordinary,
believable and spontaneous.

It should look like a photograph
that could genuinely exist in someone's phone gallery.

Do not make it look like an AI portrait.

Do not make it look like a fashion advertisement.

Do not make it look like a beauty campaign.

Do not make it look like a studio photograph.

Do not make it look like a 3D render.

Do not make it look like an illustration.

Vertical photograph.

4:5 Instagram composition.

No text.
No logo.
No watermark.
"""

    print("🎨 Generating natural smartphone photo of Alicia...")

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
