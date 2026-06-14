#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2-opt局部搜索优化算法流程图生成器
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle
import numpy as np


def draw_flowchart():
    """绘制2-opt算法流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')

    # 定义颜色
    start_end_color = '#4A90A4'
    process_color = '#5B9BD5'
    decision_color = '#FFC000'
    io_color = '#70AD47'
    text_color = 'white'
    arrow_color = '#333333'

    # 绘制流程框
    def draw_rounded_box(x, y, width, height, text, color, shape='rectangle'):
        if shape == 'rounded':
            box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                               boxstyle="round,pad=0.1", facecolor=color,
                               edgecolor='black', linewidth=2)
        elif shape == 'diamond':
            # 菱形用多边形绘制
            diamond = plt.Polygon([(x, y + height/2), (x + width/2, y),
                                   (x, y - height/2), (x - width/2, y)],
                                  facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(diamond)
            ax.text(x, y, text, ha='center', va='center', fontsize=9,
                   fontweight='bold', color='black')
            return
        elif shape == 'parallelogram':
            # 平行四边形
            offset = 0.3
            parallelogram = plt.Polygon([
                (x - width/2 + offset, y - height/2),
                (x + width/2 + offset, y - height/2),
                (x + width/2 - offset, y + height/2),
                (x - width/2 - offset, y + height/2)
            ], facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(parallelogram)
            ax.text(x, y, text, ha='center', va='center', fontsize=9,
                   fontweight='bold', color=text_color)
            return
        else:
            box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                               boxstyle="square,pad=0", facecolor=color,
                               edgecolor='black', linewidth=2)

        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=9,
               fontweight='bold', color=text_color, wrap=True)

    # 绘制箭头
    def draw_arrow(x1, y1, x2, y2, label='', color=arrow_color):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2))
        if label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            ax.text(mid_x + 0.15, mid_y, label, fontsize=8, color=color,
                   fontweight='bold')

    # 标题
    ax.text(5, 15.5, '2-opt 局部搜索优化算法流程图', ha='center', va='center',
           fontsize=14, fontweight='bold', color='black')

    # 开始/结束
    draw_rounded_box(5, 14.8, 2, 0.5, '开始', start_end_color, 'rounded')

    # 输入初始路径
    draw_arrow(5, 14.55, 5, 14.1)
    draw_rounded_box(5, 13.8, 3, 0.5, '输入初始路径 path', io_color, 'parallelogram')

    # 初始化
    draw_arrow(5, 13.55, 5, 13.0)
    draw_rounded_box(5, 12.6, 4, 0.7,
                    'best_path = path.copy()\nbest_distance = 计算路径距离\nimproved = True',
                    process_color, 'rounded')

    # 判断 improved
    draw_arrow(5, 12.25, 5, 11.7)
    draw_rounded_box(5, 11.2, 2.5, 0.8, 'improved\n== True ?', decision_color, 'diamond')

    # No 分支 - 返回结果
    draw_arrow(6.25, 11.2, 7.5, 11.2, 'No')
    draw_rounded_box(8.2, 11.2, 2, 0.6,
                    '返回结果\n(best_path,\nbest_distance)',
                    io_color, 'parallelogram')

    # Yes 分支 - improved = False
    draw_arrow(5, 10.8, 5, 10.2, 'Yes')
    draw_rounded_box(5, 9.8, 2.5, 0.5, 'improved = False', process_color, 'rounded')

    # 遍历 i,j 对
    draw_arrow(5, 9.55, 5, 9.0)
    draw_rounded_box(5, 8.5, 3.5, 0.7,
                    '遍历所有 (i, j) 对\ni: 1 → n-2,  j: i+1 → n-1',
                    process_color, 'rounded')

    # 计算 delta
    draw_arrow(5, 8.15, 5, 7.5)
    draw_rounded_box(5, 7.1, 3.5, 0.6,
                    '计算 delta =\nnew_dist - old_dist',
                    process_color, 'rounded')

    # 判断 delta < 0
    draw_arrow(5, 6.8, 5, 6.3)
    draw_rounded_box(5, 5.8, 2.5, 0.8, 'delta < 0 ?', decision_color, 'diamond')

    # No 分支 - 继续下一对
    draw_arrow(6.25, 5.8, 7.5, 5.8, 'No')
    draw_rounded_box(8.2, 5.8, 2, 0.5, '继续下一\n对 (i, j)', process_color, 'rounded')

    # 返回遍历
    draw_arrow(8.2, 5.55, 8.2, 8.5)
    draw_arrow(8.2, 8.5, 6.75, 8.5)

    # Yes 分支 - 反转路径
    draw_arrow(5, 5.4, 5, 4.8, 'Yes')
    draw_rounded_box(5, 4.4, 3, 0.6,
                    '反转路径片段\npath[i:j+1]',
                    process_color, 'rounded')

    # 更新距离
    draw_arrow(5, 4.1, 5, 3.5)
    draw_rounded_box(5, 3.1, 3, 0.6,
                    '更新距离\nbest_distance += delta',
                    process_color, 'rounded')

    # improved = True
    draw_arrow(5, 2.8, 5, 2.2)
    draw_rounded_box(5, 1.8, 2.5, 0.5, 'improved = True', process_color, 'rounded')

    # 返回判断 improved
    draw_arrow(5, 1.55, 2, 1.55)
    draw_arrow(2, 1.55, 2, 11.2)
    draw_arrow(2, 11.2, 3.75, 11.2)

    # 添加图例说明
    legend_y = 0.5
    legend_items = [
        (start_end_color, '开始/结束'),
        (process_color, '处理步骤'),
        (decision_color, '判断条件'),
        (io_color, '输入/输出'),
    ]

    for i, (color, label) in enumerate(legend_items):
        x = 1 + i * 2.2
        rect = FancyBboxPatch((x, legend_y - 0.15), 0.4, 0.3,
                             boxstyle="round,pad=0.02", facecolor=color,
                             edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        ax.text(x + 0.6, legend_y, label, fontsize=8, va='center', color='black')

    plt.tight_layout()
    return fig


def main():
    """主函数"""
    import os

    # 创建docs文件夹（如果不存在）
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    # 生成流程图
    fig = draw_flowchart()

    # 保存图片
    output_path = os.path.join(docs_dir, '2opt_flowchart.png')
    fig.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"流程图已保存到: {output_path}")

    plt.show()


if __name__ == '__main__':
    main()
