# Changelog & Architectural Enhancements: ii-p3drovfx-dynamic-island

This document details all architectural improvements, autohide engine rebuilds, keyboard interactions, upstream merges, and installer adaptations implemented in this fork (**ii-p3drovfx-dynamic-island**).

---

## 1. Upstream Merge & Feature Ingestion (`upstream/dev` @ `0065bf2ec`)

Successfully merged upstream `P3DROVFX/ii-p3drovfx@dev` with zero conflicts, bringing the following upstream additions while protecting all custom autohide and island architectural changes:
- **Tuya Smart Devices**: Native quick toggles integration and dialog (`SmartDevicesToggle.qml`, `SmartDevicesDialog.qml`, `smart_devices.py`) supporting local and cloud Tuya device controls.
- **Dock Running Indicators**: Restored and refined configurable running indicators on the dock (`dot` vs `pill` indicator styles, per-window markers, neutral vs accent colors).
- **Dock Monitor Isolation**: `isolateMonitors` option to filter dock apps per-monitor.
- **MangoHud Auto-Wiring**: Automatic Steam game detection and MangoHud hook configuration.
- **Notes Overlay Redesign**: Redesigned notes overlay and sketch canvas integration.
- **ii-Icon Pack Themed Icons**: Custom icon shapes and pack support in themed icon settings.

---

## 2. Fork Installer & In-Shell Update Adaptation

Adapted `setup-ii-p3drovfx.sh`, `ShellUpdates.qml`, `AboutConfig.qml`, and `README.md` to ensure that installing or updating directly from this repository works seamlessly out of the box:
- **Preset & Fallback Configuration**:
  - Added preset `dynamic-island` pointing to `https://github.com/imyash0722/ii-p3drovfx-dynamic-island` branch `dev`.
  - Configured alias `mine` to point to `https://github.com/imyash0722/ii-p3drovfx-dynamic-island`.
  - Set `FALLBACK_URL="https://github.com/imyash0722/ii-p3drovfx-dynamic-island"` and `FALLBACK_BRANCH="dev"`.
  - Updated `upstream` and `p3drovfx` preset branches to `dev`.
- **Protected Files Extension**:
  - Registered `modules/common/widgets/NotificationAppIcon.qml` in `PROTECTED_PATTERNS` so upstream or external updates never overwrite the glyph sanitization fix.
- **Dynamic Fork Labeling in UI**:
  - Updated `ShellUpdates.qml` to display `ii-p3drovfx-dynamic-island` for the active fork.
  - Dynamically bound "This fork" and GitHub links in `AboutConfig.qml` and `WelcomeProjectLinks.qml` to the active remote repository.
- **Clone Instructions**:
  - Updated main `README.md` and `.github/README.md` install instructions to clone `https://github.com/imyash0722/ii-p3drovfx-dynamic-island.git`.

---

## 3. Dynamic Island Keyboard Focus & Escape Key Collapse

### Overview
Previously, when the Dynamic Island expanded (via hover, click, or when opening the dashboard, search, wallpaper browser, or auxiliary bubbles), dismissing it required either clicking away or moving the mouse pointer completely off the surface. If media was actively playing or pending notifications existed, collapsing often retained those widget faces.

### Key Changes
- **Escape Key (`Esc`) Binding**:
  - Bound the `Escape` key (`Shortcut { sequences: ["Escape"] }`) directly on the Dynamic Island's layer shell window (`win: PanelWindow`).
  - Pressing `Escape` while any expanded view is active collapses the island into the **shown, resting, time-only face** (`clock` face).
- **Time-Only Resting Face Enforcement (`preferClockFace`)**:
  - Introduced the state property `preferClockFace: bool`.
  - When `Escape` is triggered:
    - `preferClockFace` is set to `true`.
    - `expandSuppressed` is set to `true`.
    - `forceCollapse()`, `dismissDashboard()`, and bubble dismissals are executed.
    - Active auxiliary surfaces (session, wallpaper, search) are closed.
    - Side glances (`sideIds`) are suppressed (`sideIds: root.preferClockFace ? [] : root.sideBound`), rendering strictly the tabular SF Pro clock face without cover art or auxiliary badges.
    - The island remains revealed at the top edge under the pointer without swelling or re-expanding.
- **Pointer Exit Reset**:
  - As soon as the pointer leaves the island boundary (`!hoverIntent.hovered && !root.islandShellHovered`), `preferClockFace` and `expandSuppressed` automatically reset to `false`.
  - If autohide is enabled, the island cleanly retracts off-screen; if autohide is off, the normal resting face (with active side glances) resumes seamlessly.
- **Dynamic OnDemand Keyboard Focus**:
  - Updated `WlrLayershell.keyboardFocus` in `NotchIsland.qml` to evaluate:
    ```qml
    WlrLayershell.keyboardFocus: (root.wallpaperActive || root.searchActive || root.sessionActive
            || root.askpassActive || notchContent.dashboardWantsKeyboard
            || root.expanded || root.dashboardActive || root.expandedBubbleId !== "") && !root.keyboardNudge
        ? WlrKeyboardFocus.OnDemand : WlrKeyboardFocus.None
    ```
  - Keyboard focus is acquired dynamically only while expanded, allowing keystrokes like `Escape` to be processed without trapping keyboard input on desktop windows during resting or contracted states.
- **Universal Signal & IPC Integration**:
  - Added `signal collapseIslandRequested()` and `function collapseDynamicIsland()` to `GlobalStates.qml`.
  - Added IPC endpoint `dynamicIsland collapseToClock` and `dynamicIsland collapse` to `IpcHandler`.
  - Integrated `Key_Escape` in `DynamicIslandStyle.qml` to route through `GlobalStates.collapseDynamicIsland()`.

---

## 4. Rebuilt Top Shell Autohide Engine

### Root Causes Addressed
1. **Competing Hover Timers**: The Bar and Dynamic Island operated independent hover and hide countdowns (e.g. 80ms vs 250ms), causing destructive feedback loops and rapid jittering ("shaking/flashing") when hovering near adjacent icons or the island edge.
2. **Horizontal Edge Mask Blocking Browser Tabs**: The floating island's hidden sensor overlay stretched beyond its body width with excessive height, intercepting mouse clicks intended for browser tabs and window title bars.
3. **Window Pushing vs Window Overlay**: Toggling between auto-hide and visible states repeatedly altered Hyprland exclusive zones, forcefully resizing open windows and disrupting user workflow.

### Architecture
- **Centralized Hover Bus (`GlobalStates.qml`)**:
  - Introduced `topShellHoverSources: ({})` to register all interactive sources (`bar_<screen>`, `island_<screen>`, popups, bubbles).
  - Single master `topShellCloseTimer` (80ms debounce) eliminates all oscillation and desynchronization.
- **Window Push vs Overlay Toggle (`pushWindows`)**:
  - Added `Config.options.bar.autoHide.pushWindows` toggle.
  - When `pushWindows: false` (Window Overlay Mode), `exclusiveZone` is held at `0`. The bar and dynamic island slide smoothly over tiled and floating windows without causing window resizes or desktop reflows.
  - When `pushWindows: true`, Hyprland windows are pushed down to accommodate the revealed bar.
- **Clean Input Sensor Handover**:
  - In `centerInBar` mode, the Dynamic Island's hidden input mask yields completely to `null` (`root.centerInBar ? null : edgeSensor`).
  - 100% of the screen top edge is managed cleanly by `BarWindow.qml`'s configurable `hoverRegionWidth` (defaulting to 6–7px), keeping tabs and close buttons accessible.

---

## 5. QML Settings UI Fusion

The autohide options, window push behavior, and Dynamic Island configurations are fused directly into the Quickshell Settings interface:

1. **Bar Settings (`BarConfig.qml`)**:
   - Added **Push windows** toggle (`ConfigSwitch`) under the auto-hide section.
   - Added **Hide delay (ms)** spinbox (`ConfigSpinBox`) allowing millisecond-level retraction tuning.
   - Unified bi-directional synchronization between `bar.autoHide.enable` and `floatingNotch.autoHide` when in `centerInBar` mode.
2. **Bar Behavior Section (`BarBehaviorSection.qml`)**:
   - Exposed **Push windows when revealed** (`ConfigSwitch`) with informative tooltip.
   - Exposed interactive edge trigger width (`hoverRegionWidth`, from 2px to 64px).
   - Exposed dwell delay (`hoverDelay`) and retraction delay (`hideDelay`).
   - Exposed **Reveal with Super key** toggle.
3. **Bar Placement Proxy Section (`BarPlacementSection.qml`)**:
   - Added search-indexed proxy entries for `pushWindows`, `hideDelay`, and `hoverRegionWidth` so Settings search quickly locates all autohide controls.
4. **Dynamic Island Settings (`DynamicIslandConfig.qml`)**:
   - Integrated mode cards with prerequisite validation.
   - Coordinated `Always hide floating island` toggle with bar autohide.

---

## 6. Notification App Icon Path Sanitization

### Issue
When applications sent raw filesystem paths (e.g. `.SCOPED_DIR.YYT79A/ICON.PNG` or Chromium temp icon paths) as notification app icons, the shell attempted to render them as Material Symbols. This caused huge raw path strings to sprawl across notification toasts and the notification center.

### Resolution
- **Strict Glyph Validation in `NotificationAppIcon.qml`**:
  - Restricted Material Symbol rendering strictly to alphanumeric font identifiers:
    ```qml
    readonly property bool isIconName: /^[a-z0-9_]+$/.test(root.appIcon)
    ```
  - Filenames containing slashes, colons, or dots (like `.png`, `.svg`) are rejected as font glyphs and routed to image loaders.
- **Resilient Fallback**:
  - If a file path is missing or unreadable on disk, falls back gracefully to category/type icons (e.g. `chat`, `notifications`) rather than displaying invalid text strings.
- **Visual Clipping**:
  - Added `clip: true` on both `MaterialShape` and `MaterialSymbol` containers to prevent any visual overflow.
- **Protection**:
  - Registered `NotificationAppIcon.qml` in `.protected` and `.updateignore` to preserve the fix across upstream syncs.

---

## 7. Verification & Contract Test Suites

Dedicated Python contract tests have been introduced under `scripts/tests/`:
1. `test_dynamic_island_escape_and_settings_contract.py`:
   - Verifies `preferClockFace` implementation, `pagedId` arbitration, `sideIds` suppressions.
   - Verifies `WlrLayershell.keyboardFocus` OnDemand rule when expanded and `Escape` shortcut activation.
   - Verifies `GlobalStates.qml` signal dispatching and Settings UI controls fusion.
2. `test_dynamic_island_overlay_autohide_contract.py`:
   - Verifies centralized metrics (`barHiddenAmounts`, `topShellHoverSources`).
   - Verifies vertical translation synchronization (`container.y = surfaceTop - barHiddenAmount`).
   - Verifies input sensor delegation in `centerInBar` mode.
3. `test_notification_app_icon_contract.py`:
   - Verifies strict regex validation, image fallback, and container clipping.
4. `test_dock_island_bar_reclaim_contract.py`:
   - Verifies layout and geometry recovery for dock and island placements.
