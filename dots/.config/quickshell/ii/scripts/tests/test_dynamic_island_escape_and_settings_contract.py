"""Contracts for Dynamic Island Escape key collapse and QML Settings fusion.

Validates that:
1. NotchIsland supports collapsing expanded views to a resting time-only face via Escape.
2. Window layer shell keyboard focus is granted OnDemand when expanded so Escape is captured.
3. pagedId returns "clock" and sideIds is empty when preferClockFace is active.
4. GlobalStates exposes collapseDynamicIsland() and collapseIslandRequested signal.
5. DynamicIslandStyle routes Escape through GlobalStates.collapseDynamicIsland().
6. Settings UI (BarConfig, BarBehaviorSection, BarPlacementSection) exposes pushWindows toggle
   and autohide options.
"""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
STATES = (ROOT / "GlobalStates.qml").read_text(encoding="utf-8")
NOTCH_ISLAND = (ROOT / "modules/ii/dynamicIsland/styles/notch/NotchIsland.qml").read_text(encoding="utf-8")
DYNAMIC_STYLE = (ROOT / "modules/ii/bar/styles/DynamicIslandStyle.qml").read_text(encoding="utf-8")
BAR_BEHAVIOR = (ROOT / "modules/settings/configs/sections/BarBehaviorSection.qml").read_text(encoding="utf-8")
BAR_PLACEMENT = (ROOT / "modules/settings/configs/sections/BarPlacementSection.qml").read_text(encoding="utf-8")
BAR_CONFIG = (ROOT / "modules/settings/configs/BarConfig.qml").read_text(encoding="utf-8")
SHELL_UPDATES = (ROOT / "services/ShellUpdates.qml").read_text(encoding="utf-8")
SETUP_SCRIPT_PATH = ROOT.parents[3] / "setup-ii-p3drovfx.sh"
SETUP_SCRIPT = SETUP_SCRIPT_PATH.read_text(encoding="utf-8") if SETUP_SCRIPT_PATH.exists() else ""


class DynamicIslandEscapeAndSettingsContractTests(unittest.TestCase):
    def test_notch_island_has_escape_collapse_to_clock(self):
        self.assertIn("property bool preferClockFace: false", NOTCH_ISLAND)
        self.assertIn("if (root.preferClockFace)\n            return \"clock\";", NOTCH_ISLAND)
        self.assertIn("readonly property bool restingFace: root.preferClockFace ||", NOTCH_ISLAND)
        self.assertIn("function collapseToClock()", NOTCH_ISLAND)
        self.assertIn("root.preferClockFace = true;", NOTCH_ISLAND)
        self.assertIn("root.expandSuppressed = true;", NOTCH_ISLAND)
        self.assertIn("root.forceCollapse();", NOTCH_ISLAND)
        self.assertIn("root.dismissDashboard();", NOTCH_ISLAND)
        self.assertIn("root.expandedBubbleId = \"\";", NOTCH_ISLAND)
        self.assertIn("sideIds: root.preferClockFace ? [] : root.sideBound", NOTCH_ISLAND)

    def test_notch_island_requests_keyboard_focus_when_expanded(self):
        self.assertIn("root.expanded || root.dashboardActive || root.expandedBubbleId !== \"\"", NOTCH_ISLAND)
        self.assertIn("WlrLayershell.keyboardFocus:", NOTCH_ISLAND)
        self.assertIn("Shortcut {", NOTCH_ISLAND)
        self.assertIn("sequences: [\"Escape\"]", NOTCH_ISLAND)
        self.assertIn("onActivated: root.collapseToClock()", NOTCH_ISLAND)

    def test_globalstates_and_bar_style_escape_signals(self):
        self.assertIn("signal collapseIslandRequested()", STATES)
        self.assertIn("function collapseDynamicIsland(): void", STATES)
        self.assertIn("GlobalStates.collapseDynamicIsland()", DYNAMIC_STYLE)
        self.assertIn("function onCollapseIslandRequested()", NOTCH_ISLAND)

    def test_settings_bar_behavior_section_fuses_push_windows(self):
        self.assertIn("Config.options.bar.autoHide.pushWindows", BAR_BEHAVIOR)
        self.assertIn("Push windows when revealed", BAR_BEHAVIOR)

    def test_settings_bar_placement_section_fuses_push_windows(self):
        self.assertIn("Config.options.bar.autoHide.pushWindows", BAR_PLACEMENT)
        self.assertIn("Push windows when revealed", BAR_PLACEMENT)

    def test_settings_bar_config_fuses_push_windows_and_hide_delay(self):
        self.assertIn("barConfigRoot.bar.autoHide.pushWindows", BAR_CONFIG)
        self.assertIn("barConfigRoot.bar.autoHide.hideDelay", BAR_CONFIG)
        self.assertIn("Config.options.bar.floatingNotch.autoHide = checked;", BAR_CONFIG)

    def test_installer_and_updates_configuration(self):
        self.assertIn('["dynamic-island"]="https://github.com/imyash0722/ii-p3drovfx-dynamic-island"', SETUP_SCRIPT)
        self.assertIn('FALLBACK_URL="https://github.com/imyash0722/ii-p3drovfx-dynamic-island"', SETUP_SCRIPT)
        self.assertIn('FALLBACK_BRANCH="dev"', SETUP_SCRIPT)
        self.assertIn('case "dynamic-island":', SHELL_UPDATES)
        self.assertIn('"ii-p3drovfx-dynamic-island"', SHELL_UPDATES)


if __name__ == "__main__":
    unittest.main()
