from ai.image_generator import generate_image


PHOTOS_PER_RUN = 3


def main():
    print("🤖 Instagram AI Agent started")
    print(f"📸 Generating {PHOTOS_PER_RUN} new Alicia photos")

    generated_images = []

    for index in range(PHOTOS_PER_RUN):
        print(f"\n--- Photo {index + 1}/{PHOTOS_PER_RUN} ---")
        image_info = generate_image()
        generated_images.append(image_info["image"])
        print(f"✅ Photo {index + 1} saved: {image_info['image']}")

    print("\n📚 Generated photos:")
    for image_path in generated_images:
        print(f" - {image_path}")

    print("✅ Generation completed")


if __name__ == "__main__":
    main()
