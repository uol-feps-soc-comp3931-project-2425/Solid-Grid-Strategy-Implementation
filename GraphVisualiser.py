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

        # Connect mouse click event
        self.canvas.mpl_connect("button_press_event", self.on_click)

        # Instance variables for storing the graph
        self.G = None  # Placeholder for the graph object
        self.pos = {}  # Placeholder for positions
        self.node_size = None # Placeholder for node size


    """Generate a grid graph based on user input and display it."""
    def generate_graph(self):
        try:
            rows = int(self.input_rows.text())
            cols = int(self.input_cols.text())

            if not (1 <= rows <= 20 and 1 <= cols <= 20):
                self.label.setText("Error: Rows & Columns must be between 1 and 20.")
                return
            
            self.label.setText(f"Grid {rows} × {cols}")

            # Create the grid graph
            self.G = nx.grid_2d_graph(rows, cols)

            # Update the posistions so the graph forms a grid
            self.pos = {(x, y): (y, -x) for x, y in self.G.nodes()}  # Invert y for correct orientation from networkX to matplotlib

            self.node_size = max(50, 2000 // (rows * cols))

            # Draw the graph
            self.redraw_graph()

        except ValueError:
            self.label.setText("Error: Please enter valid integers.")

    """Handle mouse click to remove border nodes."""
    def on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return  # Ignore clicks outside the plot

        # Define a threshold distance
        click_threshold = 0.25

        # Find the nearest node
        closest_node, min_distance = None, float('inf')
        for node in self.G.nodes:
            dist = (self.pos[node][0] - event.xdata) ** 2 + (self.pos[node][1] - event.ydata) ** 2
            if dist < min_distance:
                min_distance = dist
                closest_node = node

        # Convert squared distance to actual distance for comparison
        min_distance = min_distance ** 0.5  

        # Only proceed if the click is within the threshold distance
        if min_distance > click_threshold:
            return 
            
        # Check if the node is a border node
        if self.is_border_node(closest_node):
            if self.is_removal_safe(closest_node):
                self.G.remove_node(closest_node)  # Remove the node
                self.redraw_graph()  # Redraw the updated graph
    
    """Redraws the graph after node deletion."""
    def redraw_graph(self):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        nx.draw(self.G, self.pos, ax=ax, with_labels=False, node_color="lightblue", node_size=self.node_size)
        self.canvas.draw()

    """Check if a node is on the border (has a missing neighbor)."""
    def is_border_node(self, node):
        x, y = node
        #neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1), (x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)]
        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for neigh in neighbors:
            if neigh not in self.G.nodes:
                return True
        return False

    """Check if removing a node would split the graph."""
    def is_removal_safe(self, node):
        
        # Count connected components before removal
        initial_components = nx.number_connected_components(self.G)

        # Simulate removal
        G_copy = self.G.copy()
        G_copy.remove_node(node)

        # Count components after simulated removal
        new_components = nx.number_connected_components(G_copy)

        # If the number of components increased, removing this node is unsafe
        return new_components == initial_components

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()