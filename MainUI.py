from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import QtWidgets as qtw
from DijkstraFunction import dijkstra, getPathToSourceNode
from HelpDialogs import DijkstraDescriptionDialog, HowToUseDialog, AboutDialog
from NodeClasses import *
from ConnectClasses import *
import os, sys
import resources_rc

class ConnectItemTable(qtw.QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Connect", "Start", "End", "Value"])
        self.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(qtw.QAbstractItemView.EditTrigger.NoEditTriggers)

    @qtc.Slot(object)
    def selectEdge(self, line):
        self.setSelectionBehavior(qtw.QAbstractItemView.SelectionBehavior.SelectRows)
        item = self.findItems(line.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        self.selectRow(item[0].row())

    @qtc.Slot(object)
    def deselectEdge(self, line):
        item = self.findItems(line.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        model = self.model()
        selection_model = self.selectionModel()
        for i in range(self.columnCount()):
            index = model.index(item[0].row(), i)
            selection_model.select(index, qtc.QItemSelectionModel.SelectionFlag.Deselect)

    @qtc.Slot(object)
    def addConnectItem(self, connect_item):
        self.setRowCount(ConnectLineItem.count)
        item_key = qtw.QTableWidgetItem(connect_item.name)
        item_start = qtw.QTableWidgetItem(str(connect_item.start_node.name))
        item_end = qtw.QTableWidgetItem(str(connect_item.end_node.name))
        item_value = qtw.QTableWidgetItem(str(connect_item.value))
        self.setItem(ConnectLineItem.count - 1, 0, item_key)
        self.setItem(ConnectLineItem.count - 1, 1, item_start)
        self.setItem(ConnectLineItem.count - 1, 2, item_end)
        self.setItem(ConnectLineItem.count - 1, 3, item_value)

    @qtc.Slot(object)
    def removeConnectItem(self, connect_item):
        item = self.findItems(connect_item.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        self.removeRow(item[0].row())

    @qtc.Slot(object)
    def changeTableValue(self, connect_item):
        item = self.findItems(connect_item.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        row = item[0].row()
        self.item(row, 3).setText(str(connect_item.value))


class NodeTable(qtw.QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Node", "Value", "Previous Node"])
        self.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(qtw.QAbstractItemView.EditTrigger.NoEditTriggers)

    @qtc.Slot(object)
    def selectNode(self, node):
        self.setSelectionBehavior(qtw.QAbstractItemView.SelectionBehavior.SelectRows)
        item = self.findItems(node.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        self.selectRow(item[0].row())

    @qtc.Slot(object)
    def deselectNode(self, node):
        item = self.findItems(node.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        model = self.model()
        selection_model = self.selectionModel()
        for i in range(self.columnCount()):
            index = model.index(item[0].row(), i)
            selection_model.select(index, qtc.QItemSelectionModel.SelectionFlag.Deselect)

    @qtc.Slot(object)
    def addNodeItem(self, node):
        self.setRowCount(NodeItem.count)
        item_key = qtw.QTableWidgetItem(node.name)
        item_value = qtw.QTableWidgetItem(str(node.value))
        self.setItem(NodeItem.count - 1, 0, item_key)
        self.setItem(NodeItem.count - 1, 1, item_value)

    @qtc.Slot(object)
    def removeNodeItem(self, node):
        item = self.findItems(node.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        self.removeRow(item[0].row())

    def changePreviousNodeColumn(self, node, previous_node):
        item = self.findItems(node.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        prev_item = qtw.QTableWidgetItem(previous_node.name)
        self.setItem(item[0].row(), 2, prev_item)

    def clearPreviousNodeColumn(self):
        for row in range(self.rowCount()):
            item = self.item(row, 2)
            if item is not None:
                item.setText("")

    @qtc.Slot(object)
    def changeTableValue(self, node_item):
        item = self.findItems(node_item.name, qtc.Qt.MatchFlag.MatchExactly | qtc.Qt.MatchFlag.MatchExactly)
        row = item[0].row()
        self.item(row, 1).setText(str(node_item.value))

class Scene(qtw.QGraphicsScene):
    """
    A class that inherits from QGraphicsScene. Created separately instead of
    creating an instance of QGraphicsScene directly in the QMainWindow to override
    multiple functions to provide custom background, and modify mouse events.
    """
    grid = 30

    def __init__(self, main_window, width, height, node_table, connect_table):
        super().__init__()
        self.setSceneRect(qtc.QRectF(-width / 2, -height / 2, width, height))
        self.node_table = node_table
        self.connect_table = connect_table
        self.window = main_window


    def drawBackground(self, painter, rect):
        # Create the grid background
        painter.fillRect(rect, qtg.QColor(30, 30, 30))
        left = int(rect.left()) - int((rect.left()) % self.grid)
        top = int(rect.top()) - int((rect.top()) % self.grid)
        right = int(rect.right())
        bottom = int(rect.bottom())
        lines = []
        for x in range(left, right, self.grid):
            lines.append(qtc.QLine(x, top, x, bottom))
        for y in range(top, bottom, self.grid):
            lines.append(qtc.QLine(left, y, right, y))
        painter.setPen(qtg.QPen(qtg.QColor(50, 50, 50)))
        painter.drawLines(lines)

    def mousePressEvent(self, event):
        """
        If the mouse is right-clicked on a ConnectItem, or a NodeItem, then
        the function will delete the top most item under the mouse cursor.
        """
        if event.button() == qtc.Qt.MouseButton.RightButton:
            clicked_items = self.items(event.scenePos())
            node_and_connect_items = [x for x in clicked_items
                          if (isinstance(x, NodeItem) and not isinstance(x, SourceNodeItem))
                          or isinstance(x, ConnectLineItem)]
            if node_and_connect_items:
                if isinstance(node_and_connect_items[0], ConnectLineItem):
                    node_and_connect_items[0].ConnectLine_RemoveSelf_Request.emit()
                elif isinstance(node_and_connect_items[0], NodeItem):
                    node_and_connect_items[0].NodeItem_RemoveSelf_Request.emit()

        #if self.itemAt(event.scenePos(), qtg.QTransform()) is None:
        #    self.clearSelection()
        #    self.node_table.clearSelection()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """
        If a node is clicked and then Alt key is pressed, then it creates an
        edge between the nodes and adds it to the scene.
        """
        if event.key() == qtc.Qt.Key.Key_Alt:
            selectedItems = self.selectedItems()
            selectedNodes = [item for item in selectedItems if isinstance(item, NodeItem)]
            if len(selectedNodes) == 2:
                startNodeConnectItems = selectedNodes[0].connect_item_dict.keys()
                endNodeConnectItems = selectedNodes[1].connect_item_dict.keys()
                selectedStartNode = selectedNodes[0]
                selectedEndNode = selectedNodes[1]
                if not (set(endNodeConnectItems) & set(startNodeConnectItems)):
                    connect = ConnectLineItem(selectedStartNode, selectedEndNode)
                    connect.ConnectTable_Add_Request.connect(self.connect_table.addConnectItem)
                    connect.ConnectTable_Remove_Request.connect(self.connect_table.removeConnectItem)
                    connect.ConnectTable_ChangeValue_Request.connect(self.connect_table.changeTableValue)
                    connect.ConnectTable_Select_Request.connect(self.connect_table.selectEdge)
                    connect.ConnectTable_Deselect_Request.connect(self.connect_table.deselectEdge)
                    connect.emit_ConnectTable_Add_Request()
                    self.addItem(connect)
        super().keyPressEvent(event)


class View(qtw.QGraphicsView):
    """
    A class that inherits from QGraphicsView. Created separately instead of
    creating an instance of QGraphicsView directly in the QMainWindow to override
    QGraphicsView's wheelEvent to allow zoom in and out.
    """
    def __init__(self, main_window):
        super().__init__()
        self.window = main_window

    def wheelEvent(self, event):
        """
        Checks whether the wheel of the mouse is scrolled. When it is scrolled,
        while the Control key is pressed, the Scene zooms in or out by calling
        zoom_in() and zoom_out() respectively. They change the scale of the scene.
        """
        if not event.modifiers() & qtc.Qt.KeyboardModifier.ControlModifier:
            event.ignore()
            return

        # Calculates the change in wheel scroll and if it is positive, it zooms in
        # otherwise it zooms out.
        angle_delta = event.angleDelta()
        if angle_delta.y() > 0:
            self.window.zoom_in()
        if angle_delta.y() < 0:
            self.window.zoom_out()
        event.accept()


class MainWindow(qtw.QMainWindow):
    """
    The class that contains the entire application widgets.
    """
    def __init__(self):
        # Call the constructor of QMainWindow
        super().__init__()

        self.Node = None

        # Set up the window title and icon
        self.setWindowTitle("Dijkstra's Algorithm")
        self.setWindowIcon(qtg.QIcon(":/icon.png"))
        self.setFixedSize(1000, 600)

        # Create the node and edge table
        self.node_table = NodeTable()
        self.connect_table = ConnectItemTable()

        # Define height and width of the Scene and create the Scene
        # This Scene will contain the Nodes and Edges
        width, height = 600, 500
        self.scene = Scene(self, width, height, self.node_table, self.connect_table)

        self.startNode = SourceNodeItem(50, 50)
        self.startNode.NodeTable_Add_Request.connect(self.node_table.addNodeItem)
        self.startNode.NodeTable_ChangeValue_Request.connect(self.node_table.changeTableValue)
        self.startNode.NodeTable_Remove_Request.connect(self.node_table.removeNodeItem)
        self.startNode.NodeTable_Select_Request.connect(self.node_table.selectNode)
        self.startNode.NodeTable_Deselect_Request.connect(self.node_table.deselectNode)
        self.startNode.ConnectTable_Remove_Request.connect(self.connect_table.removeConnectItem)
        self.startNode.emit_NodeTable_Add_Request()
        self.scene.addItem(self.startNode)

        # Create the QGraphicsView for rendering the Scene
        self.view = View(self)
        self.view.setScene(self.scene)
        self.view.setRenderHint(qtg.QPainter.RenderHint.Antialiasing)

        # Remove the light trails formed when moving the Node objects by updating the Viewport
        self.view.setViewportUpdateMode(qtw.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # Add menus to the QMainWindow by calling addMenu() of the QMainWindow class
        # Add actions to those menus and connect slots to their triggered signal.
        self.menu = self.menuBar()
        self.help_menu = self.menu.addMenu("&Help")
        self.how_use_action = qtg.QAction("&How to Use?", self)
        self.what_algo_action = qtg.QAction("&What is Dijkstra's Algorithm?", self)
        self.about_action = qtg.QAction("&About", self)
        self.help_menu.addAction(self.how_use_action)
        self.help_menu.addAction(self.what_algo_action)
        self.help_menu.addAction(self.about_action)
        self.how_use_action.triggered.connect(self.showHowToUse)
        self.what_algo_action.triggered.connect(self.showDijkstraDescription)
        self.about_action.triggered.connect(self.showAbout)

        # Add buttons, add them to the button_layout and connect their clicked signals to the slots
        self.add_node_button_item = qtw.QPushButton("Add Node")
        self.calculate_button_item = qtw.QPushButton("Run Dijkstra's Algorithm")
        button_layout = qtw.QVBoxLayout()
        button_layout.addWidget(self.add_node_button_item)
        button_layout.addWidget(self.node_table)
        button_layout.addWidget(self.connect_table)
        button_layout.addWidget(self.calculate_button_item)
        self.add_node_button_item.clicked.connect(self.addNodeItem)
        self.calculate_button_item.clicked.connect(self.DijkstraAlgorithm)

        # Add layouts and widget to the main_layout, set it as a container widget
        # and set that as the central widget of the QMainWindow
        main_layout = qtw.QHBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.view)
        container = qtw.QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.show()
        self.showHowToUse()
        self.centerWindow()

    def centerWindow(self):
        """
        Centers the window by obtaining the QRect of the screen, finding its center, then
        obtaining the QRect of the window of self as a variable window_frame, moves the
        center of QRect of the window_frame to the center of the screen, and finally moves
        self to the top left corner of the window_frame.
        """
        screen_geometry = qtg.QScreen.availableGeometry(qtw.QApplication.primaryScreen())
        screen_center = screen_geometry.center()
        window_frame = self.frameGeometry()
        window_frame.moveCenter(screen_center)
        self.move(window_frame.topLeft())

    @qtc.Slot()
    def showDijkstraDescription(self):
        """
        Instantiates the Dijkstra's Algorithm Description dialog and shows it.
        """
        dialog = DijkstraDescriptionDialog()
        dialog.exec()

    @qtc.Slot()
    def showHowToUse(self):
        """
        Instantiates the How To Use dialog and shows it.
        """
        dialog = HowToUseDialog()
        dialog.exec()

    @qtc.Slot()
    def showAbout(self):
        """
        Instantiates the About dialog and shows it.
        """
        dialog = AboutDialog()
        dialog.exec()


    @qtc.Slot()
    def addNodeItem(self):
        """
        Adds a NodeItem to the Scene.
        """
        self.Node = NodeItem(50, 50)
        self.Node.NodeTable_Add_Request.connect(self.node_table.addNodeItem)
        self.Node.NodeTable_ChangeValue_Request.connect(self.node_table.changeTableValue)
        self.Node.NodeTable_Remove_Request.connect(self.node_table.removeNodeItem)
        self.Node.NodeTable_Select_Request.connect(self.node_table.selectNode)
        self.Node.NodeTable_Deselect_Request.connect(self.node_table.deselectNode)
        self.Node.ConnectTable_Remove_Request.connect(self.connect_table.removeConnectItem)
        self.Node.emit_NodeTable_Add_Request()
        self.scene.addItem(self.Node)

    @qtc.Slot()
    def DijkstraAlgorithm(self):
        """
        This function calculate the shortest distance between the source node
        to every other nodes.
        """

        # This loop ensures that all the Nodes (except the source Node) are set
        # to inf before calculation.
        for entry in NodeItem.active_nodes.values():
            entry.path_to_source_node.clear()
            self.node_table.clearPreviousNodeColumn()
            if entry.name == "Source Node":
                continue
            else:
                if entry.value != inf:
                    entry.setValue(inf)

        # Then, dijkstra is called with NodeItem.active_nodes dictionary
        # containing all the nodes as the argument.
        dijkstra(NodeItem.active_nodes)

        # This second for loop determines the previous node for each node when shortest
        # distance between them was calculated and updates them in the Node Table.
        for entry in NodeItem.active_nodes.values():
            getPathToSourceNode(entry)
            #print(entry.path_to_source_node) #  Enable this to see the path to source node for every node.
            if entry.path_to_source_node.values():
                previous_entry = list(entry.path_to_source_node.values())[0]
                self.node_table.changePreviousNodeColumn(entry, previous_entry)

    def zoom_in(self):
        self.view.scale(1.1, 1.1)

    def zoom_out(self):
        self.view.scale(0.9, 0.9)


if "__main__" == __name__:
    app = qtw.QApplication(sys.argv)
    w = MainWindow()

    sys.exit(app.exec())
