# 基于蚁群算法的旅行商问题求解系统

## 1. 项目概述

本项目是一个基于**蚁群算法（Ant Colony Optimization, ACO）**求解**旅行商问题（Traveling Salesman Problem, TSP）**的 Python 实现，并配有图形用户界面（GUI）用于交互式参数设置与结果可视化。

**旅行商问题**：给定 n 个城市及两两之间的距离，寻找一条从某城市出发，经过所有城市恰好一次后返回起点的最短回路。TSP 是组合优化领域的经典 NP-hard 问题，具有重要的理论研究和实际应用价值。

**蚁群算法**：一种模拟自然界蚂蚁觅食行为的元启发式优化算法。蚂蚁在路径上释放信息素，后续蚂蚁倾向于选择信息素浓度高的路径；同时信息素会随时间挥发，较短路径因被更多蚂蚁访问而获得更强的信息素积累，最终收敛至（近似）最优解。

---

## 2. 功能特性

| 功能 | 描述 |
|------|------|
| 算法核心 | 蚁群算法求解 TSP，支持轮盘赌选择策略 |
| 参数可调 | 城市数量、蚁群规模、信息素因子、启发函数因子、挥发因子、信息素常数、最大迭代次数 |
| 地图生成 | 支持独立生成城市分布图，运行算法时可复用已有地图 |
| 结果展示 | 实时显示最优距离、运行时间、收敛迭代次数 |
| 可视化 | 左侧显示最优路径图，右侧显示算法收敛曲线 |
| 随机实例 | 支持在指定区域内随机生成城市坐标 |
| 中文界面 | GUI 完全中文化，支持中文显示 |
| 单文件设计 | 地图生成、算法核心、可视化、GUI 与文档导出统一收纳在 `main.py` 中，便于交付与维护 |

---

## 3. 技术栈

- **Python 3**
- **NumPy** — 数值计算与矩阵运算
- **Matplotlib** — 数据可视化（路径图 + 收敛图）
- **Tkinter** — 原生 GUI 界面

---

## 4. 算法原理

### 4.1 距离矩阵

对于 n 个城市，计算欧几里得距离矩阵 $D$，其中 $D_{ij}$ 表示城市 i 到城市 j 的直线距离：

$$D_{ij} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}$$

### 4.2 状态转移规则

蚂蚁 $k$ 位于城市 $i$ 时，选择下一个未访问城市 $j$ 的概率为：

$$P_{ij}^k = \frac{[\tau_{ij}]^\alpha \cdot [\eta_{ij}]^\beta}{\sum_{s \in \text{allow}_k} [\tau_{is}]^\alpha \cdot [\eta_{is}]^\beta}$$

其中：
- $\tau_{ij}$：城市 i 到 j 的信息素浓度
- $\eta_{ij} = 1/D_{ij}$：启发函数（距离的倒数）
- $\alpha$：信息素因子，控制信息素的重要性
- $\beta$：启发函数因子，控制距离的重要性
- $\text{allow}_k$：蚂蚁 $k$ 尚未访问的城市集合

### 4.3 信息素更新

每次迭代后，所有路径上的信息素先挥发，再根据蚂蚁走过的路径强化：

**挥发**：

$$\tau_{ij} = (1 - \rho) \cdot \tau_{ij}$$

**强化**：

$$\tau_{ij} = \tau_{ij} + \sum_{k} \frac{Q}{L_k}$$

其中：
- $\rho$：信息素挥发因子（0 < $\rho$ < 1）
- $Q$：信息素常数
- $L_k$：蚂蚁 $k$ 在本次迭代中走过的路径总长度

### 4.4 算法流程

```
1. 初始化：设置参数，计算距离矩阵，初始化信息素矩阵
2. 迭代（最多 max_iter 次）：
   a. 每只蚂蚁从随机城市出发
   b. 根据概率选择下一个未访问城市，直到遍历所有城市
   c. 回到起点，计算路径长度
   d. 更新全局最优解
   e. 更新信息素矩阵（挥发 + 强化）
3. 输出最优路径、最短距离、运行时间、收敛迭代数
```

---

## 5. 项目文件结构

```text
毕业设计/
├── main.py                        # 单文件主程序（GUI、ACO、绘图、Markdown 转 DOCX）
├── Graduation Project.md          # 本文档
├── Graduation Project.pu          # 英文版系统流程图（PlantUML）
├── Graduation Project chinese.pu  # 中文版系统流程图（PlantUML）
└── 毕业设计说明书.md                # 论文说明文档
```

### 模块职责说明

| 文件 | 职责 | 依赖 |
|------|------|------|
| `main.py` | 单文件主程序，内部包含城市生成、蚁群求解、绘图辅助、GUI 界面与 Markdown 转 DOCX 入口 | `tkinter`, `numpy`, `matplotlib`, `python-docx`, `time`, `re`, `argparse` |
| `Graduation Project.pu` | 英文流程图源码，描述 `main.py` 的 GUI 与 `--docx` 双入口流程 | PlantUML |
| `Graduation Project chinese.pu` | 中文流程图源码，内容与英文版一致 | PlantUML |

---

## 6. 安装与运行

### 6.1 环境要求

- Python 3.7+
- NumPy
- Matplotlib

### 6.2 安装依赖

```bash
pip install numpy matplotlib
```

> Tkinter 通常为 Python 标准库，无需额外安装。

### 6.3 运行程序

```bash
python main.py
```

程序将启动一个 GUI 窗口。

---

## 7. 使用说明

### 7.1 界面布局

| 区域 | 说明 |
|------|------|
| 左侧（参数设置） | 输入算法各项参数 |
| 左侧（按钮） | "生成地图"、"运行算法" |
| 左侧（结果） | 显示最优距离、运行时间、收敛迭代次数 |
| 右侧（可视化结果） | 左图：城市分布 / 最优路径连线图；右图：迭代收敛曲线 |

### 7.2 参数设置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 城市数量 | 50 | 随机生成的城市个数（≥2） |
| 蚁群规模 | 50 | 每轮迭代的蚂蚁数量（≥1），推荐等于城市数量 |
| 信息素因子 (alpha) | 1.0 | 信息素在路径选择中的权重 |
| 启发函数因子 (beta) | 2.0 | 距离启发信息在路径选择中的权重 |
| 信息素挥发因子 (rho) | 0.5 | 每轮信息素挥发比例（0~1） |
| 信息素常数 (q) | 100 | 蚂蚁释放信息素的总量常数 |
| 最大迭代次数 | 100 | 算法最大迭代轮数 |

### 7.3 操作步骤

1. 运行 `python main.py`，打开 GUI 界面
2. （可选）在左侧调整参数
3. 点击 **"生成地图"** 按钮，生成并预览城市分布
4. 点击 **"运行算法"** 按钮开始求解
   - 若已生成地图，算法将复用该地图，不会重新生成
   - 若未生成地图，算法会自动创建新地图
5. 等待计算完成，查看结果与可视化图表

---

## 8. 核心接口说明

当前版本采用单文件结构，所有核心功能都位于 `main.py` 中，但仍按职责划分为若干清晰的函数区和类区。

### 8.1 城市生成

**`generate_cities(n_cities, width=100, height=100)`**

在 `[0, width] × [0, height]` 区域内随机生成 `n_cities` 个城市坐标。

- **返回**: `[(x1, y1), (x2, y2), ...]` 城市坐标列表

### 8.2 蚁群算法核心

**`class AntColonyTSP(cities, ant_count, alpha, beta, rho, q, max_iter)`**

蚁群算法核心类，负责距离矩阵构建、路径搜索、信息素更新与结果统计。

| 方法 | 功能 |
|------|------|
| `__init__(...)` | 初始化参数、计算距离矩阵、初始化信息素矩阵 |
| `_calculate_distance_matrix()` | 计算城市间欧几里得距离矩阵 |
| `_select_next_city(current_city, visited)` | 轮盘赌选择下一个未访问城市 |
| `_update_pheromone(all_paths, all_distances)` | 信息素挥发与强化更新 |
| `run()` | 执行主循环，返回最优解及统计信息 |

**`run()` 返回字典结构**：

```python
{
    'best_path': [...],                  # 最优路径（城市索引序列）
    'best_distance': float,              # 最优路径的总距离
    'running_time': float,               # 运行时间（秒）
    'convergence_iteration': int,        # 收敛迭代次数
    'iteration_best_distances': [...]    # 每轮最优距离列表
}
```

### 8.3 绘图辅助

`main.py` 内部提供 `setup_chinese_font()`、`create_figure()`、`plot_best_path()` 和 `plot_convergence()` 四个函数，用于配置中文字体、创建双子图画布并绘制路径图与收敛曲线。

### 8.4 图形界面

**`class AntColonyGUI(root)`**

基于 Tkinter 的图形用户界面，负责参数输入、地图生成、算法调用、结果显示与画布刷新。

| 方法 | 功能 |
|------|------|
| `__init__(root)` | 初始化窗口布局与控件 |
| `_create_param_controls()` | 创建参数输入控件 |
| `_create_canvas()` | 创建 Matplotlib 画布 |
| `_create_actions()` | 创建“生成地图”和“运行算法”按钮 |
| `_create_result_box()` | 创建文本结果区域 |
| `_validate_inputs()` | 校验输入参数 |
| `generate_map()` | 生成城市地图并显示城市分布散点图 |
| `run_algorithm()` | 读取参数、复用或生成地图、调用算法、更新图形和结果 |
| `_plot_cities()` | 在画布上绘制城市分布散点图 |
| `_plot_results(solver, results)` | 清空画布并绘制最优路径与收敛曲线 |

### 8.5 程序入口

`main.py` 的 `main()` 负责解析命令行参数：

- 默认运行 `python main.py` 时启动 GUI
- 运行 `python main.py --docx` 时执行 Markdown 转 Word 文档导出流程

---

## 9. 系统流程

当前系统采用**单文件、双入口**设计，流程如下：

1. **GUI 入口**
   - 运行 `python main.py`
   - 创建 Tk 窗口并初始化 `AntColonyGUI`
   - 用户可先点击“生成地图”，也可直接点击“运行算法”
   - 若未提前生成地图，系统会在运行算法前自动生成城市坐标
   - 求解完成后，同步更新文本结果、最优路径图和收敛曲线

2. **文档导出入口**
   - 运行 `python main.py --docx`
   - 程序自动扫描当前目录中的 Markdown 文件
   - 选择最近修改的目标文件并导出为同名 `.docx`
   - 若 Word 文件正被占用，程序会给出明确提示

---

## 10. 独立使用示例

由于核心函数和类仍保留为独立接口，即使采用单文件结构，也可以不启动 GUI 而直接复用算法与绘图能力：

```python
from main import generate_cities, AntColonyTSP, setup_chinese_font, plot_best_path, plot_convergence
import matplotlib.pyplot as plt

# 1. 生成城市
cities = generate_cities(n_cities=30, width=100, height=100)

# 2. 运行蚁群算法
aco = AntColonyTSP(cities=cities, ant_count=50, max_iter=100)
results = aco.run()

print(f"最优距离: {results['best_distance']:.2f}")
print(f"运行时间: {results['running_time']:.2f} 秒")

# 3. 绘制结果
setup_chinese_font()
fig, ax1, ax2 = plt.subplots(1, 2, figsize=(10, 5))
plot_best_path(ax1, cities, results['best_path'], results['best_distance'])
plot_convergence(ax2, results['iteration_best_distances'])
plt.tight_layout()
plt.show()
```

---

## 11. 结果解读

- **最优距离**：算法找到的最短回路长度
- **运行时间**：算法执行耗时（秒）
- **收敛迭代次数**：最优解首次稳定（连续两次变化 < 0.01）时的迭代轮数
- **路径图**：城市按最优访问顺序连线，起点与终点重合
- **收敛曲线**：横轴为迭代次数，纵轴为当前最优距离，反映算法收敛过程

---

## 12. 注意事项

1. **中文显示**：程序已设置 `SimHei` 字体，若系统无此字体，可修改 `main.py` 中 `setup_chinese_font()` 的字体配置（如 `Microsoft YaHei`、`SimSun`）
2. **计算时间**：城市数量大或迭代次数多时，计算时间可能较长；当前 GUI 仍采用同步执行方式
3. **随机性**：城市坐标和蚂蚁起点均为随机生成，每次运行结果可能略有不同
4. **地图复用**：生成地图后点击"运行算法"不会重新生成城市，便于在同一地图上对比不同参数效果
5. **参数调优**：
   - 增大 `alpha` 使蚂蚁更依赖信息素，适合 exploitation
   - 增大 `beta` 使蚂蚁更依赖距离启发，适合 exploration
   - 减小 `rho` 使信息素挥发变慢，收敛更慢但搜索更充分
   - 增大 `ant_count` 和 `max_iter` 通常能找到更优解，但计算量增加

---

## 13. 扩展方向

- 支持从文件导入城市坐标（如 TSPLIB 标准格式）
- 增加多种 ACO 变体（如 ACS、MMAS）
- 与其他启发式算法对比（遗传算法、模拟退火等）
- 支持动态调整参数（自适应 ACO）
- 导出结果和路径图
- 为 `main.py` 中的 `AntColonyTSP` 增加单元测试
- 将 `main.py` 中的绘图部分扩展为实时动画，展示蚂蚁逐步构建路径的过程

---

*文档更新日期：2026/04/28*
