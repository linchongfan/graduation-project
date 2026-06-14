#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合蚁群算法求解TSP问题
结合蚁群算法 + 自适应参数 + 遗传算法
使用PyQt5 + PyQtGraph进行可视化
"""

import sys
import time

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPen
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox,
                             QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QPushButton, QSpinBox,
                             QTextEdit, QVBoxLayout, QWidget)


# =========================
# 城市生成
# =========================

def generate_cities(n_cities, width=100, height=100):
    """生成随机城市坐标"""
    return [(np.random.rand() * width, np.random.rand() * height) for _ in range(n_cities)]


# =========================
# 混合蚁群算法核心
# =========================

class HybridACOGA:
    """
    混合蚁群算法 + 遗传算法
    包含：自适应参数、精英策略、2-opt局部搜索
    """

    def __init__(self, cities, ant_count=50, alpha=1.0, beta=2.0,
                 rho=0.5, q=100, max_iter=1000,
                 crossover_rate=0.85, mutation_rate=0.15,
                 elite_ratio=0.1, use_2opt=True, use_ga=True,
                 adaptive_params=True):
        self.cities = cities
        self.n_cities = len(cities)
        self.ant_count = ant_count
        self.alpha_init = alpha
        self.beta_init = beta
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.max_iter = max_iter

        # 遗传算法参数
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.use_ga = use_ga

        # 精英策略参数
        self.elite_ratio = elite_ratio
        self.elite_count = max(1, int(ant_count * elite_ratio))

        # 局部搜索开关
        self.use_2opt = use_2opt

        # 自适应参数开关
        self.adaptive_params = adaptive_params

        # 初始化矩阵
        self.distance_matrix = self._calculate_distance_matrix()
        self.pheromone_matrix = np.ones((self.n_cities, self.n_cities))

        # 结果记录
        self.best_path = []
        self.best_distance = float("inf")
        self.iteration_best_distances = []

    # ==================== 基础方法 ====================

    def _calculate_distance_matrix(self):
        """计算距离矩阵"""
        distance_matrix = np.zeros((self.n_cities, self.n_cities))
        for i in range(self.n_cities):
            for j in range(self.n_cities):
                if i != j:
                    distance_matrix[i][j] = np.sqrt(
                        (self.cities[i][0] - self.cities[j][0]) ** 2 +
                        (self.cities[i][1] - self.cities[j][1]) ** 2
                    )
        return distance_matrix

    def _calculate_path_distance(self, path):
        """计算路径总距离"""
        distance = 0.0
        for i in range(len(path) - 1):
            city1, city2 = path[i], path[i + 1]
            if 0 <= city1 < self.n_cities and 0 <= city2 < self.n_cities:
                distance += self.distance_matrix[city1][city2]
            else:
                return float('inf')
        return distance

    # ==================== 自适应参数 ====================

    def _update_adaptive_params(self, iteration):
        """自适应参数调整"""
        if not self.adaptive_params:
            return
        ratio = iteration / self.max_iter
        self.alpha = 0.8 + 1.2 * ratio
        self.beta = 3.0 - 1.5 * ratio

    # ==================== 蚁群算法部分 ====================

    def _select_next_city(self, current_city, visited):
        """轮盘赌选择下一个城市"""
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

    def _construct_path(self):
        """单只蚂蚁构建路径"""
        start_city = np.random.randint(self.n_cities)
        visited = [start_city]
        current_city = start_city

        while len(visited) < self.n_cities:
            next_city = self._select_next_city(current_city, visited)
            if next_city is None:
                for city in range(self.n_cities):
                    if city not in visited:
                        next_city = city
                        break
            visited.append(next_city)
            current_city = next_city

        visited.append(start_city)
        return visited

    # ==================== 遗传算法部分 ====================

    def _order_crossover(self, parent1, parent2):
        """顺序交叉（OX）"""
        size = len(parent1)
        if size <= 3:
            return parent1.copy()

        start, end = sorted(np.random.choice(range(1, size - 1), 2, replace=False))

        child = [-1] * size
        child[start:end] = parent1[start:end]

        remaining = []
        for city in parent2[1:-1]:
            if city not in child[start:end] and city not in remaining:
                remaining.append(city)

        idx = 0
        for i in range(1, size - 1):
            if child[i] == -1:
                if idx < len(remaining):
                    child[i] = remaining[idx]
                    idx += 1
                else:
                    for city in range(self.n_cities):
                        if city not in child:
                            child[i] = city
                            break

        child[0] = parent1[0]
        child[-1] = parent1[0]

        if -1 in child or len(set(child[:-1])) != self.n_cities:
            return parent1.copy()

        return child

    def _swap_mutation(self, path):
        """交换变异"""
        if np.random.random() < self.mutation_rate:
            new_path = path.copy()
            n_middle = len(new_path) - 2
            if n_middle < 2:
                return path
            i, j = np.random.choice(range(1, len(new_path) - 1), 2, replace=False)
            new_path[i], new_path[j] = new_path[j], new_path[i]
            return new_path
        return path

    def _reverse_mutation(self, path):
        """逆转变异"""
        if np.random.random() < self.mutation_rate:
            new_path = path.copy()
            n_middle = len(new_path) - 2
            if n_middle < 2:
                return path
            i, j = sorted(np.random.choice(range(1, len(new_path) - 1), 2, replace=False))
            new_path[i:j + 1] = reversed(new_path[i:j + 1])
            return new_path
        return path

    def _genetic_enhancement(self, paths, distances):
        """遗传算法增强"""
        n = len(paths)

        sorted_indices = np.argsort(distances)
        n_elite = max(2, n // 4)
        elite_paths = [paths[i].copy() for i in sorted_indices[:n_elite]]
        elite_distances = [distances[i] for i in sorted_indices[:n_elite]]

        new_paths = list(elite_paths)

        while len(new_paths) < n:
            p1 = self._tournament_select(elite_paths, elite_distances)
            p2 = self._tournament_select(elite_paths, elite_distances)

            if np.random.random() < self.crossover_rate:
                child = self._order_crossover(p1, p2)
            else:
                child = p1.copy()

            if np.random.random() < 0.5:
                child = self._swap_mutation(child)
            else:
                child = self._reverse_mutation(child)

            child_distance = self._calculate_path_distance(child)
            if child_distance < float('inf') and len(set(child)) == self.n_cities:
                new_paths.append(child)
            else:
                new_paths.append(p1.copy())

        new_distances = [self._calculate_path_distance(p) for p in new_paths]

        return new_paths, new_distances

    def _tournament_select(self, paths, distances, tournament_size=3):
        """锦标赛选择"""
        indices = np.random.choice(len(paths), tournament_size, replace=False)
        best_idx = indices[np.argmin([distances[i] for i in indices])]
        return paths[best_idx].copy()

    # ==================== 局部搜索 ====================

    def _two_opt_improve(self, path):
        """2-opt局部搜索"""
        improved = True
        best_path = path.copy()
        best_distance = self._calculate_path_distance(best_path)

        if best_distance == float('inf'):
            return path, float('inf')

        while improved:
            improved = False
            for i in range(1, len(best_path) - 2):
                for j in range(i + 1, len(best_path) - 1):
                    if (best_path[i - 1] >= self.n_cities or best_path[i] >= self.n_cities or
                            best_path[j] >= self.n_cities or best_path[j + 1] >= self.n_cities):
                        continue

                    old_dist = (self.distance_matrix[best_path[i - 1]][best_path[i]] +
                                self.distance_matrix[best_path[j]][best_path[j + 1]])
                    new_dist = (self.distance_matrix[best_path[i - 1]][best_path[j]] +
                                self.distance_matrix[best_path[i]][best_path[j + 1]])

                    if new_dist < old_dist - 1e-10:
                        best_path[i:j + 1] = reversed(best_path[i:j + 1])
                        best_distance -= (old_dist - new_dist)
                        improved = True

        return best_path, best_distance

    # ==================== 信息素更新 ====================

    def _update_pheromone(self, all_paths, all_distances):
        """精英策略信息素更新"""
        self.pheromone_matrix *= (1 - self.rho)

        sorted_indices = np.argsort(all_distances)

        for rank, idx in enumerate(sorted_indices):
            path = all_paths[idx]
            distance = all_distances[idx]

            delta = self.q / distance

            if rank < self.elite_count:
                delta *= 2.0

            for i in range(len(path) - 1):
                city1, city2 = path[i], path[i + 1]
                if (0 <= city1 < self.n_cities and 0 <= city2 < self.n_cities):
                    self.pheromone_matrix[city1][city2] += delta
                    self.pheromone_matrix[city2][city1] += delta

    # ==================== 主循环 ====================

    def run(self):
        """运行混合算法"""
        start_time = time.time()

        for iteration in range(self.max_iter):
            self._update_adaptive_params(iteration)

            all_paths = []
            all_distances = []

            for _ in range(self.ant_count):
                path = self._construct_path()
                distance = self._calculate_path_distance(path)
                all_paths.append(path)
                all_distances.append(distance)

            if self.use_ga:
                all_paths, all_distances = self._genetic_enhancement(all_paths, all_distances)

            if self.use_2opt:
                sorted_indices = np.argsort(all_distances)
                for i in range(min(self.elite_count, len(all_paths))):
                    idx = sorted_indices[i]
                    improved_path, improved_distance = self._two_opt_improve(all_paths[idx])
                    if improved_distance < all_distances[idx]:
                        all_paths[idx] = improved_path
                        all_distances[idx] = improved_distance

            min_idx = np.argmin(all_distances)
            if all_distances[min_idx] < self.best_distance:
                self.best_distance = all_distances[min_idx]
                self.best_path = all_paths[min_idx].copy()

            self._update_pheromone(all_paths, all_distances)
            self.iteration_best_distances.append(self.best_distance)

        running_time = time.time() - start_time
        convergence_iteration = self._find_convergence()

        return {
            "best_path": self.best_path,
            "best_distance": self.best_distance,
            "running_time": running_time,
            "convergence_iteration": convergence_iteration,
            "iteration_best_distances": self.iteration_best_distances,
        }

    def _find_convergence(self):
        """找到收敛迭代次数"""
        for i in range(1, len(self.iteration_best_distances)):
            delta = abs(self.iteration_best_distances[i] - self.iteration_best_distances[i - 1])
            if delta < 0.01:
                return i
        return len(self.iteration_best_distances)


# =========================
# PyQt5 图形用户界面
# =========================

class HybridACOGUI(QMainWindow):
    """混合蚁群算法GUI - 使用PyQt5"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("混合蚁群算法求解 TSP 问题")
        self.setGeometry(100, 50, 1200, 800)

        self.cities = None

        # 设置全局字体
        font = QFont("Microsoft YaHei", 9)
        QApplication.instance().setFont(font)

        # 设置pyqtgraph样式
        pg.setConfigOptions(antialias=True)

        self._init_ui()
        self.generate_map()

    def _init_ui(self):
        """初始化界面"""
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # 上方可视化区域
        viz_group = QGroupBox("可视化结果")
        viz_layout = QHBoxLayout(viz_group)

        # 左图 - 城市/路径图
        self.path_plot = pg.PlotWidget(title="城市分布图")
        self.path_plot.setBackground('w')
        self.path_plot.showGrid(x=True, y=True, alpha=0.3)
        self.path_plot.setLabel('bottom', 'X 坐标')
        self.path_plot.setLabel('left', 'Y 坐标')

        # 右图 - 收敛曲线
        self.convergence_plot = pg.PlotWidget(title="收敛过程")
        self.convergence_plot.setBackground('w')
        self.convergence_plot.showGrid(x=True, y=True, alpha=0.3)
        self.convergence_plot.setLabel('bottom', '迭代次数')
        self.convergence_plot.setLabel('left', '最优距离')

        viz_layout.addWidget(self.path_plot)
        viz_layout.addWidget(self.convergence_plot)
        main_layout.addWidget(viz_group, stretch=3)

        # 下方控制和结果区域
        bottom_layout = QHBoxLayout()

        # 左侧 - 参数设置
        params_group = QGroupBox("参数设置")
        params_layout = QGridLayout(params_group)

        # 蚁群参数
        row = 0
        params_layout.addWidget(QLabel("城市数量:"), row, 0)
        self.n_cities_spin = QSpinBox()
        self.n_cities_spin.setRange(5, 500)
        self.n_cities_spin.setValue(50)
        params_layout.addWidget(self.n_cities_spin, row, 1)

        row += 1
        params_layout.addWidget(QLabel("蚂蚁数量:"), row, 0)
        self.ant_count_spin = QSpinBox()
        self.ant_count_spin.setRange(10, 200)
        self.ant_count_spin.setValue(50)
        params_layout.addWidget(self.ant_count_spin, row, 1)

        row += 1
        params_layout.addWidget(QLabel("alpha:"), row, 0)
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.1, 5.0)
        self.alpha_spin.setValue(1.0)
        self.alpha_spin.setSingleStep(0.1)
        params_layout.addWidget(self.alpha_spin, row, 1)

        row += 1
        params_layout.addWidget(QLabel("beta:"), row, 0)
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setRange(0.1, 5.0)
        self.beta_spin.setValue(2.0)
        self.beta_spin.setSingleStep(0.1)
        params_layout.addWidget(self.beta_spin, row, 1)

        row += 1
        params_layout.addWidget(QLabel("rho:"), row, 0)
        self.rho_spin = QDoubleSpinBox()
        self.rho_spin.setRange(0.1, 0.9)
        self.rho_spin.setValue(0.5)
        self.rho_spin.setSingleStep(0.1)
        params_layout.addWidget(self.rho_spin, row, 1)

        row += 1
        params_layout.addWidget(QLabel("Q:"), row, 0)
        self.q_spin = QSpinBox()
        self.q_spin.setRange(10, 500)
        self.q_spin.setValue(100)
        params_layout.addWidget(self.q_spin, row, 1)

        row += 1
        params_layout.addWidget(QLabel("迭代次数:"), row, 0)
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(10, 1000)
        self.max_iter_spin.setValue(100)
        self.max_iter_spin.setSingleStep(10)
        params_layout.addWidget(self.max_iter_spin, row, 1)

        # 混合算法选项
        row += 1
        params_layout.addWidget(QLabel("--- 混合算法选项 ---"), row, 0, 1, 2)

        row += 1
        self.adaptive_check = QCheckBox("自适应参数")
        self.adaptive_check.setChecked(True)
        params_layout.addWidget(self.adaptive_check, row, 0, 1, 2)

        row += 1
        self.ga_check = QCheckBox("遗传算法增强")
        self.ga_check.setChecked(True)
        params_layout.addWidget(self.ga_check, row, 0, 1, 2)

        row += 1
        self.opt2_check = QCheckBox("2-opt优化")
        self.opt2_check.setChecked(True)
        params_layout.addWidget(self.opt2_check, row, 0, 1, 2)

        row += 1
        params_layout.addWidget(QLabel("交叉率:"), row, 0)
        self.crossover_spin = QDoubleSpinBox()
        self.crossover_spin.setRange(0.5, 1.0)
        self.crossover_spin.setValue(0.85)
        self.crossover_spin.setSingleStep(0.05)
        params_layout.addWidget(self.crossover_spin, row, 1)

        row += 1
        params_layout.addWidget(QLabel("变异率:"), row, 0)
        self.mutation_spin = QDoubleSpinBox()
        self.mutation_spin.setRange(0.01, 0.5)
        self.mutation_spin.setValue(0.15)
        self.mutation_spin.setSingleStep(0.05)
        params_layout.addWidget(self.mutation_spin, row, 1)

        row += 1
        params_layout.addWidget(QLabel("精英比例:"), row, 0)
        self.elite_spin = QDoubleSpinBox()
        self.elite_spin.setRange(0.05, 0.3)
        self.elite_spin.setValue(0.1)
        self.elite_spin.setSingleStep(0.05)
        params_layout.addWidget(self.elite_spin, row, 1)

        # 按钮
        row += 1
        btn_layout = QHBoxLayout()
        self.gen_btn = QPushButton("生成地图")
        self.gen_btn.clicked.connect(self.generate_map)
        btn_layout.addWidget(self.gen_btn)

        self.run_btn = QPushButton("运行算法")
        self.run_btn.clicked.connect(self.run_algorithm)
        btn_layout.addWidget(self.run_btn)
        params_layout.addLayout(btn_layout, row, 0, 1, 2)

        bottom_layout.addWidget(params_group, stretch=1)

        # 右侧 - 求解结果
        result_group = QGroupBox("求解结果")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)

        bottom_layout.addWidget(result_group, stretch=1)

        main_layout.addLayout(bottom_layout, stretch=1)

    def generate_map(self):
        """生成地图"""
        try:
            n_cities = self.n_cities_spin.value()
            self.cities = generate_cities(n_cities)

            self.result_text.clear()
            self.result_text.append(f"已生成 {n_cities} 个城市的地图。")
            self.result_text.append('点击"运行算法"开始求解。')

            self._plot_cities()

        except Exception as exc:
            QMessageBox.critical(self, "错误", f"生成地图失败: {exc}")

    def run_algorithm(self):
        """运行算法"""
        try:
            if self.cities is None:
                QMessageBox.warning(self, "警告", "请先生成地图！")
                return

            params = {
                "n_cities": self.n_cities_spin.value(),
                "ant_count": self.ant_count_spin.value(),
                "alpha": self.alpha_spin.value(),
                "beta": self.beta_spin.value(),
                "rho": self.rho_spin.value(),
                "q": self.q_spin.value(),
                "max_iter": self.max_iter_spin.value(),
                "crossover_rate": self.crossover_spin.value(),
                "mutation_rate": self.mutation_spin.value(),
                "elite_ratio": self.elite_spin.value(),
                "use_ga": self.ga_check.isChecked(),
                "use_2opt": self.opt2_check.isChecked(),
                "adaptive_params": self.adaptive_check.isChecked(),
            }

            # 显示算法配置
            algo_config = []
            if params["adaptive_params"]:
                algo_config.append("自适应参数")
            if params["use_ga"]:
                algo_config.append("遗传算法")
            if params["use_2opt"]:
                algo_config.append("2-opt")
            config_str = " + ".join(algo_config) if algo_config else "基本ACO"

            self.result_text.clear()
            self.result_text.append(f"=== 算法配置 ===")
            self.result_text.append(f"算法: {config_str}")
            self.result_text.append(f"城市数: {params['n_cities']}, 蚂蚁数: {params['ant_count']}")
            self.result_text.append(f"\n开始求解...")
            QApplication.processEvents()

            solver = HybridACOGA(
                cities=self.cities,
                ant_count=params["ant_count"],
                alpha=params["alpha"],
                beta=params["beta"],
                rho=params["rho"],
                q=params["q"],
                max_iter=params["max_iter"],
                crossover_rate=params["crossover_rate"],
                mutation_rate=params["mutation_rate"],
                elite_ratio=params["elite_ratio"],
                use_2opt=params["use_2opt"],
                use_ga=params["use_ga"],
                adaptive_params=params["adaptive_params"],
            )

            results = solver.run()

            self.result_text.clear()
            self.result_text.append("=== 求解结果 ===")
            self.result_text.append(f"算法配置: {config_str}\n")
            self.result_text.append(f"最优距离: {results['best_distance']:.2f}")
            self.result_text.append(f"运行时间: {results['running_time']:.2f} 秒")
            self.result_text.append(f"收敛迭代: 第 {results['convergence_iteration']} 次")
            self.result_text.append(f"首次迭代距离: {results['iteration_best_distances'][0]:.2f}")

            # 找到最后一次距离下降的迭代次数
            last_decrease_iter = 0
            for i in range(1, len(results['iteration_best_distances'])):
                if results['iteration_best_distances'][i] < results['iteration_best_distances'][i - 1]:
                    last_decrease_iter = i
            self.result_text.append(f"最后下降迭代: 第 {last_decrease_iter} 次")

            if params["adaptive_params"]:
                self.result_text.append(f"\n自适应参数范围:")
                self.result_text.append(f"  alpha: {params['alpha']:.1f} → {solver.alpha:.2f}")
                self.result_text.append(f"  beta: {params['beta']:.1f} → {solver.beta:.2f}")

            self._plot_results(solver, results)

        except Exception as exc:
            QMessageBox.critical(self, "错误", f"运行失败: {exc}")

    def _plot_cities(self):
        """绘制城市分布图"""
        self.path_plot.clear()
        self.convergence_plot.clear()

        if self.cities is None:
            return

        x = [city[0] for city in self.cities]
        y = [city[1] for city in self.cities]

        # 绘制城市点
        self.path_plot.plot(x, y, pen=None, symbol='o', symbolSize=8,
                           symbolBrush=(70, 130, 180, 200), symbolPen='k')

        self.path_plot.setTitle(f"城市分布图（共 {len(self.cities)} 个城市）")

        # 右侧显示等待提示
        self.convergence_plot.setTitle("收敛过程")
        text = pg.TextItem("点击\"运行算法\"\n开始求解", color=(150, 150, 150))
        text.setPos(0.5, 0.5)
        self.convergence_plot.addItem(text)

    def _plot_results(self, solver, results):
        """绘制结果"""
        self.path_plot.clear()
        self.convergence_plot.clear()

        # 绘制最优路径
        path = results["best_path"]
        x = [solver.cities[city][0] for city in path]
        y = [solver.cities[city][1] for city in path]

        # 路径线
        pen = pg.mkPen(color=(70, 130, 180), width=2)
        self.path_plot.plot(x, y, pen=pen)

        # 城市点
        city_x = [solver.cities[city][0] for city in path[:-1]]
        city_y = [solver.cities[city][1] for city in path[:-1]]
        self.path_plot.plot(city_x, city_y, pen=None, symbol='o', symbolSize=8,
                           symbolBrush=(70, 130, 180, 200), symbolPen='k')

        self.path_plot.setTitle(f"最优路径（距离: {results['best_distance']:.2f}）")

        # 绘制收敛曲线
        iterations = list(range(len(results["iteration_best_distances"])))
        distances = results["iteration_best_distances"]

        pen = pg.mkPen(color=(220, 80, 60), width=2)
        self.convergence_plot.plot(iterations, distances, pen=pen)

        # 在距离下降的点上显示坐标
        for i in range(1, len(distances)):
            if distances[i] < distances[i - 1]:
                # 距离收缩了，显示坐标
                text = pg.TextItem(f"({i},{distances[i]:.0f})", color=(0, 128, 0),
                                   anchor=(0.5, 1))
                text.setPos(i, distances[i])
                self.convergence_plot.addItem(text)

        self.convergence_plot.setTitle("收敛过程")


# =========================
# 程序入口
# =========================

def main():
    app = QApplication(sys.argv)

    # 设置全局样式
    app.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton {
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
    """)

    window = HybridACOGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
