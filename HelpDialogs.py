from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QApplication, QVBoxLayout, QGridLayout
from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import QSize
import resources_rc

class HelpDialog(QDialog):
    def __init__(self, x, y, text=""):
        super().__init__()
        icon = QIcon(":/icon.png")

        self.setWindowTitle("Help")
        self.setWindowIcon(icon)
        self.setFixedSize(x, y)

        icon_label = QLabel()
        pixmap = icon.pixmap(QSize(100, 100))
        icon_label.setPixmap(pixmap)

        text_label = QLabel()
        text_label.setText(text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        text_label.setWordWrap(True)
        text_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        layout_1 = QVBoxLayout()
        layout_1.addWidget(icon_label)
        layout_1.setAlignment(icon_label, Qt.AlignmentFlag.AlignTop)
        layout_1.setContentsMargins(10,10,10,10)

        layout_2 = QHBoxLayout()
        layout_2.addLayout(layout_1)
        layout_2.addWidget(text_label)

        main_layout = QHBoxLayout()
        main_layout.addLayout(layout_2)

        self.setLayout(main_layout)

class DijkstraDescriptionDialog(HelpDialog):
    def __init__(self):
        x, y = 900, 430
        text = '''
                <h1>Dijkstra's Algorithm</h1>
                Dijkstra's algorithm is an algorithm for finding the shortest paths between nodes in a weighted graph, which may represent, for example, a road network. It was conceived by the computer scientist Edsger W. Dijkstra in 1956. The following is the procedure:
                <ol>
                <li>Create a set of all unvisited nodes: the unvisited set.</li>
                <li>Assign to every node a distance from start value: for the starting node, it is zero, and for all other nodes, it is infinity, since initially no path is known to these nodes. During execution, the distance of a node N is the length of the shortest path discovered so far between the starting node and N.</li>
                <li>From the unvisited set, select the current node to be the one with the smallest (finite) distance; initially, this is the starting node (distance zero). If the unvisited set is empty, or contains only nodes with infinite distance (which are unreachable), then the algorithm terminates by skipping to step 6. If the only concern is the path to a target node, the algorithm terminates once the current node is the target node. Otherwise, the algorithm continues.</li>
                <li>For the current node, consider all of its unvisited neighbors and update their distances through the current node; compare the newly calculated distance to the one currently assigned to the neighbor and assign the smaller one to it. For example, if the current node A is marked with a distance of 6, and the edge connecting it with its neighbor B has length 2, then the distance to B through A is 6 + 2 = 8. If B was previously marked with a distance greater than 8, then update it to 8 (the path to B through A is shorter). Otherwise, keep its current distance (the path to B through A is not the shortest).</li>
                <li>After considering all of the current node's unvisited neighbors, the current node is removed from the unvisited set. Thus a visited node is never rechecked, which is correct because the distance recorded on the current node is minimal (as ensured in step 3), and thus final. Repeat from step 3.</li>
                <li>Once the loop exits (steps 3–5), every visited node contains its shortest distance from the starting node.</li>
                </ol>
                <i>Source: Wikipedia</i>
        '''
        super().__init__(x, y, text)
        self.setWindowTitle("What is Dijkstra's Algorithm?")

class HowToUseDialog(HelpDialog):
    def __init__(self):
        x, y = 900, 430
        text = '''
        <h1>How to Use</h1>
        <ul>
        <li>To add a node, click on <b>Add Node</b> button.</li>
        <li>To delete a node, <b>right click</b> on the node.</li>
        <li>To zoom in and zoom out of the scene, <b>scroll up or down</b> respectively.</li>
        <li>The red node is the source node and cannot be deleted. The number on each node indicates its distance from the source node. <i>inf</i> is infinity.</li>
        <li>To connect two nodes with an edge, select the two nodes with the <b>Ctrl</b> key and press <b>Alt</b> key. To remove the edge, right click on the edge.</li>
        <li>The number on each edge can be edited and indicates its distance from the two nodes.</li>
        <li>To run the Dijkstra Algorithm, click the <b>Run Dijkstra's Algorithm</b> button.</li>
        <li>There are two tables on the left of the scene. The top table (<i>Node Table</i>) shows relevant information regarding the nodes present in the scene. The bottom table (<i>Edge Table</i>) shows relevant information regarding the edges present in the scene.</li>
        <li>The node table can be used to deduce the shortest distance (or the shortest path) from the Source node to a specific (destination) node. This can be done by successively looking at the <i>Previous Node</i> entry of the destination node. 
        <br>If, for instance, one wants to deduce shortest distance from Node 4 to the Source Node, one should look at the <i>Previous Node</i> entry in Node 4. Say the <i>Previous Node</i> entry says Node 7, then one should look at the <i>Previous Node</i> entry of Node 7. Then one should look at the <i>Previous Node</i> entry of the node in the <i>Previous Node</i> entry of node 7 and so on. This is repeated until Source Node is reached in the <i>Previous Node</i> entry. The path in this example would then be node 4 -> node 7 -> ... -> Source Node.</li>
        </ul>
        
        '''
        super().__init__(x, y, text)
        self.setWindowTitle("How to Use?")

class AboutDialog(HelpDialog):
    def __init__(self):
        x, y = 500, 200
        text = '''
        <h1>About</h1>
        <p style="font-size: 15px;">Made by <b><i>Solar Stacer</i></b>, in Python using the PySide6 library, the official port of the Qt framework for C++ by The Qt Company as part of the Qt for Python project.</p>
        '''
        super().__init__(x, y, text)
        self.setWindowTitle("About")


if __name__ == '__main__':
    app = QApplication([])
    d = DijkstraDescriptionDialog()
    d.show()
    h = HowToUseDialog()
    h.show()
    a = AboutDialog()
    a.show()
    app.exec()

