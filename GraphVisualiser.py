from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QStackedWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up stacked window to switch between defined windows
        self.setWindowTitle("Graph Visualizer")
        self.setGeometry(100, 100, 800, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.graph_creator_window = GraphCreator(self)
        self.stacked_widget.addWidget(self.graph_creator_window)

        self.game_window = GameWindow(self)
        self.stacked_widget.addWidget(self.game_window)

    """Switch to the game window."""
    def switch_to_game_window(self, graph, pos, node_size):
        self.game_window.update_graph(graph, pos, node_size)
        self.game_window.display_graph()
        self.stacked_widget.setCurrentIndex(1)

class GraphCreator(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Central widget and layout
        layout = QVBoxLayout(self)

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

        # Button to submit graph
        self.button_submit = QPushButton("Submit", self)
        self.button_submit.clicked.connect(self.submit_graph)
        layout.addWidget(self.button_submit)

        # Matplotlib Figure
        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)

        # Connect mouse click event
        self.mouse_click_cid = self.canvas.mpl_connect("button_press_event", self.on_click)

        # Instance variables for storing the graph
        self.graph = None  
        self.pos = {}  
        self.node_size = None

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
            self.graph = nx.grid_2d_graph(rows, cols)

            # Update the posistions so the graph forms a grid
            self.pos = {(x, y): (y, -x) for x, y in self.graph.nodes()}  # Invert y for correct orientation from networkX to matplotlib

            # Update node size dynamically as node number increases
            self.node_size = max(50, 4000 // (rows * cols))

            # Draw the graph
            self.redraw_graph()

        except ValueError:
            self.label.setText("Error: Please enter valid integers.")

    """Handle mouse click to remove border nodes."""
    def on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return  # Ignore clicks outside the plot

        # Define a threshold distance to decide on which clicks to count
        click_threshold = 0.25

        # Find the nearest node
        closest_node, min_distance = None, float('inf')
        for node in self.graph.nodes:
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
                self.graph.remove_node(closest_node)
                self.redraw_graph()  
    
    """Redraws the graph"""
    def redraw_graph(self):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        nx.draw(self.graph, self.pos, ax=ax, with_labels=False, node_color="lightblue", node_size=self.node_size)
        self.canvas.draw()

    """Check if a node is on the border (has a missing neighbor)."""
    def is_border_node(self, node):
        x, y = node
        #neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1), (x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)]
        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for neigh in neighbors:
            if neigh not in self.graph.nodes:
                return True
        return False

    """Check if removing a node would split the graph making it disconnected"""
    def is_removal_safe(self, node):
        
        # Count connected components before removal
        initial_components = nx.number_connected_components(self.graph)

        # Simulate removal
        graph_copy = self.graph.copy()
        graph_copy.remove_node(node)

        # Count components after simulated removal
        new_components = nx.number_connected_components(graph_copy)

        # If the number of components increased, removing this node is unsafe
        return new_components == initial_components

    """Handle submit button functionality to change window"""
    def submit_graph(self):
        if not self.graph:
            return

        # Disconnect the mouse click event
        self.canvas.mpl_disconnect(self.mouse_click_cid)

        self.parent.switch_to_game_window(self.graph, self.pos, self.node_size)

class GameWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Initialize graph info
        self.graph = None
        self.pos = {}
        self.node_size = None

        # Player States
        self.cop_nodes = []
        self.cop_moved = [False, False]
        self.robber_node = None
        self.robber_moved = False

        # Game States
        self.is_robber_turn = False
        self.is_placement_phase = True
     

        # Set up layout and canvas
        layout = QVBoxLayout(self)

        self.turn_label = QLabel("Cop's Placement Phase", self)
        layout.addWidget(self.turn_label)

        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)

        # Connect mouse click event
        self.mouse_click_cid = self.canvas.mpl_connect("button_press_event", self.on_click)

    """Update the sotred graph info."""
    def update_graph(self, graph, pos, node_size):  
        self.graph = graph
        self.pos = pos
        self.node_size = node_size

    """Display the graph."""
    def display_graph(self):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        # Draw user created graph
        nx.draw(self.graph, self.pos, ax=ax, with_labels=False, node_color="lightblue", node_size=self.node_size, node_shape='s')

        # Highlight Legal moves
        if not self.is_placement_phase:

            # Single robber so legal moves only based on single node neighbours
            if self.is_robber_turn:
                legal_moves = list(self.graph.neighbors(self.robber_node))
                legal_moves.append(self.robber_node)
            # Two cops so legal moves based on two nodes neighbours
            else:
                legal_moves=[]
                for i in range(len(self.cop_nodes)):
                    if not self.cop_moved[i]:
                        legal_moves.extend(self.graph.neighbors(self.cop_nodes[i]))
                        legal_moves.append(self.cop_nodes[i])
        # In placement phase any node is a legal move unless occupied 
        else:
            legal_moves = [node for node in self.graph.nodes if node not in self.cop_nodes]
    
        # Highlight cop and robber nodes through colour and size
        if self.cop_nodes:
            nx.draw_networkx_nodes(self.graph, self.pos, nodelist=self.cop_nodes, node_color="blue", ax=ax, node_size=self.node_size*0.7)
        if self.robber_node is not None:
            nx.draw_networkx_nodes(self.graph, self.pos, nodelist=[self.robber_node], node_color="red", ax=ax, node_size=self.node_size*0.7)

        # Highlight legal moves
        nx.draw_networkx_nodes(self.graph, self.pos, nodelist=legal_moves, node_color="black", ax=ax, node_size=self.node_size*0.2, alpha=0.7)

        self.canvas.draw()
   
    """Handle mouse click events."""
    def on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return  # Ignore clicks outside the plot

        # Define a threshold distance to decide on which clicks to count
        click_threshold = 0.25

        # Find the nearest node
        closest_node, min_distance = None, float('inf')
        for node in self.graph.nodes:
            dist = (self.pos[node][0] - event.xdata) ** 2 + (self.pos[node][1] - event.ydata) ** 2
            if dist < min_distance:
                min_distance = dist
                closest_node = node

        # Convert squared distance to actual distance for comparison
        min_distance = min_distance ** 0.5  

        # Only proceed if the click is within the threshold distance
        if min_distance > click_threshold:
            return

        # Check if the clicked node is a valid move
        if self.is_robber_turn:
            self.make_move(closest_node, "robber")
        else:
            self.make_move(closest_node, "cop")

    """Make a move for the robber or cop"""
    def make_move(self, closest_node, player):         
        if self.is_placement_phase:
            # Set starting posistion to clicked node
            if player == "robber":
                self.robber_node = closest_node
            else:

                # Adds node to list to say that is one of the cop nodes
                self.cop_nodes.append(closest_node)
                self.cop_moved[len(self.cop_nodes)-1] = True
            
            # Check if both cops have made a move
            both_moved = True
            for placed in self.cop_moved:
                if not placed:
                    both_moved = False

            # Once both cops and robber has been placed, phase changes out of the placement phase
            if both_moved and self.robber_node is not None:
                self.is_robber_turn = not self.is_robber_turn
                self.cop_moved = [False, False]
                self.is_placement_phase = False
                self.turn_label.setText("Cop's Turn")
            # Once both cops have made a move change to robbers turn
            elif both_moved:
                self.is_robber_turn = not self.is_robber_turn
                self.turn_label.setText("Robber's Placement Phase")
            else:
                self.turn_label.setText("Cop's Placement Phase 2")
        else:
            
            is_valid_move = False
            is_valid_move1 = False
            is_valid_move2 = False
            
            # Get the node where the player is currently posistioned
            if player == "robber":

                # Check if node near mouse click is a neighbour of player posistion node, the current node
                current_node = self.robber_node
                is_valid_move = closest_node in self.graph.neighbors(current_node) or closest_node == current_node
            elif player == "cop":

                # Individual checks for both cop nodes to see if clicked node is one of their neighbours
                current_node1 = self.cop_nodes[0]
                current_node2 = self.cop_nodes[1]
                is_valid_move1 = closest_node in self.graph.neighbors(current_node1) or closest_node == current_node1
                is_valid_move2 = closest_node in self.graph.neighbors(current_node2) or closest_node == current_node2
            
            # Check to see if the clicked node is a valid move for any of the players
            if is_valid_move or (is_valid_move1 or is_valid_move2):
                
                # Update player node as node clicked is a valid move only if its their turn
                if player == "robber":
                    self.robber_node = closest_node
                    self.robber_moved = True
                elif player == "cop":
                    if not self.cop_moved[0] and is_valid_move1:
                        self.cop_nodes[0] = closest_node
                        self.cop_moved[0] = True
                    elif not self.cop_moved[1] and is_valid_move2:
                        self.cop_nodes[1] = closest_node
                        self.cop_moved[1] = True
            
                # Check if both cops have made their move
                both_moved = True
                for placed in self.cop_moved:
                    if  not placed:
                        both_moved = False

                # If both cops have moved switch to robbers turn
                if both_moved:
                    self.is_robber_turn = not self.is_robber_turn
                    self.cop_moved = [False, False]
                    self.turn_label.setText("Robber's Turn")
                
                # If robber has moved switch to cops turn
                elif self.robber_moved:
                    self.robber_moved = False
                    self.is_robber_turn = not self.is_robber_turn
                    self.turn_label.setText("Cop's Turn")

        self.display_graph()
        self.check_game_over()

    def check_game_over(self):
        for cop in self.cop_nodes:
            if cop == self.robber_node:
                self.turn_label.setText("Game Over, Cops captured the robber")
                self.canvas.mpl_disconnect(self.mouse_click_cid)

app = QApplication([])
window = MainApp()
window.show()
app.exec_()