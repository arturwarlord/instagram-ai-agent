"""Promote a generated Alicia image into the manually curated selection."""
import shutil
import sys
from pathlib import Path

from PIL import Image


GENERATED_DIR = Path("content/generated")
SELECTED_DIR = Path("content/selected")


def select_photo(filename, generated_dir=GENERATED_DIR, selected_dir=SELECTED_DIR):
    """Copy one valid generated PNG into the curated folder without overwriting."""
    if not filename or Path(filename).name != filename or filename in {".", ".."}:
        raise ValueError("Provide only the image filename, not a path.")
    if not filename.lower().endswith(".png"):
        raise ValueError("Only PNG images can be selected.")

    source = generated_dir / filename
    if not source.is_file():
        raise FileNotFoundError(f"Generated image not found: {source}")

    try:
        with Image.open(source) as image:
            if image.format != "PNG":
                raise ValueError("The selected file is not a valid PNG image.")
            image.verify()
    except (OSError, SyntaxError) as error:
        raise ValueError(f"Image is corrupt or unreadable: {filename}") from error

    selected_dir.mkdir(parents=True, exist_ok=True)
    destination = selected_dir / filename
    if destination.exists():
        raise FileExistsError(f"That image is already selected: {filename}")

    shutil.copy2(source, destination)
    return destination


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/select_photo.py <generated-image.png>")
    try:
        destination = select_photo(sys.argv[1])
    except (ValueError, FileNotFoundError, FileExistsError) as error:
        raise SystemExit(f"Selection failed: {error}") from error
    print(f"Selected photo saved to: {destination}")


if __name__ == "__main__":
    main()
