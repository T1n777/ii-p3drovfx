"""Contract tests for NotificationAppIcon.

Validates that:
1. File paths (such as Chromium scoped temporary directories or .png/.jpg/.svg images)
   are never misclassified as Material Symbol glyphs.
2. Material Symbol names are strictly short lowercase identifiers without slashes, dots,
   colons, or extensions.
3. NotificationAppIcon enforces clipping so no icon or text can overflow into notification text.
4. Missing or deleted temporary image files do not show missing-icon checkerboards
   and cleanly fall back to appropriate summary/default material symbols.
"""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
ICON_QML = (ROOT / "modules/common/widgets/NotificationAppIcon.qml").read_text(encoding="utf-8")


class NotificationAppIconContractTests(unittest.TestCase):
    def test_clipping_is_enforced_on_shape_and_symbol(self):
        self.assertIn("clip: true", ICON_QML)

    def test_image_is_glyph_rejects_slashes_and_extensions(self):
        self.assertIn("themedImageName.indexOf(\"/\") !== -1", ICON_QML)
        self.assertIn("themedImageName.indexOf(\".\") !== -1", ICON_QML)
        self.assertIn("/^[a-z0-9_]+$/", ICON_QML)

    def test_regex_classifies_correctly(self):
        glyph_regex = re.compile(r"^[a-z0-9_]+$")
        # Real glyph names must pass
        self.assertTrue(glyph_regex.match("coffee"))
        self.assertTrue(glyph_regex.match("dns"))
        self.assertTrue(glyph_regex.match("battery_full"))
        self.assertTrue(glyph_regex.match("priority_high"))

        # Chromium temp paths and file paths must fail
        self.assertFalse(glyph_regex.match("/tmp/org.chromium.Chromium.scoped_dir.Yyt79a/icon.png"))
        self.assertFalse(glyph_regex.match(".scoped_dir.yyt79a/icon.png"))
        self.assertFalse(glyph_regex.match("icon.png"))
        self.assertFalse(glyph_regex.match("file:///tmp/icon.png"))

    def test_material_symbol_loader_acts_as_fallback_when_image_not_ready(self):
        self.assertIn("!notifImageLoader.item.imageReady", ICON_QML)

    def test_notif_image_app_icon_loader_omits_image_missing_fallback(self):
        self.assertIn('Quickshell.iconPath(root.appIcon, "")', ICON_QML)


if __name__ == "__main__":
    unittest.main()
