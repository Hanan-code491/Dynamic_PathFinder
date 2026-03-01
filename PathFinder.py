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

    def handle_click(self, event):
        col, row = event.x // CELL_SIZE, event.y // CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if not self.start_pos:
                self.start_pos = (row, col)
                self.canvas.itemconfig(self.cells[row][col], fill=COLORS["start"])
            elif not self.goal_pos and (row, col) != self.start_pos:
                self.goal_pos = (row, col)
                self.canvas.itemconfig(self.cells[row][col], fill=COLORS["goal"])
            elif (row, col) != self.start_pos and (row, col) != self.goal_pos:
                self.grid_data[row][col] = 1
                self.canvas.itemconfig(self.cells[row][col], fill=COLORS["wall"])

    def get_h(self, p1, p2):
        if not p1 or not p2: return 0
        r1, c1 = p1
        r2, c2 = p2
        if self.heur_var.get() == "Manhattan":
            return abs(r1 - r2) + abs(c1 - c2)
        return math.sqrt((r1 - r2)**2 + (c1 - c2)**2)
    
    def search(self, start_node):
        if not self.goal_pos: return None
        start_t = time.perf_counter()
        pq = []
        heappush(pq, (0, 0, start_node, []))
        visited = set()
        nodes_expanded = 0

        while pq:
            f, g, curr, path = heappop(pq)
            if curr in visited: continue
            visited.add(curr)
            nodes_expanded += 1
            
            if curr != start_node and curr != self.goal_pos:
                self.canvas.itemconfig(self.cells[curr[0]][curr[1]], fill=COLORS["visited"])

            if curr == self.goal_pos:
                exec_time = (time.perf_counter() - start_t) * 1000
                self.total_search_time += exec_time # Accumulate calculation time
                self.update_metrics(nodes_expanded, len(path), exec_time)
                return path

            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = curr[0]+dr, curr[1]+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid_data[nr][nc] == 0:
                    new_g = g + 1
                    h = self.get_h((nr, nc), self.goal_pos)
                    new_f = h if self.algo_var.get() == "Greedy BFS" else new_g + h
                    heappush(pq, (new_f, new_g, (nr, nc), path + [(nr, nc)]))
                    if (nr, nc) != self.goal_pos and (nr, nc) not in visited:
                        self.canvas.itemconfig(self.cells[nr][nc], fill=COLORS["frontier"])
        return None

    def start_navigation(self):
        if not self.start_pos or not self.goal_pos:
            messagebox.showwarning("Error", "Set Start and Goal first!")
            return
        self.agent_pos = self.start_pos
        self.steps_taken = 0
        self.total_search_time = 0
        self.move_agent()

    def move_agent(self):
        # 1. Clear visuals
        for r in range(self.rows):
            for c in range(self.cols):
                color = self.canvas.itemcget(self.cells[r][c], "fill")
                if color in [COLORS["path"], COLORS["frontier"], COLORS["visited"]]:
                    self.canvas.itemconfig(self.cells[r][c], fill=COLORS["empty"])

if __name__ == "__main__":
    root = tk.Tk()
    app = PathfindingApp(root)
    root.mainloop()