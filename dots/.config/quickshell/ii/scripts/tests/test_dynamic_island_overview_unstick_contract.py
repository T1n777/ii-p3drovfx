"""Contracts for Dynamic Island overview unsticking and Super overview toggle coordination.

Validates that:
1. collapseToClock() explicitly closes session, wallpaper, and overview via GlobalStates,
   and clears edgeRevealed when centerInBar is active to prevent unhide latches.
2. preferClockFace and expandSuppressed are reset when explicit surfaces open (overview,
   app drawer, session, wallpaper) or when the cursor leaves the island shell.
3. fullWindow background MouseArea is enabled whenever overview or search is open so
   outside clicks reliably close it.
4. fullWindow and container capture Super key releases to toggle overview when the
   layer-shell window holds keyboard focus.
5. GlobalStates unlatches superDown upon collapseDynamicIsland and upon Hyprland workspace
   switching events so bar and island autohide is never held hostage.
"""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
STATES = (ROOT / "GlobalStates.qml").read_text(encoding="utf-8")
NOTCH_ISLAND = (ROOT / "modules/ii/dynamicIsland/styles/notch/NotchIsland.qml").read_text(encoding="utf-8")


class DynamicIslandOverviewUnstickContractTests(unittest.TestCase):
    def test_collapse_to_clock_closes_surfaces_and_unlatches_edge(self):
        self.assertIn("function collapseToClock()", NOTCH_ISLAND)
        self.assertIn("GlobalStates.sessionOpen = false;", NOTCH_ISLAND)
        self.assertIn("GlobalStates.wallpaperSelectorOpen = false;", NOTCH_ISLAND)
        self.assertIn("GlobalStates.closeOverview();", NOTCH_ISLAND)
        self.assertIn("if (root.centerInBar)\n            root.edgeRevealed = false;", NOTCH_ISLAND)

    def test_prefer_clock_face_clears_on_surface_open_or_unhover(self):
        self.assertIn("function onOverviewOpenChanged()", NOTCH_ISLAND)
        self.assertIn("root.preferClockFace = false;\n                root.expandSuppressed = false;", NOTCH_ISLAND)
        self.assertIn("function onAppDrawerOpenChanged()", NOTCH_ISLAND)
        self.assertIn("function onSessionOpenChanged()", NOTCH_ISLAND)
        self.assertIn("function onWallpaperSelectorOpenChanged()", NOTCH_ISLAND)
        self.assertIn("if (!islandShellHovered)\n            root.preferClockFace = false;", NOTCH_ISLAND)

    def test_fullwindow_and_container_super_and_click_dismiss(self):
        self.assertIn("enabled: root.searchActive || GlobalStates.overviewOpen", NOTCH_ISLAND)
        self.assertIn("Keys.onReleased: event => {", NOTCH_ISLAND)
        self.assertIn("event.key === Qt.Key_Super_L || event.key === Qt.Key_Super_R", NOTCH_ISLAND)
        self.assertIn("GlobalStates.toggleOverview();", NOTCH_ISLAND)

    def test_globalstates_superdown_unlatches(self):
        self.assertIn("function collapseDynamicIsland(): void {\n        root.superDown = false;\n        collapseIslandRequested();\n    }", STATES)
        self.assertIn('event.name === "workspace" || event.name === "workspacev2" || event.name === "focusedmon"', STATES)
        self.assertIn("root.superDown = false;", STATES)


if __name__ == "__main__":
    unittest.main()
