import tkinter as tk
from tkinter import colorchooser, simpledialog
import threading
import time

bg_color = "white"
draw_color = "black"
draw_radius = 3
erase_radius = 20
draw_frequency = 0.5  # 调整绘制频率以获得更流畅的绘画体验


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Draft")
        self.root.attributes("-topmost", 1)
        self.canvas = tk.Canvas(root, bg=bg_color)
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
        self.size_menu.add_command(
            label="Set Draw Radius", command=self.set_draw_radius
        )
        self.size_menu.add_command(
            label="Set Erase Radius", command=self.set_erase_radius
        )
        self.last_x, self.last_y = 0, 0
        self.draw_radius_var = tk.IntVar(value=draw_radius)
        self.erase_radius_var = tk.IntVar(value=erase_radius)
        self.thread_lock = threading.Lock()
        self.last_draw_time = 0

    def update_draw_radius(self, event):
        global draw_radius
        draw_radius = self.draw_radius_var.get()

    def update_erase_radius(self, event):
        global erase_radius
        erase_radius = self.erase_radius_var.get()

    def draw(self, event, color, radius):
        x, y = event.x, event.y
        dx = x - self.last_x
        dy = y - self.last_y
        distance = max(abs(dx), abs(dy))
        for i in range(distance + 1):
            point_x = self.last_x + i * dx // (distance + 1)
            point_y = self.last_y + i * dy // (distance + 1)
            self.canvas.create_oval(
                point_x - radius,
                point_y - radius,
                point_x + radius,
                point_y + radius,
                fill=color,
                width=0,
            )
        self.last_x, self.last_y = x, y

    def write(self, event):
        self.draw(event, draw_color, draw_radius)

    def erase(self, event):
        self.draw(event, bg_color, erase_radius)

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
        self.canvas.delete("all")  # 清空画布
        self.canvas.config(width=window_size[0] - 4, height=window_size[1] - 4)

    def choose_draw_color(self):
        global draw_color
        color = colorchooser.askcolor()[1]
        if color:
            draw_color = color

    def choose_bg_color(self):
        global bg_color
        color = colorchooser.askcolor()[1]
        if color:
            bg_color = color
            self.canvas.config(bg=bg_color)

    def set_draw_radius(self):
        global draw_radius
        draw_radius = simpledialog.askinteger("Draw Radius", "Enter draw radius:")

    def set_erase_radius(self):
        global erase_radius
        erase_radius = simpledialog.askinteger("Erase Radius", "Enter erase radius:")

    def draw_color_change(self, color):
        global draw_color
        draw_color = color

    def motion_handler(self, event, motion_func):
        with self.thread_lock:
            motion_func(event)

    def mouse_motion_thread(self, event):
        self.motion_handler(event, self.write)

    def erase_motion_thread(self, event):
        self.motion_handler(event, self.erase)


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)

    def motion_handler_with_delay(event, app, motion_func):
        if hasattr(app, "last_draw_time"):
            time_since_last_draw = time.time() - app.last_draw_time
            if time_since_last_draw < draw_frequency:
                return
            app.last_draw_time = time.time()
            motion_func(event)

    app.canvas.bind(
        "<B1-Motion>",
        lambda event: motion_handler_with_delay(event, app, app.mouse_motion_thread),
    )
    app.canvas.bind(
        "<B3-Motion>",
        lambda event: motion_handler_with_delay(event, app, app.erase_motion_thread),
    )

    root.mainloop()
