import tkinter as tk
from tkinter import messagebox
import time
import random


class Connect4Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        self.rows = 6
        self.columns = 7
        self.cell_size = 100
        self.margin = 10
        self.grid = []
        self.column_highlight = -1
        self.is_button_disabled = False
        self.playing_against_bot = False
        self.current_player = 1

        self.create_menu()

    def create_menu(self):
        """Main menu."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Welcome to Connect 4!", font=("Arial", 24)).pack(pady=20)
        tk.Button(self.root, text="2 Player Game", font=("Arial", 18), command=self.start_2_player_game).pack(pady=10)
        tk.Button(self.root, text="Play Against Bot", font=("Arial", 18), command=self.start_bot_game).pack(pady=10)
        tk.Button(self.root, text="Exit", font=("Arial", 18), command=self.root.destroy).pack(pady=10)

    def start_2_player_game(self):
        """Start a 2-player game."""
        self.playing_against_bot = False
        self.initialize_game()

    def start_bot_game(self):
        """Start a game against the bot."""
        self.playing_against_bot = True
        self.initialize_game()

    def initialize_game(self):
        """Initialize the game grid and UI."""
        self.grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        self.current_player = 1
        self.column_highlight = -1
        self.is_button_disabled = False

        for widget in self.root.winfo_children():
            widget.destroy()

        self.canvas = tk.Canvas(self.root, bg="blue")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(fill=tk.X)

        self.buttons = []
        for col in range(self.columns):
            button = tk.Button(self.buttons_frame, text="↓", font=("Arial", 14), command=lambda c=col: self.select_column(c))
            button.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
            self.buttons.append(button)

        for i in range(self.columns):
            self.buttons_frame.columnconfigure(i, weight=1)

        self.canvas.bind("<Configure>", self.redraw)

    def redraw(self, event=None):
        """Redraw the grid to match the new canvas size."""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        self.cell_size = min(width // self.columns, height // self.rows)
        self.margin = self.cell_size // 10

        for row in range(self.rows):
            for col in range(self.columns):
                x1 = col * self.cell_size + self.margin
                y1 = row * self.cell_size + self.margin
                x2 = x1 + self.cell_size - 2 * self.margin
                y2 = y1 + self.cell_size - 2 * self.margin

                color = "white"
                if self.grid[row][col] == 1:
                    color = "red"
                elif self.grid[row][col] == 2:
                    color = "yellow"

                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black")

        if self.column_highlight != -1:
            x1 = self.column_highlight * self.cell_size
            x2 = x1 + self.cell_size
            self.canvas.create_rectangle(x1, 0, x2, self.rows * self.cell_size, outline="white", width=3)

    def select_column(self, col):
        """Select a column."""
        if self.is_button_disabled:
            return

        self.column_highlight = col
        self.redraw()
        self.disable_buttons()
        self.root.after(200, lambda: self.drop_disk(col))

    def drop_disk(self, col):
        """Animate the disk dropping into the selected column."""
        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][col] == 0:
                for anim_row in range(row + 1):
                    self.grid[anim_row][col] = self.current_player
                    self.redraw()
                    self.root.update()
                    time.sleep(0.05)
                    self.grid[anim_row][col] = 0
                self.grid[row][col] = self.current_player
                break
        else:
            self.enable_buttons()
            return  # Column is full

        self.redraw()

        if self.check_winner(row, col):
            self.animate_win()
        else:
            self.current_player = 3 - self.current_player
            if self.playing_against_bot and self.current_player == 2:
                self.bot_move()
            else:
                self.enable_buttons()

    def bot_move(self):
        """Bot makes a move."""
        self.disable_buttons()
        time.sleep(0.3) 

        valid_columns = [col for col in range(self.columns) if self.grid[0][col] == 0]
        for col in valid_columns:
            if self.simulate_move(col, 2):  # Bot tries to win
                self.drop_disk(col)
                return
        for col in valid_columns:
            if self.simulate_move(col, 1):  # Bot blocks player's winning move
                self.drop_disk(col)
                return

        # Prioritize center column
        if self.grid[0][self.columns // 2] == 0:
            self.drop_disk(self.columns // 2)
            return

        # Random move
        self.drop_disk(random.choice(valid_columns))

    def simulate_move(self, col, player):
        """Simulate a move for a player and check for a win."""
        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][col] == 0:
                self.grid[row][col] = player
                win = self.check_winner(row, col)
                self.grid[row][col] = 0
                return win
        return False

    def check_winner(self, row, col):
        """Check if the current player has won."""
        self.win_coords = []

        def count_disks(direction_row, direction_col):
            r, c = row, col
            count = 0
            coords = []
            while 0 <= r < self.rows and 0 <= c < self.columns and self.grid[r][c] == self.current_player:
                coords.append((r, c))
                count += 1
                r += direction_row
                c += direction_col
            return count, coords

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count1, coords1 = count_disks(dr, dc)
            count2, coords2 = count_disks(-dr, -dc)
            total_count = count1 + count2 - 1
            if total_count >= 4:
                self.win_coords = coords1 + coords2[1:]
                return True
        return False

    def animate_win(self):
        """Highlight the winning disks with an animation."""
        for _ in range(3):
            for row, col in self.win_coords:
                x1 = col * self.cell_size + self.margin
                y1 = row * self.cell_size + self.margin
                x2 = x1 + self.cell_size - 2 * self.margin
                y2 = y1 + self.cell_size - 2 * self.margin
                self.canvas.create_oval(x1, y1, x2, y2, fill="green", outline="black")
            self.root.update()
            time.sleep(0.3)
            self.redraw()
            self.root.update()
            time.sleep(0.3)

        self.show_winner()

    def disable_buttons(self):
        """Disable column buttons to prevent spamming."""
        self.is_button_disabled = True
        for button in self.buttons:
            button.config(state=tk.DISABLED)

    def enable_buttons(self):
        """Enable column buttons."""
        self.is_button_disabled = False
        for button in self.buttons:
            button.config(state=tk.NORMAL)

    def show_winner(self):
        """Display the winner."""
        winner = f"Player {self.current_player}"
        messagebox.showinfo("Connect 4", f"{winner} wins!")
        self.play_again_menu()

    def play_again_menu(self):
        """Menu to replay or switch modes."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Game Over!", font=("Arial", 24)).pack(pady=20)
        tk.Button(self.root, text="Play Again (Same Mode)", font=("Arial", 18), command=self.initialize_game).pack(pady=10)
        tk.Button(self.root, text="Switch Game Mode", font=("Arial", 18), command=self.create_menu).pack(pady=10)
        tk.Button(self.root, text="Exit", font=("Arial", 18), command=self.root.destroy).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    Connect4Game(root)
    root.mainloop()
