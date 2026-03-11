import QtQuick

Rectangle {
    id: header
    width: parent ? parent.width : 400
    height: 36
    color: "transparent"

    property string title: ""

    // Bottom border
    Rectangle { width: parent.width; height: 1; anchors.bottom: parent.bottom; color: "#27272a" }

    Text {
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left; anchors.leftMargin: 16
        text: header.title
        font.pixelSize: 11; font.weight: Font.Bold; font.letterSpacing: 2
        color: "#71717a"
    }
}
