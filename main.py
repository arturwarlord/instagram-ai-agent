from ai.image_generator import generate_image


PHOTOS_PER_RUN = 1


def main():
    print("🤖 Instagram AI Agent started")
    print(f"📸 Generating {PHOTOS_PER_RUN} new Alicia photo")

    image_info = generate_image()
    print(f"✅ Photo saved: {image_info['image']}")
    print("✅ Generation completed")


if __name__ == "__main__":
    main()
