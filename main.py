from ai.caption_generator import generate_caption
from ai.image_generator import generate_image


def main():
    print("🤖 Instagram AI Agent started")

    image_info = generate_image()
    generate_caption(image_info)

    print("✅ Generation completed")


if __name__ == "__main__":
    main()
