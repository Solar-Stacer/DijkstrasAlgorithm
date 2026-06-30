from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import QtWidgets as qtw
from random import randint
from math import inf

class NodeItemText(qtw.QGraphicsTextItem):
    """
    A class that provides every Node an uneditable text item that is set to be the value of the Node.
    """
    def __init__(self, Node):
        super().__init__()
        # self.text_flag = qtc.Qt.TextEditorInteraction
        # self.setTextInteractionFlags(self.text_flag)

        font = qtg.QFont()
        font.setPointSize(15)
        self.setFont(font)
        self.setDefaultTextColor("white")

        self.text = Node.value
        self.setTextWidth(Node.boundingRect().width())
        self.setHtml(f"<div style='text-align: center;'>{self.text}</div>")

        center_self = self.boundingRect()
        center_node = Node.boundingRect().center()
        center_self.moveCenter(center_node)

        self.setPos(center_self.topLeft())

    def changeText(self, value):
        self.text = value
        self.setHtml(f"<div style='text-align: center;'>{self.text}</div>")


class NodeItem(qtw.QGraphicsObject):
    """
    The Main Node class represent all Node objects in the Scene.
    """
    count = 0
    active_nodes = {}
    index = 0

    NodeItem_RemoveSelf_Request = qtc.Signal()
    NodeTable_ChangeValue_Request = qtc.Signal(object)
    NodeTable_Remove_Request = qtc.Signal(object)
    NodeTable_Add_Request = qtc.Signal(object)
    NodeTable_Select_Request = qtc.Signal(object)
    NodeTable_Deselect_Request = qtc.Signal(object)
    ConnectTable_Remove_Request = qtc.Signal(object)

    def __repr__(self):
        return f"{self.name} with value {self.value}"

    def __init__(self, width, height, override_addToWidget=True):
        super().__init__()
        # Stores the number of edges it is connected
        self.connect_item_dict = {}
        # Stores the path to source node by storing nodes in order
        self.path_to_source_node = {}
        self.name = "Node " + str(NodeItem.index)
        self.value = inf
        self.pen_width = 3
        self.node_color = qtg.QColor(200, 0, 255)
        NodeItem.index += 1
        NodeItem.count += 1

        self._rect = qtc.QRectF(0, 0, width + self.pen_width, height + self.pen_width)
        self.setPos(-randint(0, width * 2), -randint(0, height * 2))

        center_rect = self._rect.center()
        self.draw_rect = qtc.QRectF(0, 0, width, height)
        self.draw_rect.moveCenter(center_rect)
        self.setToolTip(f"{self.name}")

        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.NodeItem_RemoveSelf_Request.connect(self.removeSelf)
        if override_addToWidget:
            self.addToWidgets()

    def addToWidgets(self):
        self.text = NodeItemText(self)
        self.text.setParentItem(self)
        NodeItem.active_nodes.update({self.name: self})

    def emit_NodeTable_Add_Request(self):
        self.NodeTable_Add_Request.emit(self)

    def paint(self, painter, option, widget=None):
        if not self.isSelected():
            painter.setBrush(self.node_color)
            painter.setPen(qtg.QPen(qtg.QColor(0, 0, 0), self.pen_width))
            painter.drawEllipse(self.draw_rect)
        else:
            painter.setBrush(self.node_color)
            painter.setPen(qtg.QPen(qtg.QColor(0, 255, 255), self.pen_width))
            painter.drawEllipse(self.draw_rect)

    def boundingRect(self):
        return self._rect

    def setValue(self, value):
        """
        Only run by DijkstraFunction.py to change the value of the node.
        """
        self.value = value
        self.text.changeText(self.value)
        self.NodeTable_ChangeValue_Request.emit(self)
        self.setToolTip(f"{self.name}")

    def shape(self):
        """
        For modifying the area where the node is clickable.
        The area is a circle of radius by the painted circle,
        not a default square.
        """
        path = qtg.QPainterPath()
        path.addEllipse(self.draw_rect)
        return path

    def __lt__(self, other):
        """
        Required by DijkstraFunction.py for max-heap.
        """
        return self.index < other.index

    @qtc.Slot()
    def removeSelf(self):
        for line in list(self.connect_item_dict.values()):
            line.ConnectLine_RemoveSelf_Request.emit()
        NodeItem.active_nodes.pop(self.name)
        NodeItem.count -= 1
        self.scene().removeItem(self)
        self.NodeTable_Remove_Request.emit(self)

    """
    The following two functions is responsible for the ability to move the nodes.
    ItemIsMovableFlag is not used because it causes a lot of glitches and issues.
    """
    def mousePressEvent(self, event):
        if event.button() == qtc.Qt.MouseButton.LeftButton:
            self.drag_offset = event.pos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & qtc.Qt.MouseButton.LeftButton:
            self.setPos(
                event.scenePos() - self.drag_offset
            )

    def itemChange(self, change, value):
        # Responsible for selecting the relevant node entry in NodeTable when the node is selected
        if change == qtw.QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.NodeTable_Select_Request.emit(self)
                self.update()
            else:
                self.NodeTable_Deselect_Request.emit(self)
                self.update()

        # Responsible for adjusting the edge when the node is moved so that the edge remains connected
        if change == qtw.QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for connect in self.connect_item_dict.values():
                connect.adjust()
        return qtw.QGraphicsItem.itemChange(self, change, value)

    def appendConnectItem(self, connect_item):
        # Appends the edge to the node's connect_item dictionary
        self.connect_item_dict.update({f"{connect_item.name}": connect_item})


class SourceNodeItem(NodeItem):
    """
    A Node class that inherits from NodeItem. This Node cannot be deleted by right-clicking.
    It has an index of 0 and is the fist node created.
    """
    def __init__(self, width, height):
        super().__init__(width, height, override_addToWidget=False)
        self.name = "Source Node"
        self.value = 0
        self.node_color = qtg.QColor(255, 0, 0)
        self.setToolTip(f"{self.name}")
        self.addToWidgets()

    def addToWidgets(self):
        self.text = NodeItemText(self)
        self.text.setParentItem(self)
        NodeItem.active_nodes.update({self.name: self})