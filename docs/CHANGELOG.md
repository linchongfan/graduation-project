# 代码修改记录

## 版本历史

### v2.0 (2026-05-29) - 混合算法版本

#### 新增功能

1. **混合蚁群算法**
   - 自适应参数调整（alpha从0.8→2.0，beta从3.0→1.5）
   - 遗传算法增强（顺序交叉OX + 交换/逆转变异）
   - 2-opt局部搜索优化
   - 精英蚂蚁策略（前10%精英释放2倍信息素）

2. **PyQt5 + PyQtGraph 可视化界面**
   - 现代化GUI界面
   - 交互式图表（缩放、拖动）
   - 实时显示最优路径和收敛曲线
   - 收敛图上标记距离下降点

3. **结果导出功能**
   - JSON格式导出
   - TXT格式导出
   - CSV格式导出

4. **算法对比功能**
   - 一键对比5种算法配置
   - 显示对比结果表格

5. **结果统计**
   - 首次迭代距离
   - 最后下降迭代次数

#### 代码结构

```
hybrid_aco.py
├── 配置常量
│   ├── AlgorithmConfig        # 算法配置
│   └── VisualizationConfig    # 可视化配置
├── 数据结构
│   ├── City                   # 城市数据类
│   ├── AlgorithmResult        # 算法结果类
│   └── OptimizationStrategy   # 优化策略枚举
├── 核心模块
│   ├── CityGenerator          # 城市生成器
│   ├── DistanceCalculator     # 距离计算器
│   ├── PheromoneManager       # 信息素管理器
│   ├── Ant                    # 蚂蚁类
│   ├── AntColonyOptimizer     # 蚁群优化器
│   ├── GeneticOperator        # 遗传操作算子
│   ├── GeneticEnhancer        # 遗传增强器
│   ├── TwoOptOptimizer        # 2-opt优化器
│   └── HybridACOGA            # 混合算法主类
├── 辅助模块
│   ├── PlotManager            # 图表管理器
│   ├── ResultExporter         # 结果导出器
│   ├── ParameterPreset        # 参数预设
│   ├── PerformanceAnalyzer    # 性能分析器
│   ├── AlgorithmValidator     # 算法验证器
│   ├── TSPLibLoader           # TSP测试实例库
│   └── ExperimentRunner       # 实验运行器
└── GUI
    └── HybridACOGUI           # 图形用户界面
```

---

### v1.0 (2026-05-29) - 基本版本

#### 初始功能

1. **基本蚁群算法**
   - 轮盘赌选择策略
   - 信息素更新机制
   - 收敛判定

2. **Matplotlib + Tkinter 界面**
   - 基本参数设置
   - 城市分布图
   - 最优路径图
   - 收敛曲线

---

## 详细修改记录

### 2026-05-29 修改

#### 1. 移除DOCX导出功能

**文件**: `main.py`

**修改内容**:
- 移除 `argparse` 导入
- 移除 `re` 模块导入
- 移除 `pathlib` 模块导入
- 移除 `DOCX export helpers` 部分（约250行）
- 移除 `--docx` 命令行参数
- 简化 `main()` 函数

**原因**: 保持代码专注于蚁群算法核心功能

#### 2. 更新毕业设计说明书

**文件**: `毕业设计说明书.md`

**修改内容**:
- 移除摘要中关于文档导出功能的描述
- 移除第一章中关于文档导出模块的描述
- 更新第二章Python开发环境（移除python-docx、pathlib、argparse）
- 更新第三章系统架构设计（移除双入口设计和文档导出模块）
- 更新第四章系统实现（移除文档导出模块实现）
- 更新第六章总结与展望（移除文档导出功能）

#### 3. 创建混合算法版本

**文件**: `hybrid_aco.py`

**新增内容**:
- 混合蚁群算法实现
- PyQt5 + PyQtGraph 可视化界面
- 自适应参数调整策略
- 遗传算法增强
- 2-opt局部搜索优化
- 精英蚂蚁策略
- 结果导出功能
- 算法对比功能

#### 4. 创建README文档

**文件**: `README.md`

**内容**:
- 项目简介
- 功能特点
- 安装依赖
- 运行方法
- 使用说明
- 参数说明
- 算法流程
- 实验对比

#### 5. 修复BUG

**问题1**: `SyntaxError: invalid syntax`
- **原因**: 中文引号在字符串中被解释为引号分隔符
- **修复**: 使用单引号包裹字符串

**问题2**: `AttributeError: 'HybridACOGUI' object has no attribute '_create_algorithm_options'`
- **原因**: 方法被合并但调用未更新
- **修复**: 移除旧方法调用

**问题3**: `object of type 'NoneType' has no len()`
- **原因**: 遗传算法增强器未设置距离矩阵
- **修复**: 添加 `set_distance_matrix()` 方法

**问题4**: 导出结果失败
- **原因**: 未保存求解结果到 `self.last_result`
- **修复**: 在 `run_algorithm()` 中添加结果保存

---

## 算法对比实验

| 算法 | 平均最优距离 | 运行时间 | 收敛迭代 | 说明 |
|------|------------|---------|---------|------|
| 基本ACO | ~578 | ~6.9s | ~3.7 | 仅蚁群算法 |
| ACO + 自适应 | ~565 | ~7.0s | ~3.5 | 添加参数自适应 |
| ACO + 遗传算法 | ~550 | ~10s | ~4.0 | 添加遗传增强 |
| ACO + 2-opt | ~542 | ~8s | ~3.2 | 添加局部搜索 |
| 混合算法 | ~525 | ~12s | ~3.0 | 全部组合 |

---

## 文件清单

| 文件 | 说明 | 状态 |
|------|------|------|
| `main.py` | 原始蚁群算法（已精简） | 保留 |
| `hybrid_aco.py` | 混合算法版本（主要） | 新增 |
| `hybrid_aco_backup.py` | 混合算法备份 | 新增 |
| `毕业设计说明书.md` | 毕业设计文档 | 更新 |
| `README.md` | 项目说明文档 | 新增 |
| `CHANGELOG.md` | 修改记录文档 | 新增 |

---

## 技术要点

### 1. 自适应参数调整

```python
# alpha从0.8线性增长到2.0
self.alpha = 0.8 + 1.2 * ratio

# beta从3.0线性减小到1.5
self.beta = 3.0 - 1.5 * ratio
```

**原理**: 前期注重探索（alpha小、beta大），后期注重利用（alpha大、beta小）

### 2. 顺序交叉（OX）

```python
# 1. 从parent1复制一段基因
child[start:end] = parent1[start:end]

# 2. 从parent2按顺序填充剩余城市
remaining = [city for city in parent2[1:-1] if city not in child[start:end]]
```

**原理**: 保持父代1的路径片段，从父代2继承路径顺序

### 3. 2-opt局部搜索

```python
# 计算距离变化
old_dist = distance_matrix[path[i-1]][path[i]] + distance_matrix[path[j]][path[j+1]]
new_dist = distance_matrix[path[i-1]][path[j]] + distance_matrix[path[i]][path[j+1]]

if new_dist < old_dist:
    # 反转路径片段
    path[i:j+1] = reversed(path[i:j+1])
```

**原理**: 通过反转路径片段减少路径交叉

### 4. 精英信息素更新

```python
# 精英蚂蚁释放2倍信息素
if rank < elite_count:
    delta *= 2.0
```

**原理**: 强化正反馈，加速收敛

---

## 待优化项

1. **界面优化**
   - 添加参数预设选择
   - 添加实时参数调整
   - 优化图表样式

2. **算法优化**
   - 实现更多遗传算法变体
   - 添加并行计算支持
   - 实现动态TSP求解

3. **功能扩展**
   - 添加TSPLIB标准实例导入
   - 添加结果可视化报告
   - 添加单元测试
