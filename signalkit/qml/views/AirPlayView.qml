import QtQuick
import QtQuick.Layouts
import "../components"

Item {
    id: airplayRoot
    property color accent: "#3b82f6"

    // AirPlay state from bridge
    property bool airplayAvailable: bridge.airplayAvailable
    property bool airplayRunning: bridge.airplayRunning
    property bool airplayConnected: bridge.airplayConnected
    property string airplayDevice: bridge.airplayDevice

    // -- Waiting / status overlay (shown when not connected) --
    Item {
        anchors.fill: parent
        visible: !airplayConnected

        Column {
            anchors.centerIn: parent
            spacing: 16
            width: 280

            // AirPlay icon
            Rectangle {
                width: 72; height: 72; radius: 20
                anchors.horizontalCenter: parent.horizontalCenter
                color: Qt.rgba(0.506, 0.549, 0.972, 0.10)
                border.width: 1
                border.color: Qt.rgba(0.506, 0.549, 0.972, 0.25)

                Image {
                    anchors.centerIn: parent
                    source: "" + iconsPath + "airplay.svg"
                    sourceSize: Qt.size(32, 32)
                    smooth: true
                }
            }

            // Title
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "AirPlay"
                font.pixelSize: 18; font.weight: Font.Bold
                color: "#e4e4e7"
            }

            // Status message
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: {
                    if (!airplayAvailable)
                        return "AirPlay is not available on this device.\nInstall uxplay to enable AirPlay mirroring."
                    if (!airplayRunning)
                        return "AirPlay receiver is stopped."
                    return "Waiting for connection...\nOpen Control Center on your iPhone or iPad\nand tap Screen Mirroring \u2192 SignalKit"
                }
                font.pixelSize: 11
                color: "#71717a"
                horizontalAlignment: Text.AlignHCenter
                lineHeight: 1.4
                wrapMode: Text.WordWrap
                width: parent.width
            }

            Item { width: 1; height: 8 }

            // Pulsing indicator (when waiting)
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 8; height: 8; radius: 4
                color: airplayRunning ? "#818cf8" : "#3f3f46"
                visible: airplayAvailable

                SequentialAnimation on opacity {
                    running: airplayRunning && !airplayConnected
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.3; duration: 800; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0; duration: 800; easing.type: Easing.InOutSine }
                }
            }

            Item { width: 1; height: 8 }

            // Start / Stop button
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 140; height: 36; radius: 8
                color: airplayRunning ? "#2a1215" : Qt.rgba(0.506, 0.549, 0.972, 0.15)
                border.width: 1
                border.color: airplayRunning ? "#7f1d1d" : Qt.rgba(0.506, 0.549, 0.972, 0.3)
                visible: airplayAvailable

                Text {
                    anchors.centerIn: parent
                    text: airplayRunning ? "Stop Receiver" : "Start Receiver"
                    font.pixelSize: 11; font.weight: Font.DemiBold
                    color: airplayRunning ? "#fca5a5" : "#818cf8"
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (airplayRunning)
                            bridge.stopAirplay()
                        else
                            bridge.startAirplay()
                    }
                }
            }
        }
    }

    // -- Connected overlay (top bar info when streaming) --
    Rectangle {
        anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
        height: 32
        color: Qt.rgba(0.506, 0.549, 0.972, 0.08)
        visible: airplayConnected

        Row {
            anchors.centerIn: parent
            spacing: 8

            Rectangle {
                width: 6; height: 6; radius: 3
                color: "#818cf8"
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: airplayDevice ? ("Mirroring from " + airplayDevice) : "AirPlay Connected"
                font.pixelSize: 10; font.weight: Font.DemiBold
                color: "#a5b4fc"
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // Disconnect button
        Rectangle {
            anchors.right: parent.right; anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            width: 24; height: 24; radius: 6
            color: disconnectMa.containsMouse ? "#2a1215" : "transparent"

            Text {
                anchors.centerIn: parent
                text: "\u00d7"; font.pixelSize: 14; color: "#71717a"
            }
            MouseArea {
                id: disconnectMa
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: bridge.stopAirplay()
            }
        }
    }

    // -- Video area placeholder --
    // When uxplay renders via GStreamer, the video appears in a separate
    // overlay/window managed by GStreamer's video sink. On EGLFS this
    // renders directly to the display framebuffer as a DRM plane overlay.
    //
    // For future embedded rendering (shared memory frames), a QML Image
    // with a QQuickImageProvider can be used here:
    Rectangle {
        anchors.fill: parent
        anchors.topMargin: airplayConnected ? 32 : 0
        color: "transparent"
        visible: airplayConnected

        Text {
            anchors.centerIn: parent
            text: "AirPlay video is rendering via GStreamer"
            font.pixelSize: 11; color: "#52525b"
            visible: airplayConnected
        }
    }
}
