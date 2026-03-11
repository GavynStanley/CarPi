import QtQuick

Rectangle {
    id: dot
    width: size; height: size; radius: size / 2

    property bool connected: false
    property int size: 6
    property color connectedColor: "#22c55e"
    property color disconnectedColor: "#ef4444"

    color: connected ? connectedColor : disconnectedColor
}
