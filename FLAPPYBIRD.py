import tkinter as tk
import random

class FlappyBirdGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird")

        # Game settings
        self.window_width = 400
        self.window_height = 600
        self.pipe_width = 60
        self.pipe_gap = 150
        self.bird_size = 20

        # Initialize variables
        self.bird_y = self.window_height // 2
        self.bird_velocity = 0
        self.gravity = 1
        self.flap_strength = -12
        self.score = 0
        self.game_running = False
        self.pipe_spacing = 200
        self.pipes = []

        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height, bg="skyblue")
        self.canvas.pack()

        # Bird
        self.bird = self.canvas.create_oval(
            50, self.bird_y, 50 + self.bird_size, self.bird_y + self.bird_size, fill="yellow"
        )

        # Start screen
        self.start_screen()

        # Key bindings
        self.root.bind("<space>", self.flap)

    def start_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            self.window_width // 2,
            self.window_height // 2 - 20,
            text="Flappy Bird",
            font=("Arial", 24, "bold"),
            fill="black"
        )
        self.canvas.create_text(
            self.window_width // 2,
            self.window_height // 2 + 20,
            text="Press SPACE to Flap",
            font=("Arial", 16),
            fill="black"
        )
        self.canvas.create_text(
            self.window_width // 2,
            self.window_height // 2 + 50,
            text="Press ENTER to Start",
            font=("Arial", 16),
            fill="black"
        )
        self.root.bind("<Return>", self.start_game)

    def start_game(self, event=None):
        self.root.unbind("<Return>")
        self.canvas.delete("all")
        self.bird_y = self.window_height // 2
        self.bird_velocity = 0
        self.score = 0
        self.pipes = []
        self.game_running = True

        # Reset bird position
        self.bird = self.canvas.create_oval(
            50, self.bird_y, 50 + self.bird_size, self.bird_y + self.bird_size, fill="yellow"
        )

        self.generate_initial_pipes()
        self.update_game()

    def generate_initial_pipes(self):
        for i in range(3):
            x = self.window_width + i * self.pipe_spacing
            self.add_pipe(x)

    def add_pipe(self, x):
        top_pipe_end = random.randint(100, self.window_height - self.pipe_gap - 100)
        bottom_pipe_start = top_pipe_end + self.pipe_gap

        top_pipe = self.canvas.create_rectangle(
            x, 0, x + self.pipe_width, top_pipe_end, fill="green"
        )
        bottom_pipe = self.canvas.create_rectangle(
            x, bottom_pipe_start, x + self.pipe_width, self.window_height, fill="green"
        )
        self.pipes.append((top_pipe, bottom_pipe))

    def flap(self, event=None):
        if self.game_running:
            self.bird_velocity = self.flap_strength

    def update_game(self):
        if not self.game_running:
            return

        # Update bird position
        self.bird_velocity += self.gravity
        self.bird_y += self.bird_velocity
        self.canvas.move(self.bird, 0, self.bird_velocity)

        # Check for collisions
        if self.bird_y <= 0 or self.bird_y + self.bird_size >= self.window_height:
            self.end_game()
            return

        # Move pipes and check collisions
        new_pipes = []
        for top_pipe, bottom_pipe in self.pipes:
            self.canvas.move(top_pipe, -5, 0)
            self.canvas.move(bottom_pipe, -5, 0)

            top_coords = self.canvas.coords(top_pipe)
            bottom_coords = self.canvas.coords(bottom_pipe)

            if self.check_collision(top_coords) or self.check_collision(bottom_coords):
                self.end_game()
                return

            # If the pipe is still on screen, keep it
            if top_coords[2] > 0:
                new_pipes.append((top_pipe, bottom_pipe))
            else:
                self.score += 1

        self.pipes = new_pipes

        # Add new pipes when the last pipe is far enough
        if len(self.pipes) > 0 and self.canvas.coords(self.pipes[-1][0])[2] < self.window_width - self.pipe_spacing:
            self.add_pipe(self.window_width)

        # Update score display
        self.canvas.delete("score")
        self.canvas.create_text(
            50, 30, text=f"Score: {self.score}", font=("Arial", 16), fill="black", tag="score"
        )

        self.root.after(20, self.update_game)

    def check_collision(self, pipe_coords):
        if not pipe_coords or len(pipe_coords) != 4:
            return False
        bird_coords = self.canvas.coords(self.bird)
        return not (
            bird_coords[2] < pipe_coords[0] or
            bird_coords[0] > pipe_coords[2] or
            bird_coords[3] < pipe_coords[1] or
            bird_coords[1] > pipe_coords[3]
        )

    def end_game(self):
        self.game_running = False
        self.canvas.delete("all")
        self.canvas.create_text(
            self.window_width // 2,
            self.window_height // 2 - 20,
            text="You Died",
            font=("Arial", 24, "bold"),
            fill="red"
        )
        self.canvas.create_text(
            self.window_width // 2,
            self.window_height // 2 + 20,
            text=f"Score: {self.score}",
            font=("Arial", 16),
            fill="black"
        )
        self.canvas.create_text(
            self.window_width // 2,
            self.window_height // 2 + 50,
            text="Press ENTER to Restart",
            font=("Arial", 16),
            fill="black"
        )
        self.root.bind("<Return>", self.start_game)

if __name__ == "__main__":
    root = tk.Tk()
    game = FlappyBirdGame(root)
    root.mainloop()
