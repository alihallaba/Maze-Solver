import tkinter as tk
import random
import heapq
from tkinter import messagebox

CELL_SIZE = 30
TREAT_COUNT = 5
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class MazeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Maze Game")
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()

        # Button frame to reduce space between buttons
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        # Play Button with warm colors
        self.start_button = tk.Button(button_frame, text="Play", command=self.play_game, font=("Arial", 12, "bold"), bg="#FFB74D", fg="white", padx=20, pady=10)
        self.start_button.grid(row=0, column=0, padx=5)

        # Watch Agent Button with warm colors
        self.agent_button = tk.Button(button_frame, text="Watch Agent", command=self.agent_solve, font=("Arial", 12, "bold"), bg="#FF8A65", fg="white", padx=20, pady=10)
        self.agent_button.grid(row=0, column=1, padx=5)

        # Level Selection Menu with warm colors
        self.level_var = tk.StringVar(value='Choose')
        self.level_menu = tk.OptionMenu(button_frame, self.level_var, 'beginner', 'mid', 'hard')
        self.level_menu.config(font=("Arial", 12), bg="#FFB74D", width=10)
        self.level_menu.grid(row=1, column=0, padx=5, pady=5)

        # Score and treat counter label with styling
        self.total_score = 0
        self.score = 0
        self.treat_counter = 0
        self.steps = 1  # Start steps from 1
        self.agent_score = 0
        self.agent_treat_counter = 0
        self.score_label = tk.Label(master, text=f"Total Score: {self.total_score} | Treats Collected: {self.treat_counter} | Steps: {self.steps}", font=("Arial", 12), fg="#000000")
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.maze = []
        self.player_pos = (0, 0)
        self.steps_taken = []
        self.optimal_path = []
        self.optimal_treats = 0

        # Bind arrow keys for movement
        self.master.bind("<KeyPress>", self.on_key_press)

    def generate_maze(self, level):
        if level == 'beginner':
            size = 5
        elif level == 'mid':
            size = 10
        else:
            size = 15

        maze = [[1] * size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                if random.random() > 0.3:
                    maze[i][j] = 0

        maze[0][0] = 0
        maze[size - 1][size - 1] = 0

        for _ in range(TREAT_COUNT):
            while True:
                x, y = random.randint(0, size - 1), random.randint(0, size - 1)
                if maze[x][y] == 0 and (x, y) != (0, 0) and (x, y) != (size - 1, size - 1):
                    maze[x][y] = 'T'
                    break

        if not self.is_solvable(maze):
            return self.generate_maze(level)

        return maze

    def is_solvable(self, maze):
        stack = [(0, 0)]
        visited = set()
        while stack:
            x, y = stack.pop()
            if (x, y) == (len(maze) - 1, len(maze) - 1):
                return True
            visited.add((x, y))
            for direction in DIRECTIONS:
                nx, ny = x + direction[0], y + direction[1]
                if 0 <= nx < len(maze) and 0 <= ny < len(maze) and maze[nx][ny] != 1 and (nx, ny) not in visited:
                    stack.append((nx, ny))
        return False

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self):
        start = (0, 0)
        goal = (len(self.maze) - 1, len(self.maze) - 1)
        open_set = []
        heapq.heappush(open_set, (0, start))  # Use heapq to manage the open set
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        treat_count = {start: 0}

        while open_set:
            current = heapq.heappop(open_set)[1]  # Pop the node with the lowest f_score

            if current == goal:
                self.optimal_treats = treat_count[current]
                return self.reconstruct_path(came_from, current)

            for direction in DIRECTIONS:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if 0 <= neighbor[0] < len(self.maze) and 0 <= neighbor[1] < len(self.maze) and self.maze[neighbor[0]][neighbor[1]] != 1:
                    tentative_g_score = g_score[current] + 1
                    treats_collected = treat_count[current] + (1 if self.maze[neighbor[0]][neighbor[1]] == 'T' else 0)

                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                        treat_count[neighbor] = treats_collected
                        if neighbor not in [i[1] for i in open_set]:
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))  # Push to heapq

        return []

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def draw_maze(self):
        self.canvas.delete("all")
        self.canvas.config(width=len(self.maze) * CELL_SIZE, height=len(self.maze) * CELL_SIZE)
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                color = "black" if cell == 1 else "white"
                if cell == 'T':
                    color = "pink"
                if (i, j) == (0, 0):
                    color = "green"
                if (i, j) == (len(self.maze) - 1, len(self.maze) - 1):
                    color = "orange"  # Highlight the end point
                if (i, j) in self.steps_taken:
                    color = "lightblue"
                self.canvas.create_rectangle(j * CELL_SIZE, i * CELL_SIZE,
                                              (j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE,
                                              fill=color)

    def play_game(self):
        self.score = 0
        self.treat_counter = 0
        self.steps = 1  # Start steps from 1
        self.steps_taken = []
        self.optimal_treats = 0
        self.optimal_path = []
        self.score_label.config(text=f"Total Score: {self.total_score} | Treats Collected: {self.treat_counter} | Steps: {self.steps}")
        level = self.level_var.get()
        self.maze = self.generate_maze(level)
        self.optimal_path = self.a_star()
        self.draw_maze()
        self.player_pos = (0, 0)

    def user_move(self):
        if self.player_pos == (len(self.maze) - 1, len(self.maze) - 1):
            optimal_steps = len(self.optimal_path) - 1
            message = f"You won! Final score: {self.score} | Steps taken: {self.steps} | Optimal steps: {optimal_steps} | Optimal treats: {self.optimal_treats}"
            if self.steps == optimal_steps:
                message += "\nCongratulations! You took the optimal path!"
            else:
                message += "\nYou didn't get the optimal path better luck next time"

            self.total_score += self.score
            play_again = messagebox.askyesno("Game Over", message + "\n\nDo you want to play again?")
            if play_again:
                self.level_var.set('beginner')
                self.play_game()
            else:
                self.reset_game()

            return

        x, y = self.player_pos
        if self.maze[x][y] == 'T':
            self.treat_counter += 1
            self.score += 1
            self.maze[x][y] = 0

        self.steps += 1
        self.steps_taken.append(self.player_pos)
        self.score_label.config(text=f"Total Score: {self.total_score} | Treats Collected: {self.treat_counter} | Steps: {self.steps}")
        self.draw_maze()

    def reset_game(self):
        self.total_score = 0
        self.score = 0
        self.treat_counter = 0
        self.steps = 1  # Reset steps to 1
        self.steps_taken = []
        self.score_label.config(text=f"Total Score: {self.total_score} | Treats Collected: {self.treat_counter} | Steps: {self.steps}")
        self.time_left = 0  # Reset the timer

    def on_key_press(self, event):
        if self.player_pos == (len(self.maze) - 1, len(self.maze) - 1):
            return

        x, y = self.player_pos
        if event.keysym == 'Up':
            new_x, new_y = x - 1, y
        elif event.keysym == 'Left':
            new_x, new_y = x, y - 1
        elif event.keysym == 'Down':
            new_x, new_y = x + 1, y
        elif event.keysym == 'Right':
            new_x, new_y = x, y + 1
        else:
            return

        if 0 <= new_x < len(self.maze) and 0 <= new_y < len(self.maze) and self.maze[new_x][new_y] != 1:
            self.player_pos = (new_x, new_y)
            self.user_move()
        else:
            messagebox.showinfo("Hit Wall", "You hit a wall! Try a different direction.")

    def agent_solve(self):
        self.player_pos = (0, 0)
        self.steps_taken = []

        level = self.level_var.get()
        self.maze = self.generate_maze(level)
        self.draw_maze()

        path = self.a_star()
        if path:
            self.animate_agent(path)
        else:
            messagebox.showinfo("No Path", "No path found for the agent.")

    def animate_agent(self, path):
        self.agent_treat_counter = 0
        for (x, y) in path:
            self.canvas.create_rectangle(y * CELL_SIZE, x * CELL_SIZE,
                                          (y + 1) * CELL_SIZE, (x + 1) * CELL_SIZE,
                                          fill="blue")
            if self.maze[x][y] == 'T':
                self.agent_treat_counter += 1
            self.master.update()
            self.master.after(500)
        self.agent_score = self.agent_treat_counter
        messagebox.showinfo("Agent Finished", f"Agent collected {self.agent_treat_counter} treats. Final score: {self.agent_score}")



if __name__ == "__main__":
    root = tk.Tk()
    game = MazeGame(root)
    root.mainloop()
