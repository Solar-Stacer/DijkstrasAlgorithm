from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import QtWidgets as qtw
from math import sin, cos, pi

import __NodeClasses


class ConnectLineItemText(qtw.QGraphicsTextItem):

    ConnectItem_Request_For_Value_Change_In_Connect_Table = qtc.Signal()

    def __init__(self, connect_item):
        super().__init__()
        # Sets the textbox interactive, i.e. editable
        self.setTextInteractionFlags(qtc.Qt.TextInteractionFlag.TextEditorInteraction)
        self.connect_item = connect_item

        font = qtg.QFont()
        font.setPointSize(15)
        self.setFont(font)
        self.setDefaultTextColor("white")

        self.text = str(connect_item.value)
        self.setTextWidth(connect_item.boundingRect().width())
        self.setHtml(f"<div style='text-align: center;'>{self.text}</div>")
        self.setDefaultTextColor(qtg.QColor("white"))
        self.setTextWidth(50)

        center_self = self.boundingRect()
        center_node = connect_item.boundingRect().center()
        center_self.moveCenter(center_node)

        self.setPos(center_self.topLeft())
        self.document().contentsChanged.connect(self.changeText)
        self.ConnectItem_Request_For_Value_Change_In_Connect_Table.connect(self.connect_item.changeValue)

    def changeText(self):
        current_value = self.toPlainText()
        self.connect_item.value = int(current_value)
        self.ConnectItem_Request_For_Value_Change_In_Connect_Table.emit()

    def updatePos(self):
        center_self = self.boundingRect()
        center_node = self.connect_item.boundingRect().center()
        center_self.moveCenter(center_node)

        self.setPos(center_self.topLeft())


class ConnectLineItem(qtw.QGraphicsObject):
    """
    Class representing the edge object between two nodes, named ConnectLineItem.
    """
    count = 0
    active_edges = {}
    index = 0

    ConnectLine_RemoveSelf_Request = qtc.Signal()
    ConnectTable_Add_Request = qtc.Signal(object)
    ConnectTable_Remove_Request = qtc.Signal(object)
    ConnectTable_ChangeValue_Request = qtc.Signal(object)
    ConnectTable_Select_Request = qtc.Signal(object)
    ConnectTable_Deselect_Request = qtc.Signal(object)

    def __init__(self, start_node, end_node):
        super().__init__()

        self.pen_width = 5
        self.name = "Connect " + str(ConnectLineItem.index)
        self.value = 0
        # Identifies the start and end node of the edge
        self.start_node = start_node
        self.end_node = end_node
        self.setZValue(-1)
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setToolTip(f"{self.name}")

        ConnectLineItem.count += 1
        ConnectLineItem.index += 1

        start_node.appendConnectItem(self)
        end_node.appendConnectItem(self)

        self._line = qtc.QLineF()

        self.prepareGeometryChange()    # notify the QGraphicsScene that the item's boundingRect is about to change
        start = self.mapFromScene(self.start_node.sceneBoundingRect().center())
        end = self.mapFromScene(self.end_node.sceneBoundingRect().center())
        self._line = qtc.QLineF(start, end)
        self.text = ConnectLineItemText(self)
        self.text.setParentItem(self)

        self.ConnectLine_RemoveSelf_Request.connect(self.removeSelf)

    def emit_ConnectTable_Add_Request(self):
        self.ConnectTable_Add_Request.emit(self)

    @qtc.Slot()
    def changeValue(self):
        self.ConnectTable_ChangeValue_Request.emit(self)

    @qtc.Slot()
    def removeSelf(self):
        self.ConnectTable_Remove_Request.emit(self)
        self.start_node.connect_item_dict.pop(self.name)
        self.end_node.connect_item_dict.pop(self.name)
        ConnectLineItem.count -= 1
        self.scene().removeItem(self)

    def adjust(self):
        self.prepareGeometryChange()
        start = self.mapFromScene(self.start_node.sceneBoundingRect().center())
        end = self.mapFromScene(self.end_node.sceneBoundingRect().center())
        self._line = qtc.QLineF(start, end)
        self.update()
        self.text.updatePos()

    def shape(self):
        """
        Sets the interactive area to around the edge item instead of the bounding rect
        of the edge item, which is the rectangle where the diagonal is the edge item.
        """
        path = qtg.QPainterPath()
        angle = 270 + self._line.angle()
        thickness = 12.0
        node_center_translation = qtc.QPointF(thickness * cos(angle * pi / 180), -thickness * sin(angle * pi / 180))

        current_angle = self._line.angle()
        circle_radius = 30
        node_circle_translation = (
            qtc.QPointF(circle_radius * cos(current_angle * pi / 180), -circle_radius * sin(current_angle * pi / 180)))
        start_node_center = self._line.p1() + node_circle_translation
        end_node_center = self._line.p2() - node_circle_translation

        point_1 = start_node_center + node_center_translation
        point_2 = end_node_center + node_center_translation
        point_3 = end_node_center - node_center_translation
        point_4 = start_node_center - node_center_translation
        points = [point_1, point_2, point_3, point_4]
        shape_poly_rect = qtg.QPolygonF(points)
        path.addPolygon(shape_poly_rect)
        return path

    def returnNeighbor(self, neighbor: __NodeClasses.NodeItem):
        """
        Only called in DijkstraFunction.py and returns node A where edge
        is between node A and B and neighbor is B.
        :param neighbor:
        :return:
        """
        if neighbor is not self.start_node:
            return self.start_node
        else:
            return self.end_node

    def itemChange(self, change, value):
        # Responsible for selecting the relevant edge entry in ConnectItemTable when the edge is selected
        if change == qtw.QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.ConnectTable_Select_Request.emit(self)
                self.update()
            else:
                self.ConnectTable_Deselect_Request.emit(self)
                self.update()

        return qtw.QGraphicsItem.itemChange(self, change, value)

    def boundingRect(self):
        extra = self.pen_width
        return qtc.QRectF(
            self._line.p1(),
            self._line.p2()
        ).normalized().adjusted(
            -extra, -extra,
            extra, extra
        )

    def paint(self, painter: qtg.QPainter, option: qtw.QStyleOptionGraphicsItem, widget: qtw.QWidget = None):
        if not self.isSelected():
            painter.setPen(qtg.QPen(qtg.QColor("#009B00"), self.pen_width))
            painter.drawLine(self._line)
        else:
            painter.setPen(qtg.QPen(qtg.QColor(0, 255, 255), self.pen_width))
            painter.drawLine(self._line)
