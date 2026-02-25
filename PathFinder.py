import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import math
from heapq import heappush, heappop

# --- Constants ---
CELL_SIZE = 25
COLORS = {
    "empty": "white",
    "wall": "black",
    "start": "blue",
    "goal": "green",
    "path": "lime green",
    "visited": "indian red",
    "frontier": "khaki",
    "agent": "orange"
}

class PathfindingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Pathfinding Agent")
        
        self.rows = 20
        self.cols = 20
        self.grid_data = []
        self.cells = []
        
        self.start_pos = None
        self.goal_pos = None
        self.agent_pos = None
        self.current_path = []
        
        # New persistent metrics
        self.steps_taken = 0
        self.total_search_time = 0 
        
        self.setup_ui()
        self.initialize_grid()

    def setup_ui(self):
        self.control_panel = ttk.Frame(self.root, padding=10)
        self.control_panel.pack(side="right", fill="y")

        tk.Label(self.control_panel, text="Grid Size (Rows x Cols):").pack()
        size_frame = ttk.Frame(self.control_panel)
        size_frame.pack()
        self.row_entry = ttk.Entry(size_frame, width=5)
        self.row_entry.insert(0, "20")
        self.row_entry.pack(side="left")
        self.col_entry = ttk.Entry(size_frame, width=5)
        self.col_entry.insert(0, "20")
        self.col_entry.pack(side="left")
        ttk.Button(self.control_panel, text="Update Grid", command=self.update_grid_dims).pack(pady=5)

        tk.Label(self.control_panel, text="Algorithm:").pack(pady=(10,0))
        self.algo_var = tk.StringVar(value="A*")
        ttk.Combobox(self.control_panel, textvariable=self.algo_var, values=["A*", "Greedy BFS"], state="readonly").pack()

        tk.Label(self.control_panel, text="Heuristic:").pack(pady=(10,0))
        self.heur_var = tk.StringVar(value="Manhattan")
        ttk.Combobox(self.control_panel, textvariable=self.heur_var, values=["Manhattan", "Euclidean"], state="readonly").pack()

        self.dynamic_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self.control_panel, text="Dynamic Obstacles", variable=self.dynamic_var).pack(pady=10)

        # --- Metrics Dashboard ---
        self.metrics_frame = ttk.LabelFrame(self.control_panel, text="Metrics", padding=5)
        self.metrics_frame.pack(fill="x", pady=10)
        self.lbl_visited = tk.Label(self.metrics_frame, text="Nodes Visited: 0")
        self.lbl_visited.pack(anchor="w")
        self.lbl_remain = tk.Label(self.metrics_frame, text="Remaining Cost: 0")
        self.lbl_remain.pack(anchor="w")
        self.lbl_accum = tk.Label(self.metrics_frame, text="Accumulated Cost: 0")
        self.lbl_accum.pack(anchor="w")
        self.lbl_time = tk.Label(self.metrics_frame, text="Execution: 0ms")
        self.lbl_time.pack(anchor="w")

        ttk.Button(self.control_panel, text="Start Agent", command=self.start_navigation).pack(fill="x", pady=2)
        ttk.Button(self.control_panel, text="Random Maze (30%)", command=lambda: self.random_maze(0.3)).pack(fill="x", pady=2)
        ttk.Button(self.control_panel, text="Clear Grid", command=self.initialize_grid).pack(fill="x", pady=2)

        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=1, highlightbackground="black")
        self.canvas.pack(side="left", padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.handle_click)
    
    def initialize_grid(self):
        self.canvas.delete("all")
        self.rows = int(self.row_entry.get())
        self.cols = int(self.col_entry.get())
        self.canvas.config(width=self.cols*CELL_SIZE, height=self.rows*CELL_SIZE)
        self.grid_data = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.cells = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.start_pos = self.goal_pos = self.agent_pos = None
        self.steps_taken = 0
        self.total_search_time = 0
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["empty"], outline="#ddd")
                self.cells[r][c] = rect

if __name__ == "__main__":
    root = tk.Tk()
    app = PathfindingApp(root)
    root.mainloop()