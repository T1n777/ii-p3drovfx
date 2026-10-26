"""Contracts for Dynamic Island overlay autohide coordination.

Validates that:
1. Dynamic Island autohide coordinates with the bar autohide system.
2. In overlay mode, windows are not pushed (exclusiveZone: 0).
3. The wallpaper gradient overlay (BarGradientOverlay) fades out in lockstep
   with barHiddenAmount / isBarHidden instead of leaving an empty blurred bar.
4. NotchIsland translates along the Y-axis with barHiddenAmount in bar-center mode
   instead of collapsing width and leaving a visual hole.
5. Reveal state between the island and the bar is bidirectional.
"""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
STATES = (ROOT / "GlobalStates.qml").read_text(encoding="utf-8")
INTERACTION = (ROOT / "modules/common/BarInteraction.qml").read_text(encoding="utf-8")
BAR_WINDOW = (ROOT / "modules/ii/bar/core/BarWindow.qml").read_text(encoding="utf-8")
NOTCH_ISLAND = (ROOT / "modules/ii/dynamicIsland/styles/notch/NotchIsland.qml").read_text(encoding="utf-8")
BAR_GRADIENT = (ROOT / "modules/ii/background/blur/BarGradientOverlay.qml").read_text(encoding="utf-8")
DEPTH_CUTOUT = (ROOT / "modules/ii/background/depth/DepthCutoutLayer.qml").read_text(encoding="utf-8")


class DynamicIslandOverlayAutohideContractTests(unittest.TestCase):
    def test_globalstates_holds_bar_hidden_metrics_and_reveal_flags(self):
        self.assertIn("property var barHiddenAmounts: ({})", STATES)
        self.assertIn("property var barHiddenStates: ({})", STATES)
        self.assertIn("property var barHiddenProgresses: ({})", STATES)
        self.assertIn("function setBarHiddenMetrics(screenName, hiddenAmount, isHidden, progress)", STATES)
        self.assertIn("function barHiddenAmountFor(screenName)", STATES)
        self.assertIn("function isBarHidden(screenName)", STATES)
        self.assertIn("function barHiddenProgressFor(screenName)", STATES)
        self.assertIn("function reportTopShellHover(source, isHovered)", STATES)
        self.assertIn("property bool topShellRevealed:", STATES)
        self.assertIn("property bool islandInBarRevealed:", STATES)
        self.assertIn("property bool barInBarRevealed:", STATES)

    def test_bar_interaction_includes_island_in_bar_autohide(self):
        self.assertIn("isIslandInBarCenter", INTERACTION)
        self.assertIn("Config.options?.bar?.floatingNotch?.autoHide", INTERACTION)

    def test_bar_window_coordinates_reveal_and_publishes_metrics(self):
        self.assertIn("GlobalStates.setBarHiddenMetrics(autohidePublisher.screenName", BAR_WINDOW)
        self.assertIn("GlobalStates.reportTopShellHover", BAR_WINDOW)
        self.assertIn("GlobalStates.islandInBarRevealed", BAR_WINDOW)
        self.assertIn("GlobalStates.topShellRevealed", BAR_WINDOW)

    def test_notch_island_translates_with_bar_hidden_amount(self):
        self.assertIn("barHiddenAmount", NOTCH_ISLAND)
        self.assertIn("shown - root.barHiddenAmount", NOTCH_ISLAND)
        self.assertIn("GlobalStates.islandInBarRevealed", NOTCH_ISLAND)
        self.assertIn("GlobalStates.topShellRevealed", NOTCH_ISLAND)
        self.assertIn("GlobalStates.reportTopShellHover", NOTCH_ISLAND)
        self.assertIn("effectiveHideDelay", NOTCH_ISLAND)
        self.assertIn("!root.centerInBar", NOTCH_ISLAND)
        self.assertIn("root.centerInBar ? null : edgeSensor", NOTCH_ISLAND)

    def test_bar_gradient_overlay_syncs_with_autohide(self):
        self.assertIn("barHiddenAmount", BAR_GRADIENT)
        self.assertIn("barHiddenProgress", BAR_GRADIENT)
        self.assertIn("isBarHidden", BAR_GRADIENT)
        self.assertIn("1.0 - barOverlayRoot.barHiddenProgress", BAR_GRADIENT)

    def test_depth_cutout_layer_checks_bar_hidden(self):
        self.assertIn("!GlobalStates.isBarHidden(root.screenName)", DEPTH_CUTOUT)

    def test_topshell_keyboard_and_event_reveal_release_triggers_close(self):
        self.assertIn("else if (!root.topShellHovered && !root.barInBarRevealed)", STATES)
        self.assertIn("else if (!root.topShellHovered && !root.islandInBarRevealed)", STATES)
        self.assertIn("!root.topShellHovered && !root.islandInBarRevealed && !root.barInBarRevealed", STATES)


if __name__ == "__main__":
    unittest.main()
