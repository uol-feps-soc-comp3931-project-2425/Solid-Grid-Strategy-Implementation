from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel
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

        # Input fields for grid dimensions
        self.label = QLabel("Enter grid dimensions (rows × cols):")
        layout.addWidget(self.label)

        self.input_rows = QLineEdit(self)
        self.input_rows.setPlaceholderText("Enter rows")
        layout.addWidget(self.input_rows)

        self.input_cols = QLineEdit(self)
        self.input_cols.setPlaceholderText("Enter cols")
        layout.addWidget(self.input_cols)

        # Button to generate graph
        self.button = QPushButton("Generate Graph", self)
        self.button.clicked.connect(self.generate_graph)
        layout.addWidget(self.button)

        # Matplotlib Figure
        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)

    def generate_graph(self):
        """Generate a grid graph based on user input and display it."""
        try:
            rows = int(self.input_rows.text())
            cols = int(self.input_cols.text())

            if not (1 <= rows <= 20 and 1 <= cols <= 20):
                self.label.setText("Error: Rows & Columns must be between 1 and 20.")
                return
            
            self.label.setText(f"Grid {rows} × {cols}")

            # Create the grid graph
            G = nx.grid_2d_graph(rows, cols)

            # Clear the previous plot
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)

            # Draw the new graph
            pos = {(x, y): (y, -x) for x, y in G.nodes()}  # Invert y for correct orientation from networkX to matplotlib
            node_size = max(50, 2000 // (rows * cols))
            nx.draw(G, pos, ax=ax, with_labels=False, node_color="lightblue", node_size=node_size)

            # Refresh the canvas
            self.canvas.draw()

        except ValueError:
            self.label.setText("Error: Please enter valid integers.")

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()