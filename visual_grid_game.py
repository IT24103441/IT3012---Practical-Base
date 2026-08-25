import random
import tkinter as tk
 
 
class VisualGridHuntGame:
    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]
 
        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}
 
        available_positions = {
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) != (0, 0) and (x, y) not in self.walls
        }
 
        food_count = min(num_food, len(available_positions))
        self.food_positions = set(random.sample(list(available_positions), food_count))
        available_positions -= self.food_positions
 
        trap_count = min(5, len(available_positions))
        self.toxic_traps = set(random.sample(list(available_positions), trap_count))
        available_positions -= self.toxic_traps
 
        opponent_count = min(num_opponents, len(available_positions))
        opponent_positions = random.sample(list(available_positions), opponent_count)
        self.opponents = [list(pos) for pos in opponent_positions]
 
        self.score = 0
        self.steps = 0
        self.collision = False
 
    def get_percept(self):
        x, y = self.agent_pos
        ahead = (x + 1, y)
 
        wall_ahead = (
            ahead[0] >= self.width
            or ahead in self.walls
        )
 
        return {
            "food_here": (x, y) in self.food_positions,
            "toxin_here": (x, y) in self.toxic_traps,
            "wall_ahead": wall_ahead,
 
            'agent_pos': tuple(self.agent_pos),
            'grid_size': (self.width, self.height),
            'walls': list(self.walls),
            'all_food': list(self.food_positions)
        }
 
    def execute_action(self, action):
        self.steps += 1
        new_pos = list(self.agent_pos)
 
        # Map movement strings or actions
        if action == "Up":
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == "Down":
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == "Left":
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == "Right":
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)
        elif action == "Stay":
            pass
        else:
            return
 
        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos
 
        tuple_pos = tuple(self.agent_pos)
 
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20
 
        if tuple_pos in self.toxic_traps:
            self.score -= 15
 
        for op in self.opponents:
            move = random.choice(["Up", "Down", "Left", "Right", "Stay"])
 
            if move == "Up" and op[1] < self.height - 1:
                op[1] += 1
            elif move == "Down" and op[1] > 0:
                op[1] -= 1
            elif move == "Left" and op[0] > 0:
                op[0] -= 1
            elif move == "Right" and op[0] < self.width - 1:
                op[0] += 1
 
            if tuple(op) in self.walls:
                if move == "Up":
                    op[1] -= 1
                elif move == "Down":
                    op[1] += 1
                elif move == "Left":
                    op[0] += 1
                elif move == "Right":
                    op[0] -= 1
 
            if op == self.agent_pos:
                self.score -= 50
                self.collision = True
 
    def is_done(self):
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision
 
 
# Keep the GUI and main block intact for execution
class GridGameGUI:
    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")
 
        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )
 
        # Later you will replace this with your SearchAgent() from agent.py
        from agent import SearchAgent
        self.agent = SearchAgent()
 
        max_canvas_dim = 600
        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )
 
        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size
 
        self.canvas = tk.Canvas(
            root,
            width=canvas_w,
            height=canvas_h,
            bg="white"
        )
        self.canvas.pack()
 
        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )
        self.label.pack(pady=10)
 
        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )
        self.btn.pack(pady=5)
 
        self.draw_grid()
 
    def draw_grid(self):
        self.canvas.delete("all")
 
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
 
                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
 
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1"
                )
 
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold")
                    )
 
        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
 
            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )
 
        for tx, ty in self.env.toxic_traps:
            offset = self.cell_size * 0.25
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset
 
            self.canvas.create_polygon(
                x1 + self.cell_size * 0.25,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                x1,
                y1 + self.cell_size * 0.5,
                fill="purple",
                outline="black"
            )
 
        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
 
            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )
 
        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
 
        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )
 
    def run_loop(self):
        self.btn.config(state="disabled")
 
        def step():
            if self.env.is_done():
                end_text = (
                    f"Collision! Game Over! Final Score: {self.env.score}"
                    if self.env.collision
                    else f"Finished! Final Score: {self.env.score}"
                )
                self.label.config(text=end_text)
                self.btn.config(state="normal")
                return
 
            percept = self.env.get_percept()
            action = self.agent.sense_and_act(percept)
            self.env.execute_action(action)
 
            self.draw_grid()
 
            self.label.config(
                text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}"
            )
 
            self.root.after(250, step)
 
        step()
 
 
if __name__ == "__main__":
    root = tk.Tk()
 
    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )
 
    root.mainloop()
