import QtQuick

Flickable {
    id: panel
    contentHeight: innerCol.height
    clip: true

    default property alias content: innerCol.children

    Column {
        id: innerCol
        anchors.left: parent.left; anchors.leftMargin: 16
        anchors.right: parent.right; anchors.rightMargin: 16
        width: parent.width - 32
        spacing: 4
    }
}
