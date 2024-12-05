import tkinter as tk
import random
import time

# Maze configuration defaults
DEFAULT_CELL_SIZE = 25

# Maze sizes for easy, medium, and hard levels
MAZE_SIZES = {
    "easy": (21, 21),
    "medium": (31, 31),
    "hard": (45, 45)
}

# Key Bindings
KEY_BINDINGS = """
W - Move Up
A - Move Left
S - Move Down
D - Move Right
Arrow Keys - Move
"""

def create_solvable_maze(rows, cols):
    """Generate a solvable maze using Depth-First Search (DFS) with walls intact."""
    # Initialize the maze
    maze = [[1] * cols for _ in range(rows)]

    # Mark the border as walls
    for r in range(rows):
        maze[r][0] = maze[r][cols - 1] = 1
    for c in range(cols):
        maze[0][c] = maze[rows - 1][c] = 1

    visited = [[False] * cols for _ in range(rows)]

    def carve_passages(cx, cy):
        """Recursive backtracking for maze generation."""
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]  # Skip cells for thicker walls
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 1 <= nx < rows - 1 and 1 <= ny < cols - 1 and not visited[nx][ny]:
                # Carve the wall between current cell and next cell
                maze[cx + dx // 2][cy + dy // 2] = 0
                # Carve the next cell
                maze[nx][ny] = 0
                visited[nx][ny] = True
                carve_passages(nx, ny)

    # Start maze generation at the entrance
    maze[1][1] = 0
    visited[1][1] = True
    carve_passages(1, 1)

    # Randomly place the exit, ensuring it's not a wall and is reachable
    exit_pos = None
    reachable = False
    while not reachable:
        # Randomly place exit in an open space (non-wall)
        exit_row = random.randint(2, rows - 2)
        exit_col = random.randint(2, cols - 2)
        if maze[exit_row][exit_col] == 0:  # Ensure it's not a wall
            exit_pos = (exit_row, exit_col)
            # Perform a check if the exit is reachable from the start
            visited_bfs = [[False] * cols for _ in range(rows)]
            queue = [(1, 1)]  # Start BFS from the player spawn
            visited_bfs[1][1] = True
            while queue:
                r, c = queue.pop(0)
                if (r, c) == exit_pos:
                    reachable = True
                    break
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and not visited_bfs[nr][nc] and maze[nr][nc] == 0:
                        visited_bfs[nr][nc] = True
                        queue.append((nr, nc))
            # If the exit isn't reachable, continue finding a new location
            if not reachable:
                exit_pos = None

    return maze, exit_pos

class MazeGame:
    def __init__(self, root, rows, cols, timer_duration, exit_pos):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = DEFAULT_CELL_SIZE  # Fixed cell size
        self.timer_duration = timer_duration
        self.time_left = self.timer_duration
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=False)  # Fixed canvas size

        self.maze = create_solvable_maze(self.rows, self.cols)[0]
        self.exit_pos = exit_pos
        self.player_pos = [1, 1]  # Starting position of the player
        self.game_over = False

        # Load the player's character image from the current folder
        try:
            self.player_image = tk.PhotoImage(file="player.gif")  # Ensure this is a .gif file
        except Exception as e:
            print(f"Error loading image: {e}")
            self.player_image = None
        self.player_sprite = None  # store the player sprite here

        self.draw_maze()
        self.draw_player()

        self.root.bind("<KeyPress>", self.handle_keypress)

        self.timer_label = tk.Label(root, text=f"Time Left: {self.time_left}s", font=("Helvetica", 16), fg="black", bg="yellow")
        self.timer_label.pack(pady=5, side="top", fill="x")

        self.start_timer()

    def draw_maze(self):
        """Draw the maze on the canvas."""
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                color = "black" if self.maze[r][c] == 1 else "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
        # Mark the exit
        x1, y1 = self.exit_pos[1] * self.cell_size, self.exit_pos[0] * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="gray")

    def draw_player(self):
        """Draw the player on the canvas using the PNG image."""
        x1, y1 = self.player_pos[1] * self.cell_size, self.player_pos[0] * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        # Create the player sprite on the canvas
        if self.player_image:
            self.player_sprite = self.canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=self.player_image)
        else:
            self.player_sprite = self.canvas.create_rectangle(x1, y1, x2, y2, fill="red")

    def handle_keypress(self, event):
        """Handle WASD or arrow keypress to move the player."""
        if self.game_over:
            return

        moves = {"w": (-1, 0), "a": (0, -1), "s": (1, 0), "d": (0, 1),
                 "Up": (-1, 0), "Left": (0, -1), "Down": (1, 0), "Right": (0, 1)}
        if event.keysym in moves:
            dr, dc = moves[event.keysym]
            new_r = self.player_pos[0] + dr
            new_c = self.player_pos[1] + dc

            # Check if the move is valid
            if 0 <= new_r < self.rows and 0 <= new_c < self.cols and self.maze[new_r][new_c] == 0:
                self.player_pos = [new_r, new_c]
                self.update_player_position()

            # Check for win condition
            if self.player_pos == list(self.exit_pos):
                self.show_win_message()

    def update_player_position(self):
        """Update the player's position on the canvas."""
        x1, y1 = self.player_pos[1] * self.cell_size, self.player_pos[0] * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        # Update the position of the player's image
        self.canvas.coords(self.player_sprite, (x1 + x2) / 2, (y1 + y2) / 2)

    def start_timer(self):
        """Start the countdown timer."""
        self.update_timer()
        self.timer_id = self.root.after(1000, self.countdown_timer)

    def countdown_timer(self):
        """Update the timer each second."""
        if self.time_left > 0:
            self.time_left -= 1
            self.update_timer()
            self.root.after(1000, self.countdown_timer)
        else:
            self.show_game_over()

    def update_timer(self):
        """Update the timer display on the UI."""
        self.timer_label.config(text=f"Time Left: {self.time_left}s")

    def show_win_message(self):
        """Show the win message."""
        self.game_over = True
        self.canvas.create_text(self.cols * self.cell_size / 2, self.rows * self.cell_size / 2, text="You Win!", font=("Helvetica", 24), fill="green")
        self.show_win_popup()

    def show_game_over(self):
        """Display a game over message."""
        self.game_over = True
        self.canvas.create_text(self.cols * self.cell_size / 2, self.rows * self.cell_size / 2, text="Game Over!", font=("Helvetica", 24), fill="red")

    def show_win_popup(self):
        """Display a popup with win animation and replay options."""
        win_popup = tk.Toplevel(self.root)
        win_popup.title("You Win!")
        win_popup.geometry("300x200")
        
        # Show an animation or message indicating winning
        message_label = tk.Label(win_popup, text="You Won!", font=("Helvetica", 20), fg="green")
        message_label.pack(pady=50)

        # Buttons for replaying or changing difficulty
        replay_button = tk.Button(win_popup, text="Replay", font=("Helvetica", 14),
                                  command=lambda: self.restart_game())
        replay_button.pack(pady=10)

        change_difficulty_button = tk.Button(win_popup, text="Change Difficulty", font=("Helvetica", 14),
                                             command=lambda: self.change_difficulty(win_popup))
        change_difficulty_button.pack(pady=10)

    def restart_game(self):
        """Restart the game with the same difficulty."""
        self.root.destroy()  # Close the current window
        show_menu() 

    def change_difficulty(self, win_popup):
        """Allow the player to change difficulty."""
        win_popup.destroy()  # Close the win popup
        show_menu() 

def show_menu():
    """Display the main menu with difficulty selection."""
    menu_window = tk.Tk()
    menu_window.title("Maze Game")

    title_label = tk.Label(menu_window, text="Maze Game", font=("Helvetica", 24))
    title_label.pack(pady=20)

    instructions_label = tk.Label(menu_window, text=KEY_BINDINGS, font=("Helvetica", 12))
    instructions_label.pack(padx=10)

    # Button to start the game
    start_button = tk.Button(menu_window, text="Start Game", font=("Helvetica", 14),
                             command=lambda: show_difficulty_menu(menu_window))
    start_button.pack(pady=20)

    menu_window.mainloop()

def show_difficulty_menu(menu_window):
    """Show the difficulty menu to choose difficulty."""
    for widget in menu_window.winfo_children():
        widget.destroy()

    label = tk.Label(menu_window, text="Select Difficulty", font=("Helvetica", 20))
    label.pack(pady=10)

    easy_button = tk.Button(menu_window, text="Easy", width=20, command=lambda: start_game(menu_window, "easy", 90))
    easy_button.pack(pady=10)

    medium_button = tk.Button(menu_window, text="Medium", width=20, command=lambda: start_game(menu_window, "medium", 120))
    medium_button.pack(pady=10)

    hard_button = tk.Button(menu_window, text="Hard", width=20, command=lambda: start_game(menu_window, "hard", 150))
    hard_button.pack(pady=10)

def start_game(menu_window, difficulty, timer_duration):
    """Start the game with selected difficulty."""
    menu_window.destroy()  # Close the menu window

    # Load maze configuration
    rows, cols = MAZE_SIZES[difficulty]
    maze, exit_pos = create_solvable_maze(rows, cols)  # Generate the maze and get exit position

    root = tk.Tk()
    game = MazeGame(root, rows, cols, timer_duration, exit_pos)
    root.mainloop()

show_menu()
