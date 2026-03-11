import QtQuick

Rectangle {
    id: pill
    width: pillText.width + horizontalPadding * 2
    height: 24
    radius: 8
    color: pillMA.containsMouse ? hoverColor : bgColor
    border.width: 1; border.color: borderColor

    property string text: ""
    property int horizontalPadding: 8
    property color bgColor: "#18181b"
    property color hoverColor: "#27272a"
    property color borderColor: "#27272a"
    property color textColor: "#a1a1aa"
    property string fontFamily: "Menlo"
    property int fontSize: 10
    signal clicked()

    Text {
        id: pillText
        anchors.centerIn: parent
        text: pill.text
        font.pixelSize: pill.fontSize; font.weight: Font.DemiBold; font.family: pill.fontFamily
        color: pill.textColor
    }

    MouseArea {
        id: pillMA
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: pill.clicked()
    }
}
