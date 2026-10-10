from ai.image_generator import generate_image


def main():
    print("🤖 Instagram AI Agent started")

    image_info = generate_image()
    print("ℹ️ Caption generation is temporarily disabled while image generation is tested")

    print("✅ Generation completed")


if __name__ == "__main__":
    main()
