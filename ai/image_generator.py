import base64
import io
import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image


OUTPUT_DIR = Path("content/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_IMAGE = Path("character/reference/alicia.jpg")
HISTORY_FILE = Path("data/generation_history.json")

MODEL = "@cf/black-forest-labs/flux-2-klein-9b"
API_URL_TEMPLATE = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/" + MODEL


SCENES = [
    {
        "id": "cafe_window",
        "location": "a small cozy cafe near a large window",
        "action": "sitting by the window with a coffee and casually looking outside",
        "mood": "quiet late-morning city mood",
    },
    {
        "id": "city_walk",
        "location": "a calm European city street",
        "action": "walking naturally with a takeaway coffee in one hand",
        "mood": "relaxed early-autumn afternoon",
    },
    {
        "id": "bookshop",
        "location": "a small independent bookshop",
        "action": "browsing a shelf and holding an open book",
        "mood": "quiet and curious",
    },
    {
        "id": "train_station",
        "location": "a modern European train station",
        "action": "waiting near the platform with exactly one simple everyday shoulder bag, carried naturally at her side",
        "mood": "casual beginning-of-a-trip feeling",
    },
    {
        "id": "street_bakery",
        "location": "a small neighborhood bakery",
        "action": "standing outside with a paper bag of pastries",
        "mood": "warm ordinary morning",
    },
    {
        "id": "park_walk",
        "location": "a leafy European city park",
        "action": "walking along a path while holding a takeaway drink",
        "mood": "peaceful autumn afternoon",
    },
    {
        "id": "tram_stop",
        "location": "a European tram stop",
        "action": "waiting for a tram and casually checking her phone",
        "mood": "ordinary urban moment",
    },
    {
        "id": "museum",
        "location": "a bright contemporary art museum",
        "action": "standing in front of an artwork and looking at it naturally",
        "mood": "calm weekend outing",
    },
    {
        "id": "hotel_balcony",
        "location": "a modest European hotel balcony",
        "action": "leaning casually on the railing with a morning coffee",
        "mood": "slow travel morning",
    },
    {
        "id": "old_town",
        "location": "a charming old-town street in Europe",
        "action": "walking past small shops and glancing to the side",
        "mood": "casual travel day",
    },
    {
        "id": "riverside",
        "location": "a riverside promenade in a European city",
        "action": "standing near the water with her hands in her sweater pockets",
        "mood": "cool quiet evening",
    },
    {
        "id": "metro",
        "location": "a clean modern metro platform",
        "action": "waiting for a train while holding her phone",
        "mood": "natural everyday commute",
    },
    {
        "id": "record_store",
        "location": "a small independent record store",
        "action": "looking through vinyl records with a relaxed expression",
        "mood": "casual weekend discovery",
    },
    {
        "id": "coffee_to_go",
        "location": "a lively pedestrian street",
        "action": "walking out of a cafe with coffee and adjusting her jacket",
        "mood": "spontaneous city afternoon",
    },
    {
        "id": "seaside",
        "location": "a quiet European seaside promenade",
        "action": "walking near the water with her hair moving naturally in the breeze",
        "mood": "relaxed travel day",
    },
    {
        "id": "hotel_lobby",
        "location": "a simple stylish hotel lobby",
        "action": "sitting in an armchair and checking her phone",
        "mood": "casual travel downtime",
    },
    {
        "id": "market",
        "location": "a local European street market",
        "action": "choosing fruit from a small market stall",
        "mood": "natural weekend morning",
    },
    {
        "id": "bridge",
        "location": "a pedestrian bridge over a city river",
        "action": "pausing for a moment and looking toward the city",
        "mood": "soft overcast afternoon",
    },
    {
        "id": "cinema",
        "location": "outside a small independent cinema",
        "action": "walking away from the entrance while holding a cinema ticket",
        "mood": "casual evening out",
    },
    {
        "id": "rainy_street",
        "location": "a European street after light rain",
        "action": "walking with a closed umbrella and coffee",
        "mood": "moody but realistic early evening",
    },
]


def _load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        print("⚠️ Generation history is unreadable. Starting with an empty history.")
        return []


def _save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _choose_scene():
    history = _load_history()
    used_ids = {item.get("scene_id") for item in history[-len(SCENES):]}

    available = [scene for scene in SCENES if scene["id"] not in used_ids]

    if not available:
        available = SCENES.copy()
        print("🔄 All scenes have been used. Starting a new scene cycle.")

    return random.choice(available)


def _choose_varied_option(options, history_key, recent_count=4):
    """Avoid repeating the same outfit, pose, framing, or gaze too often."""
    history = _load_history()
    recent_values = {
        item.get(history_key)
        for item in history[-recent_count:]
        if item.get(history_key)
    }
    available = [option for option in options if option not in recent_values]

    if not available:
        available = list(options)

    return random.choice(available)


def _extract_image(response):
    content_type = response.headers.get("content-type", "").lower()
    if content_type.startswith("image/"):
        return response.content
    try:
        data = response.json()
    except ValueError as error:
        raise RuntimeError(f"❌ Cloudflare returned an unexpected response: {response.text[:1000]}") from error
    result = data.get("result") or {}
    image_data = result.get("image") or result.get("data")
    if isinstance(image_data, str) and image_data:
        try:
            return base64.b64decode(image_data)
        except Exception as error:
            raise RuntimeError("❌ Could not decode the image returned by Cloudflare") from error
    raise RuntimeError(f"❌ Cloudflare returned no image: {json.dumps(data)[:1500]}")


def generate_image():
    api_key = os.getenv("Workers_AI") or os.getenv("CLOUDFLARE_API_TOKEN")
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    if not api_key:
        raise RuntimeError("❌ GitHub Secret Workers_AI is not configured")
    if not account_id:
        raise RuntimeError("❌ CLOUDFLARE_ACCOUNT_ID is not configured")

    if not REFERENCE_IMAGE.exists():
        raise RuntimeError(
            f"❌ Alicia reference image not found: {REFERENCE_IMAGE}"
        )

    scene = _choose_scene()

    clothing_options = [
        "a dark oversized knit sweater, straight jeans and minimal silver jewelry",
        "a simple cream knit sweater, straight jeans and minimal silver jewelry",
        "a casual dark jacket over a plain top, relaxed jeans and minimal silver jewelry",
        "a simple neutral cardigan, straight jeans and minimal silver jewelry",
    ]

    clothing = _choose_varied_option(clothing_options, "outfit", recent_count=3)

    # Vary framing, body language, and gaze so photos do not all look like centered portraits.
    composition_options = [
        "Place Alicia off-center in the left third of the frame, with the real location visible around her.",
        "Place Alicia off-center in the right third of the frame, leaving natural breathing room on the other side.",
        "Use a wider environmental composition showing more of the street or interior, with Alicia not filling the whole frame.",
        "Photograph her from a slight side angle in a relaxed three-quarter view, not straight-on.",
        "Use a casual candid composition with slightly imperfect framing, as if a friend took the photo spontaneously.",
        "Frame her from a little farther away, showing her natural posture and more of the surrounding environment.",
    ]
    pose_options = [
        "Her body is turned slightly sideways, with her weight resting naturally on one leg.",
        "If the setting has a suitable wall, counter, or railing, she casually leans against it with relaxed shoulders.",
        "She stands at a relaxed three-quarter angle, one shoulder slightly closer to the camera, without posing like a model.",
        "She is caught in a natural in-between moment, casually adjusting her sleeve or jacket.",
        "Her posture is relaxed and asymmetrical, with a slight shift of weight and hands resting naturally.",
        "When appropriate for the scene, she sits or stands at an angle rather than squarely facing the camera.",
    ]
    gaze_options = [
        "She is looking away from the camera toward something in the environment.",
        "Her gaze is slightly downward, as if noticing something nearby.",
        "She is looking off to the side, not directly into the lens.",
        "She is focused on the activity she is doing rather than acknowledging the photographer.",
        "She briefly glances toward the camera with a relaxed, unposed expression.",
        "Her face is shown in a natural side or three-quarter view, not a straight-on portrait.",
    ]

    composition = _choose_varied_option(composition_options, "composition", recent_count=4)
    pose = _choose_varied_option(pose_options, "pose", recent_count=4)
    gaze = _choose_varied_option(gaze_options, "gaze", recent_count=4)

    object_guidance = ""
    if scene["id"] == "train_station":
        object_guidance = """
BAG REALISM — IMPORTANT:
Show exactly ONE ordinary everyday shoulder bag. No second bag, no duplicate bag, no extra handbag in the background.
Choose a simple, believable design with a soft matte leather or durable woven-fabric surface, a clear practical shape, and only a few understated details.
The handle and shoulder strap must be continuous, correctly attached, and physically plausible. No tangled straps, broken handles, melted hardware, warped seams, or impossible geometry.
The bag hangs naturally at Alicia’s side with realistic weight, folds, perspective, and contact shadows. Its lighting, sharpness, and colors must match the same photograph and environment.
Avoid glossy plastic surfaces, perfect showroom styling, decorative clutter, complex buckles, logos, labels, and readable text. The bag must look like a real object captured by a phone camera, not a pasted-in product image.
"""

    prompt = f"""
Use the supplied reference photo as the identity reference for Alicia.

Create a new photorealistic everyday smartphone photograph of the SAME
adult woman from the reference image.

IDENTITY PRIORITY:
Preserve her recognizable identity from the reference:
same face, same natural facial proportions, same eyes, same nose, same lips,
same eyebrows, same skin tone, same dark-brown medium-length hair and the
same overall natural appearance.

Do NOT redesign her face.
Do NOT make her more beautiful.
Do NOT make her younger or older.
Do NOT turn her into a model, celebrity or generic AI woman.

The reference image is the source of truth for her appearance.

NEW SCENE:
Location: {scene["location"]}.
Action: Alicia is {scene["action"]}.
Mood: {scene["mood"]}.
Clothing: {clothing}.

She is not posing for a professional photoshoot. The photo looks like a
friend casually took it with a modern smartphone. Her body language is
natural and slightly imperfect.

PHOTOGRAPHY:
Natural daylight or realistic ambient light, ordinary smartphone perspective,
natural exposure, realistic colors, slight natural photographic softness,
realistic skin texture, subtle pores and small natural imperfections.
Use a believable candid composition rather than a centered studio portrait.

COMPOSITION VARIATION:
{composition}

BODY LANGUAGE:
{pose}
Adapt this naturally to the selected scene and its action; do not create contradictory actions.

GAZE AND EXPRESSION:
{gaze}
Direct eye contact with the camera should be occasional, not the default.

{object_guidance}

FACE AND SKIN:
Keep the natural face from the reference exactly as the identity anchor.
Natural eyes and eyelids, natural nose, natural lips, natural eyebrows.
Real human skin with normal texture and tiny imperfections.
No beauty filter, no airbrushing, no plastic or porcelain skin,
no excessive smoothing, no face enhancement.

HAIR:
Keep the same dark-brown medium-length hair identity from the reference.
Natural everyday styling, slightly imperfect, not salon-perfect.

IMPORTANT:
Only change the scene, pose, clothing details and environment.
The person herself must remain recognizably the same Alicia.

No CGI, no illustration, no 3D render, no fashion campaign,
no studio portrait, no glamour retouching, no exaggerated facial features,
no text, no logo, no watermark.

Vertical 4:5 composition suitable for an Instagram feed.
"""

    print("🎨 Generating a new Alicia photo...")
    print(f"🧬 Identity reference: {REFERENCE_IMAGE}")
    print(f"📍 Scene: {scene['id']} — {scene['location']}")
    print(f"👗 Outfit: {clothing}")

    try:
        # Reference images must be smaller than 512x512 for this model.
        with Image.open(REFERENCE_IMAGE) as source:
            reference = source.convert("RGB")
            reference.thumbnail((512, 512))
            buffer = io.BytesIO()
            reference.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            response = requests.post(
                API_URL_TEMPLATE.format(account_id=account_id),
                headers={"Authorization": f"Bearer {api_key}"},
                data={"prompt": " ".join(prompt.split()), "width": "1024", "height": "1280"},
                files={"input_image_0": ("alicia_reference.jpg", buffer, "image/jpeg")},
                timeout=300,
            )
        if response.status_code != 200:
            raise RuntimeError(
                f"❌ Cloudflare Workers AI error {response.status_code}: "
                f"{response.text[:1500]}"
            )
        image_bytes = _extract_image(response)
        if not image_bytes:
            raise RuntimeError("❌ Cloudflare returned an empty image")
        try:
            with Image.open(io.BytesIO(image_bytes)) as generated:
                generated.load()
                filename_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
                output_file = OUTPUT_DIR / f"alicia_{filename_timestamp}.png"
                generated.convert("RGB").save(output_file, format="PNG")
        except Exception as error:
            raise RuntimeError("❌ Cloudflare response was not a valid image") from error

        history = _load_history()
        generated_at = datetime.now(timezone.utc).isoformat()
        history.append(
            {
                "scene_id": scene["id"],
                "scene": scene["location"],
                "action": scene["action"],
                "outfit": clothing,
                "composition": composition,
                "pose": pose,
                "gaze": gaze,
                "generated_at": generated_at,
            }
        )
        _save_history(history)

        print(f"✅ Image saved: {output_file}")
        print(f"📝 History saved: {HISTORY_FILE}")
        print(f"📦 Size: {output_file.stat().st_size / 1024:.1f} KB")

        return {
            "image": str(output_file),
            "scene_id": scene["id"],
            "scene": scene["location"],
            "action": scene["action"],
            "mood": scene["mood"],
            "outfit": clothing,
            "composition": composition,
            "pose": pose,
            "gaze": gaze,
            "generated_at": generated_at,
        }

    except requests.RequestException as error:
        raise RuntimeError(
            f"❌ Network error while generating image: {error}"
        ) from error


if __name__ == "__main__":
    generate_image()
