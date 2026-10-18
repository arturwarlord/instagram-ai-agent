import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.select_photo import select_photo


class SelectPhotoTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.generated = root / "generated"
        self.selected = root / "selected"
        self.generated.mkdir()
        Image.new("RGB", (640, 800), (70, 120, 160)).save(
            self.generated / "alicia.png", format="PNG"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_copies_valid_image_to_selected_folder(self):
        destination = select_photo("alicia.png", self.generated, self.selected)
        self.assertTrue(destination.is_file())
        self.assertEqual(destination.read_bytes(), (self.generated / "alicia.png").read_bytes())

    def test_rejects_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "only the image filename"):
            select_photo("../alicia.png", self.generated, self.selected)

    def test_rejects_non_png(self):
        with self.assertRaisesRegex(ValueError, "Only PNG"):
            select_photo("alicia.jpg", self.generated, self.selected)

    def test_rejects_missing_image(self):
        with self.assertRaises(FileNotFoundError):
            select_photo("missing.png", self.generated, self.selected)

    def test_does_not_overwrite_selected_photo(self):
        self.selected.mkdir()
        existing = self.selected / "alicia.png"
        existing.write_bytes(b"keep this")
        with self.assertRaises(FileExistsError):
            select_photo("alicia.png", self.generated, self.selected)
        self.assertEqual(existing.read_bytes(), b"keep this")


if __name__ == "__main__":
    unittest.main()
