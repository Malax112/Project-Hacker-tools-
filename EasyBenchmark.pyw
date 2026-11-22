import subprocess
import sys

def ensure_module(module_name, package_name=None):
    try:
        __import__(module_name)
    except ImportError:
        package = package_name or module_name
        print(f"Installing {package}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package]
        )

ensure_module("customtkinter")

import time
import threading
import multiprocessing as mp
import customtkinter as ctk

REFERENCE_SINGLE_TIME = 1.0
REFERENCE_MULTI_TIME = 0.2


def bench_work(iterations):
    total = 0
    for i in range(iterations):
        total += i * i
    return total


def worker(iterations):
    return bench_work(iterations)


def run_benchmark(iterations, num_cores):
    start = time.perf_counter()
    bench_work(iterations)
    t_single = time.perf_counter() - start

    with mp.Pool(processes=num_cores) as pool:
        tasks = [iterations // num_cores] * num_cores
        start = time.perf_counter()
        list(pool.map(worker, tasks))
        t_multi = time.perf_counter() - start

    return t_single, t_multi


def calculate_scores(t_single, t_multi):
    s_score = max(0, min(100, int((REFERENCE_SINGLE_TIME / t_single) * 25)))
    m_score = max(0, min(100, int((REFERENCE_MULTI_TIME / t_multi) * 25)))
    total = int(s_score * 0.4 + m_score * 0.6)
    return total, s_score, m_score


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CPU Test")
        self.geometry("520x480")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.iterations = 10_000_000
        self.num_cores = mp.cpu_count()
        self.running = False

        ctk.CTkLabel(self, text="CPU Test",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(24, 4))
        ctk.CTkLabel(self, text=f"Cores: {self.num_cores}   •   Iterations: {self.iterations:,}",
                     text_color="gray").pack()

        self.progress = ctk.CTkProgressBar(self, width=440)
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.label_single = ctk.CTkLabel(self, text="Single-thread:  —  ",
                                         font=ctk.CTkFont(size=16))
        self.label_single.pack(pady=4)

        self.label_multi = ctk.CTkLabel(self, text="Multi-thread:  —  ",
                                        font=ctk.CTkFont(size=16))
        self.label_multi.pack(pady=4)

        self.label_score = ctk.CTkLabel(self, text="Score:  —  ",
                                        font=ctk.CTkFont(size=22, weight="bold"))
        self.label_score.pack(pady=10)

        self.btn_start = ctk.CTkButton(
            self, text="Start Test", width=220, height=44,
            corner_radius=22,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_test
        )
        self.btn_start.pack(pady=(14, 6))

        self.btn_stop = ctk.CTkButton(
            self, text="Reset", width=220, height=44,
            corner_radius=22,
            fg_color="gray30", hover_color="gray45",
            font=ctk.CTkFont(size=16),
            command=self.reset
        )
        self.btn_stop.pack(pady=6)

    def start_test(self):
        if self.running:
            return
        self.running = True
        self.btn_start.configure(state="disabled", text="Running...")
        self.progress.set(0)
        self.progress.set(0.2)
        threading.Thread(target=self.run_test, daemon=True).start()

    def run_test(self):
        t_single, t_multi = run_benchmark(self.iterations, self.num_cores)
        self.progress.set(1.0)
        total, s_score, m_score = calculate_scores(t_single, t_multi)
        self.after(0, self.show_results, t_single, t_multi, total, s_score, m_score)

    def show_results(self, t_single, t_multi, total, s_score, m_score):
        speedup = t_single / t_multi if t_multi > 0 else 0
        self.label_single.configure(text=f"Single-thread: {t_single:.3f} s ({s_score}/100)")
        self.label_multi.configure(
            text=f"Multi-thread ({self.num_cores} threads): {t_multi:.3f} s ({m_score}/100)"
        )
        self.label_score.configure(text=f"Score: {total}/100   (speedup {speedup:.2f}x)")
        self.btn_start.configure(state="normal", text="Start Test")
        self.running = False

    def reset(self):
        self.label_single.configure(text="Single-thread:  —  ")
        self.label_multi.configure(text="Multi-thread:  —  ")
        self.label_score.configure(text="Score:  —  ")
        self.progress.set(0)


if __name__ == "__main__":
    app = App()
    app.mainloop()
