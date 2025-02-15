from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import networkx as nx

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Visualizer")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add Matplotlib figure
        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)

        # Create and plot a NetworkX graph
        G = nx.grid_2d_graph(4, 4)  # Example solid grid
        ax = self.canvas.figure.add_subplot(111)
        nx.draw(G, ax=ax, with_labels=True, node_color="lightblue")

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()