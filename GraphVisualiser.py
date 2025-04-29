from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QStackedWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
import random
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout

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

        self.strategy_window = StrategyWindow(self)
        self.stacked_widget.addWidget(self.strategy_window)

        self.auto_strategy_window = AutomatedStrategyWindow(self)
        self.stacked_widget.addWidget(self.auto_strategy_window)

    """Switch to the game window."""
    def switch_to_game_window(self, graph, pos, node_size):
        self.game_window.update_graph(graph, pos, node_size)
        self.game_window.display_graph()
        self.stacked_widget.setCurrentIndex(1)

    def switch_to_strategy_window(self, graph, pos, node_size):
        self.strategy_window.update_graph(graph, pos, node_size)
        self.strategy_window.display_graph()
        self.strategy_window.cop_strategy()
        self.stacked_widget.setCurrentIndex(2)
    
    def switch_to_auto_strategy_window(self, graph, pos, node_size):
        self.auto_strategy_window.update_graph(graph, pos, node_size)
        self.auto_strategy_window.display_graph()
        self.auto_strategy_window.cop_strategy()
        self.stacked_widget.setCurrentIndex(3)
        
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

        # Submit Buttons
        submit_layout = QHBoxLayout()

        # Button to submit graph - To normal game window
        self.button_submit = QPushButton("Submit (Vs. Player)", self)
        self.button_submit.clicked.connect(self.submit_graph)
        submit_layout.addWidget(self.button_submit)

        # Button to submit graph - To normal strategy window
        self.button_submit = QPushButton("Submit (Vs. Strategy)", self)
        self.button_submit.clicked.connect(self.submit_graph_strategy)
        submit_layout.addWidget(self.button_submit)

        # Button to submit graph - To automated strategy window
        self.button_submit = QPushButton("Submit (Vs. Auto Strategy)", self)
        self.button_submit.clicked.connect(self.submit_graph_auto_strategy)
        submit_layout.addWidget(self.button_submit)
        layout.addLayout(submit_layout)

        # Matplotlib Figure
        self.canvas = FigureCanvas(Figure())
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

            if not (1 <= rows <= 100 and 1 <= cols <= 100):
                self.label.setText("Error: Rows & Columns must be between 1 and 20.")
                return
            
            self.label.setText(f"Grid {rows} × {cols}")

            # Create the grid graph
            self.graph = nx.grid_2d_graph(rows, cols)

            # Update the posistions so the graph forms a grid
            self.pos = {(x, y): (y, -x) for x, y in self.graph.nodes()}  # Invert y for correct orientation from networkX to matplotlib

            # Update node size dynamically as node number increases and canvas size changes
            area_per_node = (self.canvas.width() * self.canvas.height()) / (rows * cols)
            self.node_size = max(10, min(300, int(area_per_node * 0.05)))

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
        nx.draw(self.graph, self.pos, ax=ax, with_labels=False, node_color="#6699cc", edge_color="#cccccc", node_size=self.node_size)
        self.canvas.figure.tight_layout(pad=0)
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

    def submit_graph_strategy(self):
        if not self.graph:
            return

        # Disconnect the mouse click event
        self.canvas.mpl_disconnect(self.mouse_click_cid)

        self.parent.switch_to_strategy_window(self.graph, self.pos, self.node_size)
    
    def submit_graph_auto_strategy(self):
        if not self.graph:
            return

        # Disconnect the mouse click event
        self.canvas.mpl_disconnect(self.mouse_click_cid)

        self.parent.switch_to_auto_strategy_window(self.graph, self.pos, self.node_size)

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

    """Update the stored graph info."""
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

    """Check for if cop has captured robber"""
    def check_game_over(self):
        for cop in self.cop_nodes:
            if cop == self.robber_node:
                self.turn_label.setText("Game Over, Cops captured the robber")
                self.canvas.mpl_disconnect(self.mouse_click_cid)

class StrategyWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Initialize graph info
        self.graph = None
        self.pos = {}
        self.node_size = None
        self.highlight_moves = True

        # Player States
        self.cop_nodes = []
        self.robber_node = None
        self.cop1_pointer = 0
        self.cop2_pointer = 1
        self.guarding = [False, False]
        self.target_column_path = []
        self.target_node = None
        self.target_path = []
        self.cop1_guarded = False
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

    """Update the stored graph info."""
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
        if self.highlight_moves:
            if not self.is_placement_phase:

                # Single robber so legal moves only based on single node neighbours
                if self.is_robber_turn:
                    legal_moves = list(self.graph.neighbors(self.robber_node))
                    legal_moves.append(self.robber_node)
                else:
                    legal_moves=[]
            # In placement phase any node is a legal move unless occupied 
            else:
                legal_moves = [node for node in self.graph.nodes if node not in self.cop_nodes]
        else:
            legal_moves=[]
        
        
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
            self.make_move(closest_node)

    """Make a move for the robber or cop"""
    def make_move(self, closest_node):         
        if self.is_placement_phase:
            self.robber_node = closest_node
            self.is_robber_turn = not self.is_robber_turn
            self.is_placement_phase = False
            self.cop_strategy()
        else:
            # Check if node near mouse click is a neighbour of player posistion node, the current node
            current_node = self.robber_node
            is_valid_move = closest_node in self.graph.neighbors(current_node) or closest_node == current_node
            
            # Check to see if the clicked node is a valid move for any of the players
            if is_valid_move:
                
                # Update player node as node clicked is a valid move only if its their turn
                self.robber_node = closest_node
                self.is_robber_turn = not self.is_robber_turn
                self.turn_label.setText("Cop's Turn")
                self.cop_strategy()

        self.display_graph()
        self.check_game_over()
        
    """Check for if cop has captured robber"""
    def check_game_over(self):
        for cop in self.cop_nodes:
            if cop == self.robber_node:
                self.turn_label.setText("Game Over, Cops captured the robber")
                self.canvas.mpl_disconnect(self.mouse_click_cid)

    """Handles logic for deciding cops moves to implement strategy of capturing robber"""
    def cop_strategy(self):
        if self.is_placement_phase:
            if not self.is_robber_turn:
                # Place C1 in a right most column path in its centre
            
                # Find the column furthest to the right of the graph
                rightmost_column = max(x for (y, x) in self.graph.nodes)

                # Collect all nodes from that column in a sorted list
                rightmost_nodes = [(y, x) for (y, x) in self.graph.nodes if x == rightmost_column]

                # Find far right node in the highest row, which has the lowest y
                top_right_node = min(rightmost_nodes, key=lambda node: node[0])
                
                c1_column_path = self.find_column_path(top_right_node)
                
                # Place C1 in the middle of column path
                mid_index = len(c1_column_path) // 2
                self.cop_nodes.append(c1_column_path[mid_index])

                # Place C2 in the adjacent column path to C1
                # Find a node in the adjacent column which has an edge to C1 column path
                c2_column_path = c1_column_path
                for node in c1_column_path:
                    y, x = node
                    test_node = (y, x-1) 
                    if(test_node in self.graph.nodes):
                        if ((node, test_node) in self.graph.edges):
                            c2_column_path = self.find_column_path(test_node)
                            break

                mid_index = len(c2_column_path) // 2
                self.cop_nodes.append(c2_column_path[mid_index])

                self.target_column_path = c1_column_path
                self.guarding = [False, True]
                self.turn_label.setText("Robber's Placement Phase")
                self.is_robber_turn = not self.is_robber_turn
        else:
            # Cop 1 Move
            cop1 = self.cop_nodes[self.cop1_pointer]
            # Check if C1 is on the target column path
            if(cop1 in self.target_column_path):

                # Since Cop 1 is on column path, Check if guarded based on robber posistion 
                # Find the closest node on target path to robber, compare distance from cop and robber to that node
                robber_target, robber_target_path = self.shortest_path_to_column_path(self.robber_node, self.target_column_path)
                cop_to_robber_target = nx.shortest_path_length(self.graph, self.cop_nodes[self.cop1_pointer], robber_target)

                # If Cop 1 can get to that node quicker than the column path is gaureded
                if (cop_to_robber_target < len(robber_target_path)):
                    self.cop1_guarded = True

                # If Cop 1 doesn't guard column at current posistion must move closer node closer to robber on the column path
                else:
                    self.guard_column_path(self.cop1_pointer)
        
            # If Cop 1 not on target column path make move towards it
            else:

                # Check if we have a target node to aim for on the target column path
                if self.target_node not in self.target_column_path:

                    # target node on target column path and path from cop1 to that target node
                    self.target_node, self.target_path = self.shortest_path_to_column_path(cop1, self.target_column_path)
    
                # Find Cop 1 on the target path and interate it to follow the path to the target node
                for i in range(0, len(self.target_path)):
                    if self.cop_nodes[self.cop1_pointer] == self.target_path[i]:
                        self.cop_nodes[self.cop1_pointer] = self.target_path[i+1]
                        break

            # Cop 2 Move
            cop2_column = self.cop_nodes[self.cop2_pointer][1]
            cop2_row = self.cop_nodes[self.cop2_pointer][0]
            cop2_column_path = self.find_column_path(self.cop_nodes[self.cop2_pointer])
            robber_target, robber_target_path = self.shortest_path_to_column_path(self.robber_node, cop2_column_path)
            cop_to_robber_target = nx.shortest_path_length(self.graph, self.cop_nodes[self.cop2_pointer], robber_target)

            # Check if Cop 2 based on their current posistion still guards the column path they are on
            if not (cop_to_robber_target < len(robber_target_path)):
                self.guard_column_path(self.cop2_pointer)

            # Cop 1 and Cop 2 swap roles if Cop 1 sucessfully guards their column path, as it frees up Cop 2 to find a new column path to guard
            if self.cop1_guarded:
                # Find Connected Components after G-P and of them the connected component the robber is in
                graph_modified = self.graph.copy()
                graph_modified.remove_nodes_from(self.target_column_path)
                components = list(nx.connected_components(graph_modified))
                for component in components:
                    if self.robber_node in component:
                        robber_component = component

                # Check for nodes which reside on the adjacent column path in the robber's component
                adjacent_path_node = None
                for node in self.target_column_path:
                    y, x = node
                    test_nodes = [(y, x-1), (y, x+1)]
                    for test_node in test_nodes:
                        if(test_node in self.graph.nodes):
                            if ((node, test_node) in self.graph.edges):
                                if test_node in robber_component:
                                    adjacent_path_node = test_node
                if adjacent_path_node:
                    self.target_column_path = self.find_column_path(adjacent_path_node)
                # Swap the Cop 1 and Cop 2 pointers
                temp = self.cop1_pointer
                self.cop1_pointer = self.cop2_pointer
                self.cop2_pointer = temp
                self.cop1_guarded = False

            self.is_robber_turn = not self.is_robber_turn
            self.turn_label.setText("Robber's Turn")

        self.display_graph()
        self.check_game_over()

    """Finds a column path that a given node resides in"""
    def find_column_path(self, node):
        # Get the y and x of the node
        y, x = node

        # Search up, form a list of connected nodes above it
        upper_list = []

        # All nodes in the column above the given node
        upper_nodes = [n for n in self.graph.nodes if n[1] == x and n[0] < y]
        upper_nodes.sort(key=lambda n: n[0], reverse=True)
        if upper_nodes:

            # Checks if node above is connected meaning its in column path
            if( (node, upper_nodes[0]) in self.graph.edges):
                upper_list.append(upper_nodes[0])

                # Continues up the column adding connedcted nodes to column path
                for i in range(1, len(upper_nodes)):
                    if( (upper_nodes[i-1], upper_nodes[i]) in self.graph.edges):
                        upper_list.append(upper_nodes[i])
                    
                    # Once a disconnected node is found an end point of column path is found so break
                    else:
                        break

        # Search down, form a list of connected node below it
        lower_list = []

        # All nodes in the column below the given node
        lower_nodes = [n for n in self.graph.nodes if n[1] == x and n[0] > y]
        lower_nodes.sort(key=lambda n: n[0])
        if lower_nodes:

            # Checks if node below is connected meaning its in column path
            if( (node, lower_nodes[0]) in self.graph.edges):
                lower_list.append(lower_nodes[0])

                # Continues down the column adding connedcted nodes to column path
                for i in range(1, len(lower_nodes)):
                    if( (lower_nodes[i-1], lower_nodes[i]) in self.graph.edges):
                        lower_list.append(lower_nodes[i])

                    # Once a disconnected node is found an end point of column path is found so break
                    else:
                        break

        # Combine lists to form the complete column path
        column_path=[]
        column_path.extend(upper_list)
        column_path.append(node)
        column_path.extend(lower_list)
        return column_path

    """Finds the cloest node in a column path to a given node and the path of ndoes to it"""
    def shortest_path_to_column_path(self, node, column_path):
        # Defaults the cloest node and shortest path to be first node in column path
        shortest_path = nx.shortest_path_length(self.graph, node, column_path[0])
        target_node = column_path[0]
        target_path = nx.shortest_path(self.graph, node, target_node)

        # Loops through to check rest of column path
        for i in range(1, len(column_path)):
            
            # If current node has a shorter path, it becomes the target node and shortest path
            test_path = nx.shortest_path_length(self.graph, node, column_path[i])
            if(shortest_path > test_path):
                shortest_path = test_path
                target_node = column_path[i]
                target_path = nx.shortest_path(self.graph, node, target_node)
        
        return target_node, target_path

    """Moves cop up or down to be closer to robber's row"""
    def guard_column_path(self, cop_pointer):
        # Given cop information
        cop_column = self.cop_nodes[cop_pointer][1]
        cop_row = self.cop_nodes[cop_pointer][0]

        # Robber information
        robber_row = self.robber_node[0]

        # Check if robber is above cop
        if(cop_row > robber_row):

            # Move towards them if possible move exists
            next_move = (cop_row-1, cop_column)
            if (next_move in self.graph.nodes):
                self.cop_nodes[cop_pointer] = next_move 
        
        # Check if robber is below cop
        elif(cop_row < robber_row):

            # Move towards them if possible move exists
            next_move  = (cop_row+1, cop_column)
            if (next_move in self.graph.nodes):
                self.cop_nodes[cop_pointer] = next_move 

class AutomatedStrategyWindow(StrategyWindow):
    def __init__(self, parent):
        super().__init__(parent)

         # Initialize graph info
        self.graph = None
        self.pos = {}
        self.node_size = None
        self.highlight_moves = False

        # Player States
        self.cop_nodes = []
        self.robber_node = None
        self.cop1_pointer = 0
        self.cop2_pointer = 1
        self.guarding = [False, False]
        self.target_column_path = []
        self.target_node = None
        self.target_path = []
        self.cop1_guarded = False
        # Game States
        self.is_game_over = False
        self.is_robber_turn = False
        self.is_placement_phase = True
     
        # Clear old layout
        old_layout = self.layout()  # Get the existing layout
        if old_layout is not None:
            QWidget().setLayout(old_layout)

        # Set up layout and canvas
        layout = QVBoxLayout(self)

        self.turn_label = QLabel("Cop's Placement Phase", self)
        layout.addWidget(self.turn_label)

        self.turn_count = 0 
        self.turn_count_label = QLabel(f"Turn: {self.turn_count}", self)
        layout.addWidget(self.turn_count_label)

        # Button to start automation
        self.button_submit = QPushButton("Start", self)
        self.button_submit.clicked.connect(self.automation)
        layout.addWidget(self.button_submit)

        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)
    
    """Handles the start of the automated game"""
    def automation(self):
        self.robber_strategy()
        self.button_submit.setParent(None)  
        self.button_submit.deleteLater() 

    """Handles randomized movement for robber"""
    def robber_strategy(self):
        if self.is_placement_phase:
            if not self.is_game_over:
                avaible_nodes = set(self.graph.nodes()) - set(self.cop_nodes)
                random_node = random.choice(list(avaible_nodes))
                self.robber_node = random_node
                self.is_placement_phase = False
        else:
            if not self.is_game_over:
                y, x = self.robber_node
                potential_moves = [(y, x), (y+1, x), (y-1, x), (y, x+1), (y, x-1)]
                random_node = random.choice(potential_moves)
                if random_node in self.graph:
                    self.robber_node = random_node
                
        self.turn_count += 1
        self.turn_count_label.setText(f"Turn: {self.turn_count}")
        self.is_robber_turn = not self.is_robber_turn
        self.turn_label.setText("Cop's Turn")
        self.display_graph()
        self.check_game_over()
        QTimer.singleShot(50, self.auto_cop_strategy)

    """Handles logic for deciding cops moves to implement strategy of capturing robber"""
    def auto_cop_strategy(self):
        if self.is_placement_phase:
            if not self.is_robber_turn:
                # Place C1 in a right most column path in its centre
            
                # Find the column furthest to the right of the graph
                rightmost_column = max(x for (y, x) in self.graph.nodes)

                # Collect all nodes from that column in a sorted list
                rightmost_nodes = [(y, x) for (y, x) in self.graph.nodes if x == rightmost_column]

                # Find far right node in the highest row, which has the lowest y
                top_right_node = min(rightmost_nodes, key=lambda node: node[0])
                
                c1_column_path = self.find_column_path(top_right_node)
                
                # Place C1 in the middle of column path
                mid_index = len(c1_column_path) // 2
                self.cop_nodes.append(c1_column_path[mid_index])

                # Place C2 in the adjacent column path to C1
                # Find a node in the adjacent column which has an edge to C1 column path
                c2_column_path = c1_column_path
                for node in c1_column_path:
                    y, x = node
                    test_node = (y, x-1) 
                    if(test_node in self.graph.nodes):
                        if ((node, test_node) in self.graph.edges):
                            c2_column_path = self.find_column_path(test_node)
                            break

                mid_index = len(c2_column_path) // 2
                self.cop_nodes.append(c2_column_path[mid_index])

                self.target_column_path = c1_column_path
                self.guarding = [False, True]
                self.turn_label.setText("Robber's Placement Phase")
                self.is_robber_turn = not self.is_robber_turn
                self.turn_count += 1
                self.turn_count_label.setText(f"Turn: {self.turn_count}")
                self.display_graph()
                self.check_game_over()
        else:
            if not self.is_game_over:
                # Cop 1 Move
                cop1 = self.cop_nodes[self.cop1_pointer]
                # Check if C1 is on the target column path
                if(cop1 in self.target_column_path):

                    # Since Cop 1 is on column path, Check if guarded based on robber posistion 
                    # Find the closest node on target path to robber, compare distance from cop and robber to that node
                    robber_target, robber_target_path = self.shortest_path_to_column_path(self.robber_node, self.target_column_path)
                    cop_to_robber_target = nx.shortest_path_length(self.graph, self.cop_nodes[self.cop1_pointer], robber_target)

                    # If Cop 1 can get to that node quicker than the column path is gaureded
                    if (cop_to_robber_target < len(robber_target_path)):
                        self.cop1_guarded = True

                    # If Cop 1 doesn't guard column at current posistion must move closer node closer to robber on the column path
                    else:
                        self.guard_column_path(self.cop1_pointer)
            
                # If Cop 1 not on target column path make move towards it
                else:

                    # Check if we have a target node to aim for on the target column path
                    if self.target_node not in self.target_column_path:

                        # target node on target column path and path from cop1 to that target node
                        self.target_node, self.target_path = self.shortest_path_to_column_path(cop1, self.target_column_path)
        
                    # Find Cop 1 on the target path and interate it to follow the path to the target node
                    for i in range(0, len(self.target_path)):
                        if self.cop_nodes[self.cop1_pointer] == self.target_path[i]:
                            self.cop_nodes[self.cop1_pointer] = self.target_path[i+1]
                            break

                # Cop 2 Move
                cop2_column = self.cop_nodes[self.cop2_pointer][1]
                cop2_row = self.cop_nodes[self.cop2_pointer][0]
                cop2_column_path = self.find_column_path(self.cop_nodes[self.cop2_pointer])
                robber_target, robber_target_path = self.shortest_path_to_column_path(self.robber_node, cop2_column_path)
                cop_to_robber_target = nx.shortest_path_length(self.graph, self.cop_nodes[self.cop2_pointer], robber_target)

                # Check if Cop 2 based on their current posistion still guards the column path they are on
                if not (cop_to_robber_target < len(robber_target_path)):
                    self.guard_column_path(self.cop2_pointer)

                # Cop 1 and Cop 2 swap roles if Cop 1 sucessfully guards their column path, as it frees up Cop 2 to find a new column path to guard
                if self.cop1_guarded:
                    # Find Connected Components after G-P and of them the connected component the robber is in
                    graph_modified = self.graph.copy()
                    graph_modified.remove_nodes_from(self.target_column_path)
                    components = list(nx.connected_components(graph_modified))
                    for component in components:
                        if self.robber_node in component:
                            robber_component = component

                    # Check for nodes which reside on the adjacent column path in the robber's component
                    adjacent_path_node = None
                    for node in self.target_column_path:
                        y, x = node
                        test_nodes = [(y, x-1), (y, x+1)]
                        for test_node in test_nodes:
                            if(test_node in self.graph.nodes):
                                if ((node, test_node) in self.graph.edges):
                                    if test_node in robber_component:
                                        adjacent_path_node = test_node
                    self.target_column_path = self.find_column_path(adjacent_path_node)
                    # Swap the Cop 1 and Cop 2 pointers
                    temp = self.cop1_pointer
                    self.cop1_pointer = self.cop2_pointer
                    self.cop2_pointer = temp
                    self.cop1_guarded = False

                self.turn_count += 1
                self.turn_count_label.setText(f"Turn: {self.turn_count}")
                self.is_robber_turn = not self.is_robber_turn
                self.turn_label.setText("Robber's Turn")
                self.display_graph()
                self.check_game_over()
                QTimer.singleShot(50, self.robber_strategy)
            
    """Check for if cop has captured robber"""
    def check_game_over(self):
        for cop in self.cop_nodes:
            if cop == self.robber_node:
                self.turn_label.setText("Game Over, Cops captured the robber")
                self.is_game_over = True



app = QApplication([])
window = MainApp()
window.show()
app.exec_()
