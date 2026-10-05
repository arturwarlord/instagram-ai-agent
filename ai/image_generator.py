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
A candid smartphone photograph of a real 21-year-old adult woman
named Alicia.

Alicia has short straight black bob hair,
green eyes,
fair skin,
and a slim natural body.

She looks like an ordinary real young woman,
not a professional model.

FACE:

A completely natural individual human face.

The face should NOT look designed or idealized.

Use ordinary realistic human facial proportions.

The facial features should have natural variation
and subtle asymmetry.

The nose is an ordinary natural human nose,
with realistic width, length and shape.

Do not make the nose tiny,
perfectly straight,
perfectly sculpted,
or cosmetically enhanced.

The lips have an ordinary natural human shape.

Natural lip thickness and natural lip proportions.

Do not make the lips oversized,
perfectly symmetrical,
perfectly outlined,
or cosmetically enhanced.

Do not create a beauty-model nose.

Do not create influencer-style lips.

Do not create exaggerated facial features.

Do not make the cheekbones exaggerated.

Do not make the jawline extremely sharp.

Do not make the face perfectly symmetrical.

The face should look like an individual person
who could realistically exist in everyday life.

Her appearance should be attractive in a normal,
unremarkable human way.

EYES:

Natural realistic human green eyes.

Normal human eye size and proportions.

Natural almond-shaped eyes with soft,
realistic eyelids.

The eyes should fit naturally into the face.

Natural green iris color with subtle variations
of green and brown tones.

Realistic iris texture and natural pupil size.

Soft natural reflections from daylight.

Natural eyelashes.

Natural eyelids and subtle skin texture
around the eyes.

The eyes should look relaxed and alive,
like a real person photographed with a smartphone.

No exaggerated eye size.

No unnaturally bright green color.

No glowing eyes.

No doll-like eyes.

No anime eyes.

No artificial glossy effect.

No exaggerated eyelashes.

SKIN:

Natural young adult skin.

Real photographic skin texture.

Subtle natural variation in skin tone.

Very slight natural redness around the cheeks and nose.

Small natural imperfections.

No beauty filter.

No airbrushing.

No skin smoothing.

No porcelain skin.

No waxy skin.

No plastic appearance.

No artificial facial retouching.

No flawless digital skin.

HAIR:

Short straight black bob haircut.

Natural individual hair strands.

Some strands slightly out of place.

Natural hair volume.

No perfectly arranged hairstyle.

EXPRESSION:

A relaxed natural expression.

A very subtle smile.

No exaggerated smile.

No posed influencer expression.

No seductive expression.

No exaggerated facial expression.

She is looking slightly beside the camera.

Her head is naturally turned a little to one side.

SCENE:

Alicia is sitting at a small outdoor cafe
on an ordinary European city street.

A friend is taking the photograph casually
with a modern smartphone.

It feels like a spontaneous photograph
from someone's personal phone.

She is not posing for a professional photoshoot.

She is not on a fashion set.

CLOTHING:

Simple modern everyday clothing.

A fitted neutral-colored top,
casual jeans,
minimal accessories.

Fashionable but ordinary.

LIGHTING:

Natural afternoon daylight.

Soft daylight from one side.

Natural shadows on the face.

Slightly uneven natural illumination.

No studio lighting.

No beauty lighting.

No glamour lighting.

No cinematic lighting.

No artificial glow.

CAMERA:

Modern smartphone camera.

Natural smartphone lens perspective.

Approximately 35mm equivalent.

Natural exposure.

Natural colors.

Natural dynamic range.

Very subtle smartphone image noise.

Very subtle photographic grain.

No HDR.

No excessive sharpening.

No beauty mode.

No portrait mode skin smoothing.

No face enhancement.

No artificial bokeh.

No professional retouching.

BACKGROUND:

A real European cafe street.

Tables and chairs.

Buildings.

Cars.

Several distant pedestrians.

Natural environmental details.

Moderate depth of field.

The background should remain recognizable.

FINAL RESULT:

The photograph must look like an ordinary,
unedited photograph of one real person.

Natural human face.

Natural nose.

Natural lips.

Natural eyes.

Natural skin.

Natural hair.

Natural body proportions.

Natural expression.

Natural lighting.

Natural environment.

No idealized beauty standards.

No artificial perfection.

No generic AI influencer appearance.

No CGI.

No 3D rendering.

No illustration.

No fantasy appearance.

No commercial beauty photography.

No fashion campaign.

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

