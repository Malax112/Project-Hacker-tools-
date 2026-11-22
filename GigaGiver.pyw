import os
import re
import threading
import tkinter as tk
from tkinter import messagebox


BASE_NAME = "Just a file"


def get_next_number(folder):
    pattern = re.compile(rf"^{re.escape(BASE_NAME)} $(\d+)$$")
    max_number = 0
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if os.path.isfile(path):
                match = pattern.match(name)
                if match:
                    max_number = max(max_number, int(match.group(1)))
    return max_number + 1


def get_next_file_path(folder):
    first_path = os.path.join(folder, BASE_NAME)
    if not os.path.exists(first_path):
        return first_path
    number = get_next_number(folder)
    return os.path.join(folder, f"{BASE_NAME} ({number})")


class RoundButton(tk.Canvas):
    def __init__(self, master, text, width, height, radius,
                 bg="#1f6feb", hover="#388bfd", fg="white", command=None):
        super().__init__(master, width=width, height=height,
                         bg=master["bg"], highlightthickness=0)
        self.command = command
        self.bg, self.hover, self.fg = bg, hover, fg
        self.text = text
        self.radius = radius
        self.enabled = True
        self.draw(bg)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", lambda e: self.enabled and self.draw(self.hover))
        self.bind("<Leave>", lambda e: self.enabled and self.draw(self.bg))

    def draw(self, color):
        w = int(self["width"])
        h = int(self["height"])
        self.delete("all")
        self.create_oval(0, 0, 2 * self.radius, h, fill=color, outline="")
        self.create_oval(w - 2 * self.radius, 0, w, h, fill=color, outline="")
        self.create_rectangle(self.radius, 0, w - self.radius, h,
                              fill=color, outline="")
        self.create_text(w // 2, h // 2, text=self.text,
                         fill=self.fg, font=("Segoe UI", 14, "bold"))

    def on_click(self, event):
        if self.enabled and self.command:
            self.command()

    def set_enabled(self, state):
        self.enabled = state
        self.draw("#444c56" if not state else self.bg)

    def set_text(self, text):
        self.text = text
        self.draw(self.bg if self.enabled else "#444c56")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Generator")
        self.geometry("520x420")
        self.resizable(False, False)
        self.configure(bg="#1c1c1c")

        self.folder = os.path.dirname(os.path.abspath(__file__))
        self.running = False

        tk.Label(self, text="File Generator", bg="#1c1c1c", fg="white",
                 font=("Segoe UI", 24, "bold")).pack(pady=(24, 4))
        tk.Label(self, bg="#1c1c1c", fg="gray",
                 text=f"Folder: {self.folder}",
                 font=("Segoe UI", 10), wraplength=460).pack()

        self.next_name = tk.Label(self, bg="#1c1c1c", fg="#58a6ff",
                                  text=f"Next file: {os.path.basename(get_next_file_path(self.folder))}",
                                  font=("Segoe UI", 12))
        self.next_name.pack(pady=(12, 0))

        tk.Label(self, text="Size (MB):", bg="#1c1c1c", fg="white",
                 font=("Segoe UI", 13)).pack(pady=(10, 2))

        self.entry = tk.Entry(self, width=14, font=("Segoe UI", 15),
                              bg="#2a2a2a", fg="white",
                              insertbackground="white",
                              justify="center", relief="flat")
        self.entry.pack(pady=4)
        self.entry.focus()

        self.status = tk.Label(self, bg="#1c1c1c", fg="gray",
                               text="", font=("Segoe UI", 12))
        self.status.pack(pady=8)

        self.btn_create = RoundButton(self, "Create File", 220, 44, 22,
                                      command=self.start)
        self.btn_create.pack(pady=(6, 4))

        self.btn_clear = RoundButton(self, "Clear", 220, 44, 22,
                                     bg="#4a4a4a", hover="#5c5c5c",
                                     command=self.reset)
        self.btn_clear.pack(pady=4)

        self.entry.bind("<Return>", lambda e: self.start())

    def parse_size(self):
        raw = self.entry.get().strip().replace(",", ".")
        try:
            size_mb = float(raw)
        except ValueError:
            return None
        return size_mb if size_mb > 0 else None

    def start(self):
        if self.running:
            return
        size_mb = self.parse_size()
        if size_mb is None:
            messagebox.showwarning("File Generator", "Enter a size > 0\nFor example: 5")
            return
        self.running = True
        self.btn_create.set_enabled(False)
        self.btn_create.set_text("Writing...")
        self.status.configure(text="Creating file...", fg="gray")
        file_path = get_next_file_path(self.folder)
        threading.Thread(target=self.create_file, args=(size_mb, file_path), daemon=True).start()

    def create_file(self, size_mb, file_path):
        bytes_per_chunk = 1024 * 1024
        remaining = int(size_mb * 1024 * 1024)

        try:
            with open(file_path, "wb") as f:
                while remaining > 0:
                    chunk_size = min(bytes_per_chunk, remaining)
                    f.write(b"\x00" * chunk_size)
                    remaining -= chunk_size
            size = os.path.getsize(file_path) / (1024 * 1024)
            result = f"Done! File: {os.path.basename(file_path)} — {size:.2f} MB"
            color = "#4ade80"
        except OSError as e:
            result = f"Error: {e}"
            color = "#f87171"

        self.after(0, self.finish, result, color)

    def finish(self, text, color):
        self.status.configure(text=text, fg=color)
        self.btn_create.set_enabled(True)
        self.btn_create.set_text("Create File")
        self.running = False
        self.next_name.configure(
            text=f"Next file: {os.path.basename(get_next_file_path(self.folder))}"
        )

    def reset(self):
        self.entry.delete(0, tk.END)
        self.status.configure(text="", fg="gray")
        self.entry.focus()


if __name__ == "__main__":
    app = App()
    app.mainloop()
