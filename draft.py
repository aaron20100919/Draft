import tkinter as tk
from tkinter import colorchooser, simpledialog
import threading
import time

draw_frequency = 0.5  # 调整绘制频率以获得更流畅的绘画体验


class DrawingApp:
    def __init__(self, root):
        self.root = root

        self.bg_color = "white"
        self.draw_color = "black"
        self.draw_size = 8
        self.erase_size = 15

        self.root.title("Draft")
        self.root.attributes("-topmost", 1)
        self.canvas = tk.Canvas(root, bg=self.bg_color)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.left_button)
        self.canvas.bind("<Button-2>", self.middle_button)
        self.canvas.bind("<Button-3>", self.right_button)
        self.canvas.bind("<Configure>", self.resize_canvas)
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)
        self.color_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Colors", menu=self.color_menu)
        self.color_menu.add_command(
            label="Choose Draw Color", command=self.choose_draw_color
        )
        self.color_menu.add_command(
            label="Choose Background Color", command=self.choose_bg_color
        )
        self.menu_bar.add_command(
            label="Black", command=lambda: self.draw_color_change("black")
        )
        self.menu_bar.add_command(
            label="Purple", command=lambda: self.draw_color_change("#8000FF")
        )
        self.menu_bar.add_command(
            label="Red", command=lambda: self.draw_color_change("red")
        )
        self.size_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Sizes", menu=self.size_menu)
        self.size_menu.add_command(label="Set Draw Size", command=self.set_draw_radius)
        self.size_menu.add_command(
            label="Set Erase Size", command=self.set_erase_radius
        )
        self.last_x, self.last_y = 0, 0
        self.draw_radius_var = tk.IntVar(value=self.draw_size)
        self.erase_radius_var = tk.IntVar(value=self.erase_size)
        self.thread_lock = threading.Lock()
        self.last_draw_time = 0

        self.canvas.bind(
            "<B1-Motion>",
            lambda event: self.motion_handler_with_delay(
                event, self, self.mouse_motion_thread
            ),
        )
        self.canvas.bind(
            "<B3-Motion>",
            lambda event: self.motion_handler_with_delay(
                event, self, self.erase_motion_thread
            ),
        )

    def update_draw_radius(self, event):
        self.draw_size = self.draw_radius_var.get()

    def update_erase_radius(self, event):
        self.erase_size = self.erase_radius_var.get()

    def draw(self, event, color, size):
        x, y = event.x, event.y
        dx = x - self.last_x
        dy = y - self.last_y
        distance = max(abs(dx), abs(dy))
        if distance <= 3:
            size = size / 2 - 1
            for i in range(distance + 1):
                point_x = self.last_x + i * dx // (distance + 1)
                point_y = self.last_y + i * dy // (distance + 1)
                self.canvas.create_rectangle(
                    point_x - size,
                    point_y - size,
                    point_x + size,
                    point_y + size,
                    fill=color,
                    width=0,
                )
        else:
            if x < self.last_x:
                if y < self.last_y:
                    self.canvas.create_line(
                        self.last_x + 1,
                        self.last_y + 1,
                        x - 1,
                        y - 1,
                        fill=color,
                        width=size,
                    )
                elif y > self.last_y:
                    self.canvas.create_line(
                        self.last_x + 1,
                        self.last_y - 1,
                        x - 1,
                        y + 1,
                        fill=color,
                        width=size,
                    )
                else:
                    self.canvas.create_line(
                        self.last_x + 1,
                        self.last_y,
                        x - 1,
                        y,
                        fill=color,
                        width=size,
                    )
            elif x > self.last_x:
                if y < self.last_y:
                    self.canvas.create_line(
                        self.last_x - 1,
                        self.last_y + 1,
                        x + 1,
                        y - 1,
                        fill=color,
                        width=size,
                    )
                elif y > self.last_y:
                    self.canvas.create_line(
                        self.last_x - 1,
                        self.last_y - 1,
                        x + 1,
                        y + 1,
                        fill=color,
                        width=size,
                    )
                else:
                    self.canvas.create_line(
                        self.last_x - 1,
                        self.last_y,
                        x + 1,
                        y,
                        fill=color,
                        width=size,
                    )
            else:
                if y < self.last_y:
                    self.canvas.create_line(
                        self.last_x,
                        self.last_y + 1,
                        x,
                        y - 1,
                        fill=color,
                        width=size,
                    )
                elif y > self.last_y:
                    self.canvas.create_line(
                        self.last_x,
                        self.last_y - 1,
                        x,
                        y + 1,
                        fill=color,
                        width=size,
                    )
                else:
                    self.canvas.create_line(
                        self.last_x,
                        self.last_y,
                        x,
                        y,
                        fill=color,
                        width=size,
                    )
        self.last_x, self.last_y = x, y

    def write(self, event):
        self.draw(event, self.draw_color, self.draw_size)

    def erase(self, event):
        self.draw(event, self.bg_color, self.erase_size)

    def left_button(self, event):
        self.last_x, self.last_y = event.x, event.y
        self.canvas.bind("<B1-Motion>", self.write)

    def right_button(self, event):
        self.last_x, self.last_y = event.x, event.y
        self.canvas.bind("<B3-Motion>", self.erase)

    def middle_button(self, event):
        self.canvas.delete("all")

    def resize_canvas(self, event):
        window_size = (event.width, event.height)
        # self.canvas.delete("all")  # 清空画布
        self.canvas.config(width=window_size[0] - 4, height=window_size[1] - 4)

    def choose_draw_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.draw_color = color

    def choose_bg_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.bg_color = color
            self.canvas.config(bg=self.bg_color)

    def set_draw_radius(self):
        self.root.attributes("-topmost", 0)
        self.draw_size = simpledialog.askinteger("Draw Size", "Enter draw size:")
        self.root.attributes("-topmost", 1)

    def set_erase_radius(self):
        self.root.attributes("-topmost", 0)
        self.erase_size = simpledialog.askinteger("Erase Size", "Enter erase size:")
        self.root.attributes("-topmost", 1)

    def draw_color_change(self, color):
        self.draw_color = color

    def motion_handler(self, event, motion_func):
        with self.thread_lock:
            motion_func(event)

    def mouse_motion_thread(self, event):
        self.motion_handler(event, self.write)

    def erase_motion_thread(self, event):
        self.motion_handler(event, self.erase)

    def motion_handler_with_delay(self, event, app, motion_func):
        if hasattr(app, "last_draw_time"):
            time_since_last_draw = time.time() - app.last_draw_time
            if time_since_last_draw < draw_frequency:
                return
            app.last_draw_time = time.time()
            motion_func(event)


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)

    root.mainloop()
