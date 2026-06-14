#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合蚁群算法求解TSP问题
结合蚁群算法 + 自适应参数 + 遗传算法 + 2-opt局部搜索

日期：2026年
版本：2.0

功能说明：
    1. 传统蚁群算法（ACO）求解TSP问题
    2. 自适应参数调整策略
    3. 遗传算法（GA）增强
    4. 2-opt局部搜索优化
    5. 精英蚂蚁策略
    6. PyQt5 + PyQtGraph 可视化界面

使用方法：
    python hybrid_aco.py

依赖库：
    - numpy
    - pyqt5
    - pyqtgraph
"""

import sys
import time
import json
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPen, QColor, QPainter
from PyQt5.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QSpinBox, QSplitter,
    QTextEdit, QVBoxLayout, QWidget, QTabWidget, QStatusBar
)


# =========================
# 配置常量
# =========================

class AlgorithmConfig:
    """算法配置常量"""
    # 默认参数
    DEFAULT_ALPHA = 1.0
    DEFAULT_BETA = 2.0
    DEFAULT_RHO = 0.5
    DEFAULT_Q = 100
    DEFAULT_ANT_COUNT = 50
    DEFAULT_MAX_ITER = 1000
    DEFAULT_CITIES = 50

    # 自适应参数范围
    ALPHA_MIN = 0.5
    ALPHA_MAX = 2.5
    BETA_MIN = 1.0
    BETA_MAX = 4.0

    # 遗传算法默认参数
    DEFAULT_CROSSOVER_RATE = 0.85
    DEFAULT_MUTATION_RATE = 0.15
    DEFAULT_ELITE_RATIO = 0.1

    # 收敛判定阈值
    CONVERGENCE_THRESHOLD = 0.01

    # 信息素限制
    PHEROMONE_MIN = 0.01
    PHEROMONE_MAX = 100.0


class VisualizationConfig:
    """可视化配置"""
    # 颜色定义
    CITY_COLOR = (70, 130, 180, 200)
    PATH_COLOR = (70, 130, 180)
    CONVERGENCE_COLOR = (220, 80, 60)
    TEXT_COLOR = (100, 100, 100)
    HIGHLIGHT_COLOR = (0, 128, 0)

    # 图表样式
    BACKGROUND_COLOR = 'w'
    GRID_ALPHA = 0.3
    SYMBOL_SIZE = 8
    PATH_WIDTH = 2


# =========================
# 数据结构定义
# =========================

@dataclass
class City:
    """城市数据类"""
    x: float
    y: float
    id: int = 0

    def distance_to(self, other: 'City') -> float:
        """计算到另一个城市的距离"""
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def to_tuple(self) -> Tuple[float, float]:
        """转换为元组"""
        return (self.x, self.y)

    def __repr__(self) -> str:
        return f"City(id={self.id}, x={self.x:.2f}, y={self.y:.2f})"


@dataclass
class AlgorithmResult:
    """算法结果数据类"""
    best_path: List[int]
    best_distance: float
    running_time: float
    convergence_iteration: int
    iteration_best_distances: List[float]
    first_iteration_distance: float = 0.0
    last_decrease_iteration: int = 0
    total_decrease_count: int = 0
    alpha_history: List[float] = field(default_factory=list)
    beta_history: List[float] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理"""
        if self.iteration_best_distances:
            self.first_iteration_distance = self.iteration_best_distances[0]
            self._calculate_decrease_stats()

    def _calculate_decrease_stats(self):
        """计算距离下降统计"""
        self.total_decrease_count = 0
        self.last_decrease_iteration = 0

        for i in range(1, len(self.iteration_best_distances)):
            if self.iteration_best_distances[i] < self.iteration_best_distances[i - 1]:
                self.total_decrease_count += 1
                self.last_decrease_iteration = i

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'best_distance': self.best_distance,
            'running_time': self.running_time,
            'convergence_iteration': self.convergence_iteration,
            'first_iteration_distance': self.first_iteration_distance,
            'last_decrease_iteration': self.last_decrease_iteration,
            'total_decrease_count': self.total_decrease_count,
        }


class OptimizationStrategy(Enum):
    """优化策略枚举"""
    NONE = "none"
    ADAPTIVE = "adaptive"
    GENETIC = "genetic"
    TWO_OPT = "two_opt"
    HYBRID = "hybrid"


# =========================
# 城市生成模块
# =========================

class CityGenerator:
    """城市生成器"""

    @staticmethod
    def generate_random(n_cities: int, width: float = 100.0,
                        height: float = 100.0) -> List[Tuple[float, float]]:
        """
        生成随机城市坐标

        Args:
            n_cities: 城市数量
            width: 区域宽度
            height: 区域高度

        Returns:
            城市坐标列表
        """
        cities = []
        for i in range(n_cities):
            x = np.random.rand() * width
            y = np.random.rand() * height
            cities.append((x, y))
        return cities

    @staticmethod
    def generate_clustered(n_cities: int, n_clusters: int = 3,
                           width: float = 100.0, height: float = 100.0) -> List[Tuple[float, float]]:
        """
        生成聚类分布的城市

        Args:
            n_cities: 城市数量
            n_clusters: 聚类数量
            width: 区域宽度
            height: 区域高度

        Returns:
            城市坐标列表
        """
        # 生成聚类中心
        centers = [(np.random.rand() * width, np.random.rand() * height)
                   for _ in range(n_clusters)]

        cities = []
        cities_per_cluster = n_cities // n_clusters

        for i, center in enumerate(centers):
            n = cities_per_cluster if i < n_clusters - 1 else n_cities - len(cities)
            for _ in range(n):
                x = center[0] + np.random.randn() * 10
                y = center[1] + np.random.randn() * 10
                x = np.clip(x, 0, width)
                y = np.clip(y, 0, height)
                cities.append((x, y))

        return cities

    @staticmethod
    def generate_grid(n_cities: int, width: float = 100.0,
                      height: float = 100.0) -> List[Tuple[float, float]]:
        """
        生成网格分布的城市

        Args:
            n_cities: 城市数量
            width: 区域宽度
            height: 区域高度

        Returns:
            城市坐标列表
        """
        n_per_side = int(np.ceil(np.sqrt(n_cities)))
        spacing_x = width / (n_per_side + 1)
        spacing_y = height / (n_per_side + 1)

        cities = []
        for i in range(n_per_side):
            for j in range(n_per_side):
                if len(cities) >= n_cities:
                    break
                x = spacing_x * (i + 1)
                y = spacing_y * (j + 1)
                cities.append((x, y))

        return cities[:n_cities]


# =========================
# 距离计算模块
# =========================

class DistanceCalculator:
    """距离计算器"""

    @staticmethod
    def calculate_distance_matrix(cities: List[Tuple[float, float]]) -> np.ndarray:
        """
        计算距离矩阵

        Args:
            cities: 城市坐标列表

        Returns:
            距离矩阵
        """
        n = len(cities)
        distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(
                    (cities[i][0] - cities[j][0]) ** 2 +
                    (cities[i][1] - cities[j][1]) ** 2
                )
                distance_matrix[i][j] = dist
                distance_matrix[j][i] = dist

        return distance_matrix

    @staticmethod
    def calculate_path_distance(path: List[int],
                                distance_matrix: np.ndarray) -> float:
        """
        计算路径总距离

        Args:
            path: 路径列表
            distance_matrix: 距离矩阵

        Returns:
            路径总距离
        """
        distance = 0.0
        for i in range(len(path) - 1):
            city1, city2 = path[i], path[i + 1]
            if 0 <= city1 < len(distance_matrix) and 0 <= city2 < len(distance_matrix):
                distance += distance_matrix[city1][city2]
            else:
                return float('inf')
        return distance

    @staticmethod
    def calculate_2opt_delta(distance_matrix: np.ndarray,
                             path: List[int], i: int, j: int) -> float:
        """
        计算2-opt交换的距离变化量

        Args:
            distance_matrix: 距离矩阵
            path: 当前路径
            i: 交换起始位置
            j: 交换结束位置

        Returns:
            距离变化量（负值表示改善）
        """
        n = len(path) - 1
        if i <= 0 or j >= n:
            return 0.0

        # 旧路径的两条边
        old_dist = (distance_matrix[path[i - 1]][path[i]] +
                    distance_matrix[path[j]][path[j + 1]])

        # 新路径的两条边
        new_dist = (distance_matrix[path[i - 1]][path[j]] +
                    distance_matrix[path[i]][path[j + 1]])

        return new_dist - old_dist


# =========================
# 信息素管理模块
# =========================

class PheromoneManager:
    """信息素管理器"""

    def __init__(self, n_cities: int, initial_pheromone: float = 1.0):
        """
        初始化信息素管理器

        Args:
            n_cities: 城市数量
            initial_pheromone: 初始信息素浓度
        """
        self.n_cities = n_cities
        self.pheromone_matrix = np.full((n_cities, n_cities), initial_pheromone)
        self.initial_pheromone = initial_pheromone

    def evaporate(self, rho: float):
        """
        信息素挥发

        Args:
            rho: 挥发率
        """
        self.pheromone_matrix *= (1 - rho)
        # 限制信息素浓度范围
        self.pheromone_matrix = np.clip(
            self.pheromone_matrix,
            AlgorithmConfig.PHEROMONE_MIN,
            AlgorithmConfig.PHEROMONE_MAX
        )

    def deposit(self, path: List[int], delta: float):
        """
        信息素沉积

        Args:
            path: 蚂蚁路径
            delta: 信息素增量
        """
        for i in range(len(path) - 1):
            city1, city2 = path[i], path[i + 1]
            if (0 <= city1 < self.n_cities and 0 <= city2 < self.n_cities):
                self.pheromone_matrix[city1][city2] += delta
                self.pheromone_matrix[city2][city1] += delta

        # 限制信息素浓度范围
        self.pheromone_matrix = np.clip(
            self.pheromone_matrix,
            AlgorithmConfig.PHEROMONE_MIN,
            AlgorithmConfig.PHEROMONE_MAX
        )

    def get_pheromone(self, city1: int, city2: int) -> float:
        """获取两个城市间的信息素浓度"""
        return self.pheromone_matrix[city1][city2]

    def reset(self):
        """重置信息素矩阵"""
        self.pheromone_matrix.fill(self.initial_pheromone)

    def get_average(self) -> float:
        """获取平均信息素浓度"""
        return np.mean(self.pheromone_matrix)

    def get_max(self) -> float:
        """获取最大信息素浓度"""
        return np.max(self.pheromone_matrix)

    def get_min(self) -> float:
        """获取最小信息素浓度"""
        return np.min(self.pheromone_matrix)


# =========================
# 蚁群算法核心模块
# =========================

class Ant:
    """蚂蚁类"""

    def __init__(self, n_cities: int):
        self.n_cities = n_cities
        self.visited: List[int] = []
        self.current_city: int = -1
        self.path: List[int] = []
        self.path_distance: float = float('inf')

    def reset(self, start_city: int):
        """重置蚂蚁状态"""
        self.visited = [start_city]
        self.current_city = start_city
        self.path = [start_city]
        self.path_distance = float('inf')

    def visit_city(self, city: int):
        """访问城市"""
        self.visited.append(city)
        self.current_city = city
        self.path.append(city)

    def finish(self):
        """完成路径构建"""
        self.path.append(self.path[0])  # 回到起点


class AntColonyOptimizer:
    """蚁群优化器"""

    def __init__(self, cities: List[Tuple[float, float]], config: AlgorithmConfig = None):
        """
        初始化蚁群优化器

        Args:
            cities: 城市坐标列表
            config: 算法配置
        """
        self.cities = cities
        self.n_cities = len(cities)

        # 计算距离矩阵
        self.distance_matrix = DistanceCalculator.calculate_distance_matrix(cities)

        # 初始化信息素管理器
        self.pheromone_manager = PheromoneManager(self.n_cities)

        # 算法参数
        self.alpha = AlgorithmConfig.DEFAULT_ALPHA
        self.beta = AlgorithmConfig.DEFAULT_BETA
        self.rho = AlgorithmConfig.DEFAULT_RHO
        self.q = AlgorithmConfig.DEFAULT_Q
        self.ant_count = AlgorithmConfig.DEFAULT_ANT_COUNT
        self.max_iter = AlgorithmConfig.DEFAULT_MAX_ITER

        # 结果记录
        self.best_path: List[int] = []
        self.best_distance: float = float("inf")
        self.iteration_best_distances: List[float] = []
        self.alpha_history: List[float] = []
        self.beta_history: List[float] = []

    def set_params(self, alpha: float = None, beta: float = None,
                   rho: float = None, q: int = None,
                   ant_count: int = None, max_iter: int = None):
        """设置算法参数"""
        if alpha is not None:
            self.alpha = alpha
        if beta is not None:
            self.beta = beta
        if rho is not None:
            self.rho = rho
        if q is not None:
            self.q = q
        if ant_count is not None:
            self.ant_count = ant_count
        if max_iter is not None:
            self.max_iter = max_iter

    def _select_next_city(self, current_city: int, visited: List[int]) -> int:
        """
        轮盘赌选择下一个城市

        Args:
            current_city: 当前城市
            visited: 已访问城市列表

        Returns:
            下一个城市索引
        """
        probabilities = []
        total_weight = 0.0

        for city in range(self.n_cities):
            if city in visited:
                continue

            # 计算权重
            pheromone = self.pheromone_manager.get_pheromone(current_city, city) ** self.alpha
            heuristic = (1.0 / self.distance_matrix[current_city][city]) ** self.beta
            weight = pheromone * heuristic

            probabilities.append((city, weight))
            total_weight += weight

        if total_weight > 0:
            # 轮盘赌选择
            random_value = np.random.random()
            cumulative = 0.0
            for city, weight in probabilities:
                cumulative += weight / total_weight
                if random_value <= cumulative:
                    return city

        # 备选：从未访问城市中随机选择
        unvisited = [city for city in range(self.n_cities) if city not in visited]
        return np.random.choice(unvisited)

    def _construct_path(self) -> List[int]:
        """
        单只蚂蚁构建路径

        Returns:
            构建的路径
        """
        # 随机选择起始城市
        start_city = np.random.randint(self.n_cities)
        ant = Ant(self.n_cities)
        ant.reset(start_city)

        # 逐步访问城市
        while len(ant.visited) < self.n_cities:
            next_city = self._select_next_city(ant.current_city, ant.visited)
            if next_city is None:
                # 备选方案
                for city in range(self.n_cities):
                    if city not in ant.visited:
                        next_city = city
                        break
            ant.visit_city(next_city)

        ant.finish()
        return ant.path

    def _update_adaptive_params(self, iteration: int, use_adaptive: bool = True):
        """
        自适应参数调整

        Args:
            iteration: 当前迭代次数
            use_adaptive: 是否启用自适应
        """
        if not use_adaptive:
            return

        ratio = iteration / self.max_iter

        # alpha从0.8线性增长到2.0
        self.alpha = AlgorithmConfig.ALPHA_MIN + (AlgorithmConfig.ALPHA_MAX - AlgorithmConfig.ALPHA_MIN) * ratio

        # beta从3.5线性减小到1.5
        self.beta = AlgorithmConfig.BETA_MAX - (AlgorithmConfig.BETA_MAX - AlgorithmConfig.BETA_MIN) * ratio

        # 记录参数历史
        self.alpha_history.append(self.alpha)
        self.beta_history.append(self.beta)

    def _update_pheromone(self, all_paths: List[List[int]],
                          all_distances: List[float],
                          elite_count: int):
        """
        精英策略信息素更新

        Args:
            all_paths: 所有蚂蚁的路径
            all_distances: 所有路径的距离
            elite_count: 精英蚂蚁数量
        """
        # 信息素挥发
        self.pheromone_manager.evaporate(self.rho)

        # 按距离排序
        sorted_indices = np.argsort(all_distances)

        # 释放信息素
        for rank, idx in enumerate(sorted_indices):
            path = all_paths[idx]
            distance = all_distances[idx]

            # 基础释放量
            delta = self.q / distance

            # 精英蚂蚁加倍释放
            if rank < elite_count:
                delta *= 2.0

            self.pheromone_manager.deposit(path, delta)

    def run(self, use_adaptive: bool = True) -> AlgorithmResult:
        """
        运行蚁群算法

        Args:
            use_adaptive: 是否启用自适应参数

        Returns:
            算法结果
        """
        start_time = time.time()

        # 重置历史记录
        self.best_path = []
        self.best_distance = float("inf")
        self.iteration_best_distances = []
        self.alpha_history = []
        self.beta_history = []

        # 精英蚂蚁数量
        elite_count = max(1, int(self.ant_count * AlgorithmConfig.DEFAULT_ELITE_RATIO))

        for iteration in range(self.max_iter):
            # 自适应参数调整
            self._update_adaptive_params(iteration, use_adaptive)

            # 蚁群构建路径
            all_paths = []
            all_distances = []

            for _ in range(self.ant_count):
                path = self._construct_path()
                distance = DistanceCalculator.calculate_path_distance(path, self.distance_matrix)
                all_paths.append(path)
                all_distances.append(distance)

            # 更新全局最优解
            min_idx = np.argmin(all_distances)
            if all_distances[min_idx] < self.best_distance:
                self.best_distance = all_distances[min_idx]
                self.best_path = all_paths[min_idx].copy()

            # 信息素更新
            self._update_pheromone(all_paths, all_distances, elite_count)

            # 记录收敛数据
            self.iteration_best_distances.append(self.best_distance)

        running_time = time.time() - start_time

        # 计算收敛迭代次数
        convergence_iteration = self._find_convergence()

        return AlgorithmResult(
            best_path=self.best_path,
            best_distance=self.best_distance,
            running_time=running_time,
            convergence_iteration=convergence_iteration,
            iteration_best_distances=self.iteration_best_distances,
            alpha_history=self.alpha_history,
            beta_history=self.beta_history,
        )

    def _find_convergence(self) -> int:
        """找到收敛迭代次数"""
        for i in range(1, len(self.iteration_best_distances)):
            delta = abs(self.iteration_best_distances[i] - self.iteration_best_distances[i - 1])
            if delta < AlgorithmConfig.CONVERGENCE_THRESHOLD:
                return i
        return len(self.iteration_best_distances)


# =========================
# 遗传算法模块
# =========================

class GeneticOperator:
    """遗传操作算子"""

    @staticmethod
    def order_crossover(parent1: List[int], parent2: List[int],
                        n_cities: int) -> List[int]:
        """
        顺序交叉（OX）

        Args:
            parent1: 父代1
            parent2: 父代2
            n_cities: 城市数量

        Returns:
            子代路径
        """
        size = len(parent1)
        if size <= 3:
            return parent1.copy()

        # 选择交叉点
        start, end = sorted(np.random.choice(range(1, size - 1), 2, replace=False))

        child = [-1] * size
        # 复制parent1的片段
        child[start:end] = parent1[start:end]

        # 从parent2中按顺序填充剩余城市
        remaining = []
        for city in parent2[1:-1]:
            if city not in child[start:end] and city not in remaining:
                remaining.append(city)

        # 填充中间位置
        idx = 0
        for i in range(1, size - 1):
            if child[i] == -1:
                if idx < len(remaining):
                    child[i] = remaining[idx]
                    idx += 1
                else:
                    # 从未使用的城市中选择
                    for city in range(n_cities):
                        if city not in child:
                            child[i] = city
                            break

        # 设置起点和终点相同
        child[0] = parent1[0]
        child[-1] = parent1[0]

        # 验证路径有效性
        if -1 in child or len(set(child[:-1])) != n_cities:
            return parent1.copy()

        return child

    @staticmethod
    def swap_mutation(path: List[int], mutation_rate: float) -> List[int]:
        """
        交换变异

        Args:
            path: 输入路径
            mutation_rate: 变异概率

        Returns:
            变异后的路径
        """
        if np.random.random() < mutation_rate:
            new_path = path.copy()
            n_middle = len(new_path) - 2
            if n_middle < 2:
                return path
            i, j = np.random.choice(range(1, len(new_path) - 1), 2, replace=False)
            new_path[i], new_path[j] = new_path[j], new_path[i]
            return new_path
        return path

    @staticmethod
    def reverse_mutation(path: List[int], mutation_rate: float) -> List[int]:
        """
        逆转变异

        Args:
            path: 输入路径
            mutation_rate: 变异概率

        Returns:
            变异后的路径
        """
        if np.random.random() < mutation_rate:
            new_path = path.copy()
            n_middle = len(new_path) - 2
            if n_middle < 2:
                return path
            i, j = sorted(np.random.choice(range(1, len(new_path) - 1), 2, replace=False))
            new_path[i:j + 1] = reversed(new_path[i:j + 1])
            return new_path
        return path

    @staticmethod
    def tournament_select(paths: List[List[int]], distances: List[float],
                          tournament_size: int = 3) -> List[int]:
        """
        锦标赛选择

        Args:
            paths: 路径列表
            distances: 距离列表
            tournament_size: 锦标赛规模

        Returns:
            选中的路径
        """
        indices = np.random.choice(len(paths), tournament_size, replace=False)
        best_idx = indices[np.argmin([distances[i] for i in indices])]
        return paths[best_idx].copy()


class GeneticEnhancer:
    """遗传算法增强器"""

    def __init__(self, n_cities: int, crossover_rate: float = 0.85,
                 mutation_rate: float = 0.15):
        """
        初始化遗传增强器

        Args:
            n_cities: 城市数量
            crossover_rate: 交叉概率
            mutation_rate: 变异概率
        """
        self.n_cities = n_cities
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.operators = GeneticOperator()
        self.distance_matrix = None  # 需要外部设置

    def set_distance_matrix(self, distance_matrix: np.ndarray):
        """设置距离矩阵"""
        self.distance_matrix = distance_matrix

    def enhance(self, paths: List[List[int]],
                distances: List[float]) -> Tuple[List[List[int]], List[float]]:
        """
        对种群进行遗传增强

        Args:
            paths: 路径列表
            distances: 距离列表

        Returns:
            增强后的路径和距离
        """
        n = len(paths)

        # 按距离排序，保留精英
        sorted_indices = np.argsort(distances)
        n_elite = max(2, n // 4)
        elite_paths = [paths[i].copy() for i in sorted_indices[:n_elite]]
        elite_distances = [distances[i] for i in sorted_indices[:n_elite]]

        # 新种群从精英开始
        new_paths = list(elite_paths)

        # 生成剩余个体
        while len(new_paths) < n:
            # 锦标赛选择两个父代
            p1 = self.operators.tournament_select(elite_paths, elite_distances)
            p2 = self.operators.tournament_select(elite_paths, elite_distances)

            # 交叉
            if np.random.random() < self.crossover_rate:
                child = self.operators.order_crossover(p1, p2, self.n_cities)
            else:
                child = p1.copy()

            # 变异
            if np.random.random() < 0.5:
                child = self.operators.swap_mutation(child, self.mutation_rate)
            else:
                child = self.operators.reverse_mutation(child, self.mutation_rate)

            new_paths.append(child)

        # 计算新种群的距离
        if self.distance_matrix is not None:
            new_distances = [DistanceCalculator.calculate_path_distance(p, self.distance_matrix)
                            for p in new_paths]
        else:
            new_distances = distances[:len(new_paths)]

        return new_paths, new_distances


# =========================
# 2-opt局部搜索模块
# =========================

class TwoOptOptimizer:
    """2-opt局部搜索优化器"""

    def __init__(self, distance_matrix: np.ndarray):
        """
        初始化2-opt优化器

        Args:
            distance_matrix: 距离矩阵
        """
        self.distance_matrix = distance_matrix
        self.n_cities = len(distance_matrix)

    def optimize(self, path: List[int]) -> Tuple[List[int], float]:
        """
        对路径进行2-opt优化

        Args:
            path: 输入路径

        Returns:
            优化后的路径和距离
        """
        improved = True
        best_path = path.copy()
        best_distance = DistanceCalculator.calculate_path_distance(best_path, self.distance_matrix)

        if best_distance == float('inf'):
            return path, float('inf')

        while improved:
            improved = False
            for i in range(1, len(best_path) - 2):
                for j in range(i + 1, len(best_path) - 1):
                    # 索引有效性检查
                    if (best_path[i - 1] >= self.n_cities or best_path[i] >= self.n_cities or
                            best_path[j] >= self.n_cities or best_path[j + 1] >= self.n_cities):
                        continue

                    # 计算距离变化
                    delta = DistanceCalculator.calculate_2opt_delta(
                        self.distance_matrix, best_path, i, j
                    )

                    if delta < -1e-10:
                        # 执行2-opt交换
                        best_path[i:j + 1] = reversed(best_path[i:j + 1])
                        best_distance += delta
                        improved = True

        return best_path, best_distance


# =========================
# 混合蚁群算法
# =========================

class HybridACOGA:
    """
    混合蚁群算法 + 遗传算法
    包含：自适应参数、精英策略、2-opt局部搜索
    """

    def __init__(self, cities: List[Tuple[float, float]],
                 ant_count: int = 50, alpha: float = 1.0, beta: float = 2.0,
                 rho: float = 0.5, q: int = 100, max_iter: int = 1000,
                 crossover_rate: float = 0.85, mutation_rate: float = 0.15,
                 elite_ratio: float = 0.1, use_2opt: bool = True,
                 use_ga: bool = True, adaptive_params: bool = True):
        """
        初始化混合算法

        Args:
            cities: 城市坐标列表
            ant_count: 蚁群规模
            alpha: 信息素因子（初始值）
            beta: 启发函数因子（初始值）
            rho: 信息素挥发率
            q: 信息素常数
            max_iter: 最大迭代次数
            crossover_rate: 交叉概率
            mutation_rate: 变异概率
            elite_ratio: 精英比例
            use_2opt: 是否使用2-opt
            use_ga: 是否使用遗传算法
            adaptive_params: 是否使用自适应参数
        """
        self.cities = cities
        self.n_cities = len(cities)

        # 蚁群参数
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.ant_count = ant_count
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

        # 初始化组件
        self.distance_matrix = DistanceCalculator.calculate_distance_matrix(cities)
        self.pheromone_manager = PheromoneManager(self.n_cities)
        self.genetic_enhancer = GeneticEnhancer(
            self.n_cities, crossover_rate, mutation_rate
        )
        self.genetic_enhancer.set_distance_matrix(self.distance_matrix)
        self.two_opt_optimizer = TwoOptOptimizer(self.distance_matrix)

        # 结果记录
        self.best_path: List[int] = []
        self.best_distance: float = float("inf")
        self.iteration_best_distances: List[float] = []
        self.alpha_history: List[float] = []
        self.beta_history: List[float] = []

    def _select_next_city(self, current_city: int, visited: List[int]) -> int:
        """轮盘赌选择下一个城市"""
        probabilities = []
        total_weight = 0.0

        for city in range(self.n_cities):
            if city in visited:
                continue
            pheromone = self.pheromone_manager.get_pheromone(current_city, city) ** self.alpha
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

    def _construct_path(self) -> List[int]:
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

    def _update_adaptive_params(self, iteration: int):
        """自适应参数调整"""
        if not self.adaptive_params:
            return

        ratio = iteration / self.max_iter
        self.alpha = AlgorithmConfig.ALPHA_MIN + (AlgorithmConfig.ALPHA_MAX - AlgorithmConfig.ALPHA_MIN) * ratio
        self.beta = AlgorithmConfig.BETA_MAX - (AlgorithmConfig.BETA_MAX - AlgorithmConfig.BETA_MIN) * ratio

        self.alpha_history.append(self.alpha)
        self.beta_history.append(self.beta)

    def run(self) -> AlgorithmResult:
        """运行混合算法"""
        start_time = time.time()

        # 重置历史记录
        self.best_path = []
        self.best_distance = float("inf")
        self.iteration_best_distances = []
        self.alpha_history = []
        self.beta_history = []

        for iteration in range(self.max_iter):
            # 1. 自适应参数调整
            self._update_adaptive_params(iteration)

            # 2. 蚁群构建路径
            all_paths = []
            all_distances = []

            for _ in range(self.ant_count):
                path = self._construct_path()
                distance = DistanceCalculator.calculate_path_distance(path, self.distance_matrix)
                all_paths.append(path)
                all_distances.append(distance)

            # 3. 遗传算法增强（可选）
            if self.use_ga:
                all_paths, all_distances = self.genetic_enhancer.enhance(all_paths, all_distances)
                # 重新计算距离
                all_distances = [DistanceCalculator.calculate_path_distance(p, self.distance_matrix)
                                 for p in all_paths]

            # 4. 局部搜索优化精英个体（可选）
            if self.use_2opt:
                sorted_indices = np.argsort(all_distances)
                for i in range(min(self.elite_count, len(all_paths))):
                    idx = sorted_indices[i]
                    improved_path, improved_distance = self.two_opt_optimizer.optimize(all_paths[idx])
                    if improved_distance < all_distances[idx]:
                        all_paths[idx] = improved_path
                        all_distances[idx] = improved_distance

            # 5. 更新全局最优解
            min_idx = np.argmin(all_distances)
            if all_distances[min_idx] < self.best_distance:
                self.best_distance = all_distances[min_idx]
                self.best_path = all_paths[min_idx].copy()

            # 6. 精英信息素更新
            self.pheromone_manager.evaporate(self.rho)
            sorted_indices = np.argsort(all_distances)
            for rank, idx in enumerate(sorted_indices):
                path = all_paths[idx]
                distance = all_distances[idx]
                delta = self.q / distance
                if rank < self.elite_count:
                    delta *= 2.0
                self.pheromone_manager.deposit(path, delta)

            # 7. 记录收敛数据
            self.iteration_best_distances.append(self.best_distance)

        running_time = time.time() - start_time
        convergence_iteration = self._find_convergence()

        return AlgorithmResult(
            best_path=self.best_path,
            best_distance=self.best_distance,
            running_time=running_time,
            convergence_iteration=convergence_iteration,
            iteration_best_distances=self.iteration_best_distances,
            alpha_history=self.alpha_history,
            beta_history=self.beta_history,
        )

    def _find_convergence(self) -> int:
        """找到收敛迭代次数"""
        for i in range(1, len(self.iteration_best_distances)):
            delta = abs(self.iteration_best_distances[i] - self.iteration_best_distances[i - 1])
            if delta < AlgorithmConfig.CONVERGENCE_THRESHOLD:
                return i
        return len(self.iteration_best_distances)


# =========================
# 可视化模块
# =========================

class PlotManager:
    """图表管理器"""

    @staticmethod
    def setup_plot_widget(plot_widget: pg.PlotWidget, title: str,
                          x_label: str, y_label: str):
        """设置图表控件"""
        plot_widget.setBackground(VisualizationConfig.BACKGROUND_COLOR)
        plot_widget.showGrid(x=True, y=True, alpha=VisualizationConfig.GRID_ALPHA)
        plot_widget.setLabel('bottom', x_label)
        plot_widget.setLabel('left', y_label)
        plot_widget.setTitle(title)

    @staticmethod
    def plot_cities(plot_widget: pg.PlotWidget,
                    cities: List[Tuple[float, float]]):
        """
        绘制城市分布图

        Args:
            plot_widget: 图表控件
            cities: 城市坐标列表
        """
        plot_widget.clear()

        if not cities:
            return

        x = [city[0] for city in cities]
        y = [city[1] for city in cities]

        # 绘制城市点
        plot_widget.plot(x, y, pen=None, symbol='o',
                        symbolSize=VisualizationConfig.SYMBOL_SIZE,
                        symbolBrush=VisualizationConfig.CITY_COLOR,
                        symbolPen='k')

        PlotManager.setup_plot_widget(
            plot_widget,
            f"城市分布图（共 {len(cities)} 个城市）",
            "X 坐标", "Y 坐标"
        )

    @staticmethod
    def plot_path(plot_widget: pg.PlotWidget,
                  cities: List[Tuple[float, float]],
                  path: List[int], distance: float):
        """
        绘制最优路径图

        Args:
            plot_widget: 图表控件
            cities: 城市坐标列表
            path: 最优路径
            distance: 最优距离
        """
        plot_widget.clear()

        if not path or not cities:
            return

        # 提取路径坐标
        x = [cities[city][0] for city in path]
        y = [cities[city][1] for city in path]

        # 绘制路径线
        pen = pg.mkPen(color=VisualizationConfig.PATH_COLOR,
                       width=VisualizationConfig.PATH_WIDTH)
        plot_widget.plot(x, y, pen=pen)

        # 绘制城市点
        city_x = [cities[city][0] for city in path[:-1]]
        city_y = [cities[city][1] for city in path[:-1]]
        plot_widget.plot(city_x, city_y, pen=None, symbol='o',
                        symbolSize=VisualizationConfig.SYMBOL_SIZE,
                        symbolBrush=VisualizationConfig.CITY_COLOR,
                        symbolPen='k')

        PlotManager.setup_plot_widget(
            plot_widget,
            f"最优路径（距离: {distance:.2f}）",
            "X 坐标", "Y 坐标"
        )

    @staticmethod
    def plot_convergence(plot_widget: pg.PlotWidget,
                         iteration_distances: List[float],
                         show_labels: bool = True):
        """
        绘制收敛曲线

        Args:
            plot_widget: 图表控件
            iteration_distances: 每次迭代的最优距离
            show_labels: 是否显示下降点标签
        """
        plot_widget.clear()

        if not iteration_distances:
            return

        iterations = list(range(len(iteration_distances)))

        # 绘制收敛曲线
        pen = pg.mkPen(color=VisualizationConfig.CONVERGENCE_COLOR,
                       width=VisualizationConfig.PATH_WIDTH)
        plot_widget.plot(iterations, iteration_distances, pen=pen)

        # 在距离下降的点上显示坐标
        if show_labels:
            for i in range(1, len(iteration_distances)):
                if iteration_distances[i] < iteration_distances[i - 1]:
                    text = pg.TextItem(
                        f"({i},{iteration_distances[i]:.0f})",
                        color=VisualizationConfig.HIGHLIGHT_COLOR,
                        anchor=(0.5, 1)
                    )
                    text.setPos(i, iteration_distances[i])
                    plot_widget.addItem(text)

        PlotManager.setup_plot_widget(
            plot_widget,
            "收敛过程",
            "迭代次数", "最优距离"
        )

    @staticmethod
    def plot_empty_convergence(plot_widget: pg.PlotWidget):
        """绘制空的收敛图（等待状态）"""
        plot_widget.clear()
        text = pg.TextItem("点击\"运行算法\"\n开始求解",
                          color=(150, 150, 150))
        text.setPos(0.5, 0.5)
        plot_widget.addItem(text)
        PlotManager.setup_plot_widget(plot_widget, "收敛过程", "迭代次数", "最优距离")


# =========================
# 结果导出模块
# =========================

class ResultExporter:
    """结果导出器"""

    @staticmethod
    def to_json(result: AlgorithmResult, filepath: str):
        """导出为JSON文件"""
        data = result.to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def to_text(result: AlgorithmResult, filepath: str):
        """导出为文本文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=== 混合蚁群算法求解结果 ===\n\n")
            f.write(f"最优距离: {result.best_distance:.2f}\n")
            f.write(f"运行时间: {result.running_time:.2f} 秒\n")
            f.write(f"收敛迭代: 第 {result.convergence_iteration} 次\n")
            f.write(f"首次迭代距离: {result.first_iteration_distance:.2f}\n")
            f.write(f"最后下降迭代: 第 {result.last_decrease_iteration} 次\n")
            f.write(f"距离下降次数: {result.total_decrease_count} 次\n")
            f.write(f"\n最优路径: {result.best_path}\n")

    @staticmethod
    def to_csv(result: AlgorithmResult, filepath: str):
        """导出为CSV文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("迭代次数,最优距离\n")
            for i, dist in enumerate(result.iteration_best_distances):
                f.write(f"{i},{dist:.4f}\n")

    @staticmethod
    def format_result_text(result: AlgorithmResult, config_str: str) -> str:
        """格式化结果文本"""
        text = "=== 求解结果 ===\n"
        text += f"算法配置: {config_str}\n\n"
        text += f"最优距离: {result.best_distance:.2f}\n"
        text += f"运行时间: {result.running_time:.2f} 秒\n"
        text += f"收敛迭代: 第 {result.convergence_iteration} 次\n"
        text += f"首次迭代距离: {result.first_iteration_distance:.2f}\n"
        text += f"最后下降迭代: 第 {result.last_decrease_iteration} 次\n"
        return text


# =========================
# 参数预设模块
# =========================

class ParameterPreset:
    """参数预设"""

    PRESETS = {
        "默认配置": {
            "ant_count": 50,
            "alpha": 1.0,
            "beta": 2.0,
            "rho": 0.5,
            "q": 100,
            "max_iter": 100,
            "crossover_rate": 0.85,
            "mutation_rate": 0.15,
            "elite_ratio": 0.1,
            "use_ga": True,
            "use_2opt": True,
            "adaptive_params": True,
        },
        "快速求解": {
            "ant_count": 20,
            "alpha": 1.0,
            "beta": 2.0,
            "rho": 0.5,
            "q": 100,
            "max_iter": 50,
            "crossover_rate": 0.8,
            "mutation_rate": 0.2,
            "elite_ratio": 0.1,
            "use_ga": False,
            "use_2opt": False,
            "adaptive_params": False,
        },
        "高精度求解": {
            "ant_count": 100,
            "alpha": 1.0,
            "beta": 2.5,
            "rho": 0.3,
            "q": 150,
            "max_iter": 200,
            "crossover_rate": 0.9,
            "mutation_rate": 0.1,
            "elite_ratio": 0.15,
            "use_ga": True,
            "use_2opt": True,
            "adaptive_params": True,
        },
        "传统ACO": {
            "ant_count": 50,
            "alpha": 1.0,
            "beta": 2.0,
            "rho": 0.5,
            "q": 100,
            "max_iter": 100,
            "crossover_rate": 0.85,
            "mutation_rate": 0.15,
            "elite_ratio": 0.1,
            "use_ga": False,
            "use_2opt": False,
            "adaptive_params": False,
        },
        "ACO + 自适应": {
            "ant_count": 50,
            "alpha": 1.0,
            "beta": 2.0,
            "rho": 0.5,
            "q": 100,
            "max_iter": 100,
            "crossover_rate": 0.85,
            "mutation_rate": 0.15,
            "elite_ratio": 0.1,
            "use_ga": False,
            "use_2opt": False,
            "adaptive_params": True,
        },
        "ACO + 遗传算法": {
            "ant_count": 50,
            "alpha": 1.0,
            "beta": 2.0,
            "rho": 0.5,
            "q": 100,
            "max_iter": 100,
            "crossover_rate": 0.85,
            "mutation_rate": 0.15,
            "elite_ratio": 0.1,
            "use_ga": True,
            "use_2opt": False,
            "adaptive_params": False,
        },
        "ACO + 2-opt": {
            "ant_count": 50,
            "alpha": 1.0,
            "beta": 2.0,
            "rho": 0.5,
            "q": 100,
            "max_iter": 100,
            "crossover_rate": 0.85,
            "mutation_rate": 0.15,
            "elite_ratio": 0.1,
            "use_ga": False,
            "use_2opt": True,
            "adaptive_params": False,
        },
    }

    @classmethod
    def get_preset_names(cls) -> List[str]:
        """获取所有预设名称"""
        return list(cls.PRESETS.keys())

    @classmethod
    def get_preset(cls, name: str) -> Dict[str, Any]:
        """获取预设配置"""
        return cls.PRESETS.get(name, cls.PRESETS["默认配置"])

    @classmethod
    def add_preset(cls, name: str, params: Dict[str, Any]):
        """添加新预设"""
        cls.PRESETS[name] = params


# =========================
# 性能分析模块
# =========================

class PerformanceAnalyzer:
    """性能分析器"""

    @staticmethod
    def calculate_statistics(distances: List[float]) -> Dict[str, float]:
        """计算统计指标"""
        if not distances:
            return {}

        distances_array = np.array(distances)
        return {
            "mean": np.mean(distances_array),
            "std": np.std(distances_array),
            "min": np.min(distances_array),
            "max": np.max(distances_array),
            "median": np.median(distances_array),
        }

    @staticmethod
    def calculate_convergence_speed(iteration_distances: List[float]) -> float:
        """计算收敛速度（距离下降率）"""
        if len(iteration_distances) < 2:
            return 0.0

        initial = iteration_distances[0]
        final = iteration_distances[-1]

        if initial == 0:
            return 0.0

        return (initial - final) / initial * 100

    @staticmethod
    def find_best_iteration(iteration_distances: List[float]) -> int:
        """找到最优解出现的迭代次数"""
        if not iteration_distances:
            return -1

        min_distance = min(iteration_distances)
        return iteration_distances.index(min_distance)

    @staticmethod
    def analyze_stagnation(iteration_distances: List[float],
                           threshold: float = 0.01) -> Dict[str, Any]:
        """分析停滞情况"""
        if len(iteration_distances) < 2:
            return {"stagnation_count": 0, "stagnation_length": 0}

        stagnation_count = 0
        max_stagnation_length = 0
        current_stagnation = 0

        for i in range(1, len(iteration_distances)):
            delta = abs(iteration_distances[i] - iteration_distances[i - 1])
            if delta < threshold:
                current_stagnation += 1
                stagnation_count += 1
            else:
                max_stagnation_length = max(max_stagnation_length, current_stagnation)
                current_stagnation = 0

        max_stagnation_length = max(max_stagnation_length, current_stagnation)

        return {
            "stagnation_count": stagnation_count,
            "max_stagnation_length": max_stagnation_length,
        }

    @staticmethod
    def compare_results(results: List[AlgorithmResult],
                        names: List[str]) -> str:
        """比较多个算法结果"""
        if not results or not names:
            return "无结果可比较"

        text = "=== 算法对比 ===\n\n"
        text += f"{'算法名称':<20} {'最优距离':<12} {'运行时间':<12} {'收敛迭代':<10}\n"
        text += "-" * 56 + "\n"

        for result, name in zip(results, names):
            text += f"{name:<20} {result.best_distance:<12.2f} "
            text += f"{result.running_time:<12.2f} {result.convergence_iteration:<10}\n"

        # 找出最优结果
        best_idx = np.argmin([r.best_distance for r in results])
        text += f"\n最优算法: {names[best_idx]}\n"

        return text


# =========================
# 验证和测试模块
# =========================

class AlgorithmValidator:
    """算法验证器"""

    @staticmethod
    def validate_path(path: List[int], n_cities: int) -> bool:
        """验证路径有效性"""
        if not path:
            return False

        # 检查起点和终点是否相同
        if path[0] != path[-1]:
            return False

        # 检查是否访问了所有城市
        unique_cities = set(path[:-1])
        if len(unique_cities) != n_cities:
            return False

        # 检查是否有重复城市
        if len(path) - 1 != n_cities:
            return False

        return True

    @staticmethod
    def validate_distance(distance: float, distance_matrix: np.ndarray,
                          path: List[int]) -> bool:
        """验证距离计算"""
        calculated = DistanceCalculator.calculate_path_distance(path, distance_matrix)
        return abs(distance - calculated) < 1e-6

    @staticmethod
    def run_benchmark(cities: List[Tuple[float, float]],
                      n_runs: int = 10, **kwargs) -> Dict[str, Any]:
        """运行基准测试"""
        results = []

        for i in range(n_runs):
            solver = HybridACOGA(cities, **kwargs)
            result = solver.run()
            results.append(result)

        # 统计结果
        distances = [r.best_distance for r in results]
        times = [r.running_time for r in results]

        return {
            "n_runs": n_runs,
            "mean_distance": np.mean(distances),
            "std_distance": np.std(distances),
            "min_distance": np.min(distances),
            "max_distance": np.max(distances),
            "mean_time": np.mean(times),
            "std_time": np.std(times),
            "best_result": results[np.argmin(distances)],
        }

    @staticmethod
    def test_convergence(cities: List[Tuple[float, float]],
                         max_iter: int = 200) -> Dict[str, Any]:
        """测试收敛性能"""
        solver = HybridACOGA(cities, max_iter=max_iter)
        result = solver.run()

        # 分析收敛情况
        stagnation_info = PerformanceAnalyzer.analyze_stagnation(
            result.iteration_best_distances
        )

        convergence_speed = PerformanceAnalyzer.calculate_convergence_speed(
            result.iteration_best_distances
        )

        best_iteration = PerformanceAnalyzer.find_best_iteration(
            result.iteration_best_distances
        )

        return {
            "result": result,
            "convergence_speed": convergence_speed,
            "best_iteration": best_iteration,
            "stagnation_info": stagnation_info,
        }

    @staticmethod
    def compare_with_optimal(cities: List[Tuple[float, float]],
                             optimal_distance: float) -> Dict[str, Any]:
        """与已知最优解比较"""
        solver = HybridACOGA(cities)
        result = solver.run()

        gap = (result.best_distance - optimal_distance) / optimal_distance * 100

        return {
            "result": result,
            "optimal_distance": optimal_distance,
            "gap_percent": gap,
            "is_optimal": abs(result.best_distance - optimal_distance) < 1e-6,
        }


# =========================
# TSP测试实例库
# =========================

class TSPLibLoader:
    """TSP测试实例加载器"""

    @staticmethod
    def generate_instance(n_cities: int, instance_type: str = "random") -> List[Tuple[float, float]]:
        """
        生成TSP测试实例

        Args:
            n_cities: 城市数量
            instance_type: 实例类型 (random, clustered, grid, circle)

        Returns:
            城市坐标列表
        """
        if instance_type == "random":
            return CityGenerator.generate_random(n_cities)
        elif instance_type == "clustered":
            return CityGenerator.generate_clustered(n_cities)
        elif instance_type == "grid":
            return CityGenerator.generate_grid(n_cities)
        elif instance_type == "circle":
            return TSPLibLoader._generate_circle(n_cities)
        else:
            return CityGenerator.generate_random(n_cities)

    @staticmethod
    def _generate_circle(n_cities: int, radius: float = 50.0) -> List[Tuple[float, float]]:
        """生成圆形分布的城市"""
        cities = []
        for i in range(n_cities):
            angle = 2 * np.pi * i / n_cities
            x = radius * np.cos(angle) + radius
            y = radius * np.sin(angle) + radius
            cities.append((x, y))
        return cities

    @staticmethod
    def get_known_optimal(n_cities: int) -> Optional[float]:
        """获取已知最优解（如果有的话）"""
        # 一些经典TSP实例的最优解
        known_optimals = {
            10: 2.69,
            20: 3.75,
            30: 4.57,
            50: 5.69,
        }
        return known_optimals.get(n_cities)


# =========================
# 调度和执行模块
# =========================

class ExperimentRunner:
    """实验运行器"""

    def __init__(self, cities: List[Tuple[float, float]]):
        self.cities = cities
        self.results: List[AlgorithmResult] = []
        self.names: List[str] = []

    def run_single(self, name: str, **kwargs) -> AlgorithmResult:
        """运行单个实验"""
        solver = HybridACOGA(self.cities, **kwargs)
        result = solver.run()
        self.results.append(result)
        self.names.append(name)
        return result

    def run_comparison(self) -> str:
        """运行对比实验"""
        # 传统ACO
        self.run_single("传统ACO", use_ga=False, use_2opt=False, adaptive_params=False)

        # ACO + 自适应
        self.run_single("ACO + 自适应", use_ga=False, use_2opt=False, adaptive_params=True)

        # ACO + 遗传算法
        self.run_single("ACO + 遗传算法", use_ga=True, use_2opt=False, adaptive_params=False)

        # ACO + 2-opt
        self.run_single("ACO + 2-opt", use_ga=False, use_2opt=True, adaptive_params=False)

        # 混合算法
        self.run_single("混合算法", use_ga=True, use_2opt=True, adaptive_params=True)

        return PerformanceAnalyzer.compare_results(self.results, self.names)

    def run_parameter_test(self, param_name: str, values: List[Any]) -> str:
        """运行参数测试"""
        self.results.clear()
        self.names.clear()

        for value in values:
            kwargs = {param_name: value}
            name = f"{param_name}={value}"
            self.run_single(name, **kwargs)

        return PerformanceAnalyzer.compare_results(self.results, self.names)

    def get_best_result(self) -> Tuple[str, AlgorithmResult]:
        """获取最优结果"""
        if not self.results:
            return None, None

        best_idx = np.argmin([r.best_distance for r in self.results])
        return self.names[best_idx], self.results[best_idx]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.results:
            return {}

        distances = [r.best_distance for r in self.results]
        times = [r.running_time for r in self.results]

        return {
            "n_experiments": len(self.results),
            "mean_distance": np.mean(distances),
            "std_distance": np.std(distances),
            "min_distance": np.min(distances),
            "max_distance": np.max(distances),
            "mean_time": np.mean(times),
            "std_time": np.std(times),
        }

    def export_all_results(self, filepath: str):
        """导出所有实验结果"""
        data = {
            "experiments": []
        }

        for name, result in zip(self.names, self.results):
            experiment_data = {
                "name": name,
                "result": result.to_dict(),
                "best_path": result.best_path,
                "iteration_distances": result.iteration_best_distances,
            }
            data["experiments"].append(experiment_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# =========================
# PyQt5 图形用户界面
# =========================

class HybridACOGUI(QMainWindow):
    """混合蚁群算法GUI"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("混合蚁群算法求解 TSP 问题")
        self.setGeometry(100, 50, 1200, 800)

        self.cities = None
        self.last_result = None  # 保存上次的求解结果

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
        self.path_plot = pg.PlotWidget()
        PlotManager.setup_plot_widget(self.path_plot, "城市分布图", "X 坐标", "Y 坐标")

        # 右图 - 收敛曲线
        self.convergence_plot = pg.PlotWidget()
        PlotManager.setup_plot_widget(self.convergence_plot, "收敛过程", "迭代次数", "最优距离")

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

        # 导出按钮
        row += 1
        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("导出结果")
        self.export_btn.clicked.connect(self.export_result)
        export_layout.addWidget(self.export_btn)

        self.compare_btn = QPushButton("算法对比")
        self.compare_btn.clicked.connect(self.compare_algorithms)
        export_layout.addWidget(self.compare_btn)
        params_layout.addLayout(export_layout, row, 0, 1, 2)

        bottom_layout.addWidget(params_group, stretch=1)

        # 右侧 - 求解结果
        result_group = QGroupBox("求解结果")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)

        bottom_layout.addWidget(result_group, stretch=1)

        main_layout.addLayout(bottom_layout, stretch=1)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def generate_map(self):
        """生成地图"""
        try:
            n_cities = self.n_cities_spin.value()
            self.cities = CityGenerator.generate_random(n_cities)

            self.result_text.clear()
            self.result_text.append(f"已生成 {n_cities} 个城市的地图。")
            self.result_text.append('点击"运行算法"开始求解。')

            PlotManager.plot_cities(self.path_plot, self.cities)
            PlotManager.plot_empty_convergence(self.convergence_plot)

            self.statusBar().showMessage(f"已生成 {n_cities} 个城市")

        except Exception as exc:
            QMessageBox.critical(self, "错误", f"生成地图失败: {exc}")

    def run_algorithm(self):
        """运行算法"""
        try:
            if self.cities is None:
                QMessageBox.warning(self, "警告", "请先生成地图！")
                return

            # 获取参数
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

            # 构建配置字符串
            algo_config = []
            if params["adaptive_params"]:
                algo_config.append("自适应参数")
            if params["use_ga"]:
                algo_config.append("遗传算法")
            if params["use_2opt"]:
                algo_config.append("2-opt")
            config_str = " + ".join(algo_config) if algo_config else "传统ACO"

            self.result_text.clear()
            self.result_text.append(f"=== 算法配置 ===")
            self.result_text.append(f"算法: {config_str}")
            self.result_text.append(f"城市数: {params['n_cities']}, 蚂蚁数: {params['ant_count']}")
            self.result_text.append(f"\n开始求解...")
            self.statusBar().showMessage("正在求解...")
            QApplication.processEvents()

            # 创建并运行算法
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
            self.last_result = results  # 保存结果用于导出

            # 显示结果
            self.result_text.clear()
            self.result_text.append(ResultExporter.format_result_text(results, config_str))

            if params["adaptive_params"]:
                self.result_text.append(f"\n自适应参数范围:")
                self.result_text.append(f"  alpha: {params['alpha']:.1f} → {solver.alpha:.2f}")
                self.result_text.append(f"  beta: {params['beta']:.1f} → {solver.beta:.2f}")

            # 绘制结果
            PlotManager.plot_path(self.path_plot, self.cities,
                                  results.best_path, results.best_distance)
            PlotManager.plot_convergence(self.convergence_plot,
                                        results.iteration_best_distances)

            self.statusBar().showMessage(f"求解完成！最优距离: {results.best_distance:.2f}")

        except Exception as exc:
            QMessageBox.critical(self, "错误", f"运行失败: {exc}")
            self.statusBar().showMessage("求解失败")

    def export_result(self):
        """导出求解结果"""
        if self.last_result is None:
            QMessageBox.warning(self, "警告", "请先运行算法！")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出结果", "result.json",
            "JSON文件 (*.json);;文本文件 (*.txt);;CSV文件 (*.csv)"
        )

        if not filepath:
            return

        try:
            if filepath.endswith('.json'):
                ResultExporter.to_json(self.last_result, filepath)
            elif filepath.endswith('.csv'):
                ResultExporter.to_csv(self.last_result, filepath)
            else:
                ResultExporter.to_text(self.last_result, filepath)

            self.statusBar().showMessage(f"结果已导出到: {filepath}")
            QMessageBox.information(self, "成功", f"结果已导出到:\n{filepath}")

        except Exception as exc:
            QMessageBox.critical(self, "错误", f"导出失败: {exc}")

    def compare_algorithms(self):
        """算法对比"""
        if self.cities is None:
            QMessageBox.warning(self, "警告", "请先生成地图！")
            return

        self.result_text.clear()
        self.result_text.append("=== 算法对比 ===\n")
        self.result_text.append("正在运行对比实验...\n")
        self.statusBar().showMessage("正在运行对比实验...")
        QApplication.processEvents()

        # 定义要对比的算法配置
        configs = [
            ("传统ACO", {"use_ga": False, "use_2opt": False, "adaptive_params": False}),
            ("ACO + 自适应", {"use_ga": False, "use_2opt": False, "adaptive_params": True}),
            ("ACO + 遗传算法", {"use_ga": True, "use_2opt": False, "adaptive_params": False}),
            ("ACO + 2-opt", {"use_ga": False, "use_2opt": True, "adaptive_params": False}),
            ("混合算法", {"use_ga": True, "use_2opt": True, "adaptive_params": True}),
        ]

        results = []
        names = []

        for name, config in configs:
            self.result_text.append(f"运行 {name}...")
            QApplication.processEvents()

            solver = HybridACOGA(
                cities=self.cities,
                ant_count=self.ant_count_spin.value(),
                alpha=self.alpha_spin.value(),
                beta=self.beta_spin.value(),
                rho=self.rho_spin.value(),
                q=self.q_spin.value(),
                max_iter=self.max_iter_spin.value(),
                **config
            )

            result = solver.run()
            results.append(result)
            names.append(name)

            self.result_text.append(f"  完成！距离: {result.best_distance:.2f}\n")

        # 显示对比结果
        comparison_text = PerformanceAnalyzer.compare_results(results, names)
        self.result_text.append(comparison_text)

        self.statusBar().showMessage("对比实验完成！")


# =========================
# 程序入口
# =========================

def main():
    """主函数"""
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
        QStatusBar {
            font-weight: bold;
        }
    """)

    window = HybridACOGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
