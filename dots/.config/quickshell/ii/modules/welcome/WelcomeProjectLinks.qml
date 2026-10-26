pragma Singleton
pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import qs.services

/** Official project destinations used by Welcome cards.
 * The fork documentation URL stays empty until the project publishes it.
 */
QtObject {
    readonly property string repositoryUrl: (ShellUpdates && ShellUpdates.activeRemote) ? ShellUpdates.activeRemote : "https://github.com/imyash0722/ii-p3drovfx-dynamic-island"
    readonly property string documentationUrl: "https://github.com/P3DROVFX/ii-p3drovfx/wiki"
    readonly property string discordUrl: "https://discord.gg/GtdRBXgMwq"
    readonly property bool documentationAvailable: true
}
