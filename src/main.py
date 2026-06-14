#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蚁群算法求解TSP问题的GUI程序。

用法:
    python main.py
"""

import time
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================
# TSP / ACO core
# =========================


def generate_cities(n_cities, width=100, height=100):
    """Generate random city coordinates."""
    return [(np.random.rand() * width, np.random.rand() * height) for _ in range(n_cities)]


class AntColonyTSP:
    """Ant Colony Optimization solver for TSP."""

    def __init__(self, cities, ant_count=50, alpha=1.0, beta=2.0, rho=0.5, q=100, max_iter=1000):
        self.cities = cities
        self.n_cities = len(cities)
        self.ant_count = ant_count
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.max_iter = max_iter

        self.distance_matrix = self._calculate_distance_matrix()
        self.pheromone_matrix = np.ones((self.n_cities, self.n_cities))
        self.best_path = []
        self.best_distance = float("inf")
        self.iteration_best_distances = []

    def _calculate_distance_matrix(self):
        distance_matrix = np.zeros((self.n_cities, self.n_cities))
        for i in range(self.n_cities):
            for j in range(self.n_cities):
                if i == j:
                    continue
                distance_matrix[i][j] = np.sqrt(
                    (self.cities[i][0] - self.cities[j][0]) ** 2
                    + (self.cities[i][1] - self.cities[j][1]) ** 2
                )
        return distance_matrix

    def _select_next_city(self, current_city, visited):
        probabilities = []
        total_weight = 0.0

        for city in range(self.n_cities):
            if city in visited:
                continue

            pheromone = self.pheromone_matrix[current_city][city] ** self.alpha
            heuristic = (1.0 / self.distance_matrix[current_city][city]) ** self.beta
            weight = pheromone * heuristic
            probabilities.append((city, weight))
            total_weight += weight

        if total_weight > 0:
            random_value = np.random.random()
            cumulative = 0.0
            for city, weight in probabilities:
                cumulative += weight / total_weight
                if random_value <= cumulative:
                    return city

        unvisited = [city for city in range(self.n_cities) if city not in visited]
        return np.random.choice(unvisited)

    def _update_pheromone(self, all_paths, all_distances):
        self.pheromone_matrix *= (1 - self.rho)

        for path, distance in zip(all_paths, all_distances):
            delta = self.q / distance
            for i in range(len(path) - 1):
                city1 = path[i]
                city2 = path[i + 1]
                self.pheromone_matrix[city1][city2] += delta
                self.pheromone_matrix[city2][city1] += delta

    def run(self):
        start_time = time.time()

        for _ in range(self.max_iter):
            all_paths = []
            all_distances = []

            for _ in range(self.ant_count):
                start_city = np.random.randint(self.n_cities)
                visited = [start_city]
                current_city = start_city

                while len(visited) < self.n_cities:
                    next_city = self._select_next_city(current_city, visited)
                    visited.append(next_city)
                    current_city = next_city

                visited.append(start_city)
                all_paths.append(visited)

                distance = 0.0
                for i in range(len(visited) - 1):
                    distance += self.distance_matrix[visited[i]][visited[i + 1]]
                all_distances.append(distance)

                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_path = visited.copy()

            self._update_pheromone(all_paths, all_distances)
            self.iteration_best_distances.append(self.best_distance)

        running_time = time.time() - start_time

        convergence_iteration = 0
        for i in range(1, len(self.iteration_best_distances)):
            delta = abs(self.iteration_best_distances[i] - self.iteration_best_distances[i - 1])
            if delta < 0.01:
                convergence_iteration = i
                break

        return {
            "best_path": self.best_path,
            "best_distance": self.best_distance,
            "running_time": running_time,
            "convergence_iteration": convergence_iteration,
            "iteration_best_distances": self.iteration_best_distances,
        }


# =========================
# Plot helpers
# =========================


def setup_chinese_font():
    """Configure matplotlib to render Chinese labels."""
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False


def create_figure(figsize=(8, 8), dpi=100):
    """Create the two-panel figure."""
    fig = plt.Figure(figsize=figsize, dpi=dpi)
    ax_path = fig.add_subplot(121)
    ax_convergence = fig.add_subplot(122)
    return fig, ax_path, ax_convergence


def plot_best_path(ax, cities, path, best_distance):
    """Plot the best route."""
    x = [cities[city][0] for city in path]
    y = [cities[city][1] for city in path]
    ax.plot(x, y, "o-", linewidth=1.2, markersize=4)
    ax.set_title(f"最优路径（距离: {best_distance:.2f}）")
    ax.set_xlabel("X 坐标")
    ax.set_ylabel("Y 坐标")


def plot_convergence(ax, iteration_best_distances):
    """Plot convergence history."""
    ax.plot(iteration_best_distances)
    ax.set_title("收敛过程")
    ax.set_xlabel("迭代次数")
    ax.set_ylabel("最优距离")


# =========================
# GUI
# =========================


class AntColonyGUI:
    """Tkinter GUI for the ACO TSP demo."""

    def __init__(self, root):
        self.root = root
        self.root.title("蚁群算法求解 TSP 问题")
        self.root.geometry("1200x900")

        self.cities = None

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.params_frame = ttk.LabelFrame(self.main_frame, text="参数设置", padding="10")
        self.params_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.canvas_frame = ttk.LabelFrame(self.main_frame, text="可视化结果", padding="10")
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._create_param_controls()
        self._create_canvas()
        self._create_actions()
        self._create_result_box()

    def _create_param_controls(self):
        ttk.Label(self.params_frame, text="城市数量:").pack(anchor=tk.W, pady=2)
        self.n_cities_var = tk.IntVar(value=50)
        ttk.Entry(self.params_frame, textvariable=self.n_cities_var, width=10).pack(anchor=tk.W, pady=2)

        ttk.Label(self.params_frame, text="蚂蚁数量:").pack(anchor=tk.W, pady=2)
        self.ant_count_var = tk.IntVar(value=50)
        ttk.Entry(self.params_frame, textvariable=self.ant_count_var, width=10).pack(anchor=tk.W, pady=2)

        ttk.Label(self.params_frame, text="信息素因子(alpha):").pack(anchor=tk.W, pady=2)
        self.alpha_var = tk.DoubleVar(value=1.0)
        ttk.Entry(self.params_frame, textvariable=self.alpha_var, width=10).pack(anchor=tk.W, pady=2)

        ttk.Label(self.params_frame, text="启发函数因子(beta):").pack(anchor=tk.W, pady=2)
        self.beta_var = tk.DoubleVar(value=2.0)
        ttk.Entry(self.params_frame, textvariable=self.beta_var, width=10).pack(anchor=tk.W, pady=2)

        ttk.Label(self.params_frame, text="挥发因子(rho):").pack(anchor=tk.W, pady=2)
        self.rho_var = tk.DoubleVar(value=0.5)
        ttk.Entry(self.params_frame, textvariable=self.rho_var, width=10).pack(anchor=tk.W, pady=2)

        ttk.Label(self.params_frame, text="信息素常数(q):").pack(anchor=tk.W, pady=2)
        self.q_var = tk.IntVar(value=100)
        ttk.Entry(self.params_frame, textvariable=self.q_var, width=10).pack(anchor=tk.W, pady=2)

        ttk.Label(self.params_frame, text="最大迭代次数:").pack(anchor=tk.W, pady=2)
        self.max_iter_var = tk.IntVar(value=100)
        ttk.Entry(self.params_frame, textvariable=self.max_iter_var, width=10).pack(anchor=tk.W, pady=2)

    def _create_canvas(self):
        self.fig, self.ax1, self.ax2 = create_figure(figsize=(8, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _create_actions(self):
        ttk.Button(self.params_frame, text="生成地图", command=self.generate_map).pack(pady=(10, 5), fill=tk.X)
        ttk.Button(self.params_frame, text="运行算法", command=self.run_algorithm).pack(pady=5, fill=tk.X)

    def _create_result_box(self):
        self.result_frame = ttk.LabelFrame(self.params_frame, text="结果", padding="10")
        self.result_frame.pack(fill=tk.X, pady=10)

        self.result_text = tk.Text(self.result_frame, height=10, width=40)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def _validate_inputs(self):
        n_cities = self.n_cities_var.get()
        ant_count = self.ant_count_var.get()

        if n_cities < 2:
            messagebox.showerror("错误", "城市数量至少为 2。")
            return None
        if ant_count < 1:
            messagebox.showerror("错误", "蚂蚁数量至少为 1。")
            return None

        return {
            "n_cities": n_cities,
            "ant_count": ant_count,
            "alpha": self.alpha_var.get(),
            "beta": self.beta_var.get(),
            "rho": self.rho_var.get(),
            "q": self.q_var.get(),
            "max_iter": self.max_iter_var.get(),
        }

    def run_algorithm(self):
        try:
            params = self._validate_inputs()
            if params is None:
                return

            if self.cities is None or len(self.cities) != params["n_cities"]:
                self.cities = generate_cities(params["n_cities"])

            solver = AntColonyTSP(
                cities=self.cities,
                ant_count=params["ant_count"],
                alpha=params["alpha"],
                beta=params["beta"],
                rho=params["rho"],
                q=params["q"],
                max_iter=params["max_iter"],
            )

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"开始求解 {params['n_cities']} 个城市的旅行商问题...\n")
            self.root.update()

            results = solver.run()

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END,
                "求解结果:\n"
                f"最优距离: {results['best_distance']:.2f}\n"
                f"运行时间: {results['running_time']:.2f} 秒\n"
                f"收敛迭代次数: {results['convergence_iteration']}\n",
            )

            self._plot_results(solver, results)

        except Exception as exc:
            messagebox.showerror("错误", f"运行失败: {exc}")

    def generate_map(self):
        try:
            params = self._validate_inputs()
            if params is None:
                return

            self.cities = generate_cities(params["n_cities"])
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"已生成 {params['n_cities']} 个城市的地图。\n")
            self.result_text.insert(tk.END, "点击“运行算法”开始求解。\n")
            self._plot_cities()

        except Exception as exc:
            messagebox.showerror("错误", f"生成地图失败: {exc}")

    def _plot_cities(self):
        setup_chinese_font()
        self.ax1.clear()
        self.ax2.clear()

        x = [city[0] for city in self.cities]
        y = [city[1] for city in self.cities]
        self.ax1.scatter(x, y, s=35, c="steelblue", alpha=0.8, edgecolors="black")
        self.ax1.set_title(f"城市分布图（共 {len(self.cities)} 个城市）")
        self.ax1.set_xlabel("X 坐标")
        self.ax1.set_ylabel("Y 坐标")

        self.ax2.set_title("等待运行算法...")
        self.ax2.set_xlabel("迭代次数")
        self.ax2.set_ylabel("最优距离")

        self.fig.tight_layout()
        self.canvas.draw()

    def _plot_results(self, solver, results):
        setup_chinese_font()
        self.ax1.clear()
        self.ax2.clear()

        plot_best_path(
            ax=self.ax1,
            cities=solver.cities,
            path=results["best_path"],
            best_distance=results["best_distance"],
        )
        plot_convergence(
            ax=self.ax2,
            iteration_best_distances=results["iteration_best_distances"],
        )

        self.fig.tight_layout()
        self.canvas.draw()


# =========================
# Entry point
# =========================


def main():
    root = tk.Tk()
    AntColonyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
