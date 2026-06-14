# 流程图文件说明

本目录包含混合蚁群算法的各类流程图，使用 PlantUML 格式编写。

## 文件列表

| 文件名 | 说明 |
|--------|------|
| `01_basic_aco.pu` | 基本蚁群算法流程图 |
| `02_aco_adaptive.pu` | ACO + 自适应参数流程图 |
| `03_aco_ga.pu` | ACO + 遗传算法流程图 |
| `04_aco_2opt.pu` | ACO + 2-opt局部搜索流程图 |
| `05_hybrid_algorithm.pu` | 混合算法完整流程图 |
| `06_genetic_algorithm.pu` | 遗传算法详细流程图 |
| `07_two_opt.pu` | 2-opt局部搜索详细流程图 |
| `08_algorithm_comparison.pu` | 五种算法对比流程图 |
| `09_system_architecture.pu` | 系统架构图 |
| `10_data_flow.pu` | 数据流图 |

## 如何使用

### 方法1：在线渲染

1. 访问 [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. 复制 `.pu` 文件内容
3. 粘贴到编辑器中
4. 点击 "Submit" 生成图片

### 方法2：VS Code 插件

1. 安装 VS Code 插件：**PlantUML**
2. 打开 `.pu` 文件
3. 按 `Alt + D` 预览
4. 右键导出为 PNG/SVG

### 方法3：命令行工具

```bash
# 安装 PlantUML
# 需要 Java 环境

# 生成 PNG
java -jar plantuml.jar *.pu

# 生成 SVG
java -jar plantuml.jar -tsvg *.pu
```

## 流程图预览

### 基本蚁群算法
```
开始 → 初始化 → 蚁群构建路径 → 计算距离 → 更新最优 → 信息素更新 → 循环/输出
```

### 混合算法
```
开始 → 初始化 → [自适应参数] → [蚁群构建] → [遗传增强] → [2-opt优化] → [精英更新] → 循环/输出
```

## 算法对比

| 算法 | 流程复杂度 | 解质量 | 推荐度 |
|------|-----------|--------|--------|
| 基本ACO | ★★☆☆☆ | 中等 | ⭐⭐⭐ |
| ACO+自适应 | ★★★☆☆ | 中等+ | ⭐⭐⭐⭐ |
| ACO+GA | ★★★★☆ | 较高 | ⭐⭐⭐⭐ |
| ACO+2opt | ★★★☆☆ | 较高 | ⭐⭐⭐⭐⭐ |
| 混合算法 | ★★★★★ | 最高 | ⭐⭐⭐⭐⭐ |
