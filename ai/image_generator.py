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
A highly realistic candid smartphone photograph
of a real 21-year-old adult woman named Alicia.

She looks like a normal real young woman,
not a model, influencer or AI-generated character.

APPEARANCE:

A 21-year-old woman with medium-length
dark brown hair.

Natural slightly messy straight hair,
falling naturally around her face.

Brown eyes.

Fair natural skin.

Slim natural body.

Average natural facial proportions.

Soft oval face.

She has an ordinary, believable appearance.

She is not styled to look exceptionally beautiful.

Her appearance is interesting because
she looks like a real individual person,
not because of perfect facial features.

Her face has ordinary human characteristics
and natural individual variation.

She does not look like a fashion model.

She does not have a perfect face.

Her appearance should feel believable
and completely ordinary.

Do not idealize her facial features.

Do not make her look like a celebrity.

Do not make her look like an Instagram influencer.

Do not make her look like a commercial model.

SKIN:

Unretouched real human skin.

Natural visible skin texture.

Visible pores, especially around the nose,
cheeks and forehead.

Subtle uneven skin texture.

Very small natural blemishes.

Tiny imperfections and minor variations
in skin tone.

Some areas of the skin are slightly smoother
while other areas have more visible texture.

Very subtle redness around the nose and cheeks.

Natural under-eye texture.

Natural skin creases.

Natural variation in skin color.

The skin must NOT look smooth or polished.

The skin must NOT look airbrushed.

The skin must NOT look porcelain.

The skin must NOT look waxy.

The skin must NOT look plastic.

The skin must NOT look digitally retouched.

No beauty filter.

No skin smoothing.

No flawless complexion.

No perfect skin.

No artificial skin texture.

The photograph should preserve
the natural texture of real young adult skin.

HAIR:

Medium-length dark brown hair.

Natural straight hair.

A few loose strands.

Natural hair volume.

Slightly imperfect everyday hairstyle.

No salon-perfect hairstyle.

FACE:

An ordinary real human face.

Natural facial proportions with normal
individual variation.

The face should NOT look symmetrical or perfectly balanced.

Natural differences between the two sides of the face.

Normal human nose with a slightly individual shape.

Natural lips with ordinary proportions.

Natural cheeks and jawline.

Natural eyebrows with slightly uneven shape.

The face should have small ordinary characteristics
that make it look like a specific real person.

Do not make the face conventionally beautiful.

Do not make the facial features perfectly aligned.

Do not make the nose perfectly straight.

Do not make the lips perfectly symmetrical.

Do not make the jawline perfectly defined.

Do not make the cheekbones sculpted.

Do not create a beauty-model face.

Do not create an Instagram-model face.

Do not create a celebrity face.

Do not create a generic AI beauty face.

The face should look like a completely ordinary
21-year-old woman photographed unexpectedly
during everyday life.

CLOTHING:

Simple everyday casual clothing.

Plain fitted T-shirt.

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

Cars parked on the street.

A few distant pedestrians.

Natural everyday environment.

Nothing cinematic or spectacular.

The photograph should look like
a friend casually photographed her
while they were walking around the city.

She is not posing for a photoshoot.

CAMERA:

Photographed with a modern smartphone.

Real smartphone photograph.

Natural smartphone perspective.

Natural exposure.

Natural colors.

Natural contrast.

Subtle realistic digital camera noise.

Slight natural motion softness.

Normal smartphone image quality.

No professional photography.

No studio photography.

No fashion photography.

No cinematic photography.

No HDR.

No excessive sharpening.

No artificial depth of field.

No beauty mode.

No face enhancement.

No skin smoothing.

No artificial bokeh.

LIGHTING:

Ordinary natural daylight.

Soft overcast afternoon light.

Natural shadows.

Natural illumination across the face.

No studio lighting.

No dramatic lighting.

No glamour lighting.

No cinematic lighting.

No artificial glow.

PHOTOGRAPHIC REALISM:

The image must look like
a real photograph taken by an ordinary person.

It should feel like a random photo
from someone's smartphone gallery.

Natural human appearance.

Natural skin.

Natural hair.

Natural eyes.

Natural facial proportions.

Natural body proportions.

Natural lighting.

Natural environment.

The viewer should believe
this is a real person.

Avoid all signs of AI-generated imagery.

No CGI.

No 3D rendering.

No illustration.

No digital painting.

No fantasy.

No unrealistically perfect beauty.

No generic AI influencer appearance.

No commercial beauty photography.

No fashion campaign.

Vertical 4:5 photograph.

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
