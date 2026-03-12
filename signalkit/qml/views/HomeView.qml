import QtQuick
import QtQuick.Layouts
import "../components"

Item {
    id: homeRoot
    property color accent: "#3b82f6"
    signal navigate(string view)

    // Top-left aligned app grid — CarPlay style
    Grid {
        anchors.top: parent.top; anchors.topMargin: 24
        anchors.left: parent.left; anchors.leftMargin: 24
        columns: 5
        columnSpacing: 16
        rowSpacing: 16

        AppTile {
            label: "Dashboard"
            gradStart: "#064e3b"; gradEnd: "#065f46"
            borderColor: "#059669"; iconColor: "#34d399"
            iconSource: "" + iconsPath + "bolt.svg"
            onClicked: homeRoot.navigate("dashboard")
        }
        AppTile {
            label: "Settings"
            gradStart: "#1c1c1e"; gradEnd: "#2a2a2e"
            borderColor: "#3f3f46"; iconColor: "#a1a1aa"
            iconSource: "" + iconsPath + "settings.svg"
            onClicked: homeRoot.navigate("settings")
        }
        AppTile {
            label: "Dev Console"
            gradStart: "#1c1c1e"; gradEnd: "#2a2a2e"
            borderColor: "#3f3f46"; iconColor: "#f59e0b"
            iconSource: "" + iconsPath + "terminal.svg"
            onClicked: homeRoot.navigate("dev")
        }
        AppTile {
            label: "AirPlay"
            gradStart: "#1e1b4b"; gradEnd: "#272462"
            borderColor: "#4338ca"; iconColor: "#818cf8"
            iconSource: "" + iconsPath + "airplay.svg"
            onClicked: homeRoot.navigate("airplay")
        }
    }
}
