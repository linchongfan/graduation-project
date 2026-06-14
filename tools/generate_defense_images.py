from __future__ import annotations

import math
import textwrap
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageOps


W, H = 1600, 900
BG = "#F6F1E8"
PAPER = "#FFFDF8"
INK = "#17222B"
MUTED = "#5F6A72"
LINE = "#DDD5C9"
ACCENT = "#D56F45"
ACCENT_SOFT = "#F0D6CA"
GREEN = "#2F6C5E"
GREEN_SOFT = "#DDECE5"
BLUE = "#5A758B"
BLUE_SOFT = "#DFE9F2"
GOLD = "#C4A04C"
GOLD_SOFT = "#F2E8C8"
DARK = "#10202A"
WHITE = "#FFFDF8"

ROOT = Path(r"C:\Users\帆\Desktop\毕业设计")
OUT_DIR = ROOT / "outputs" / "defense_ppt_images"
OUT_DIR.mkdir(parents=True, exist_ok=True)

GEN_DIR = Path(r"C:\Users\帆\.codex\generated_images\019eab71-2262-7221-b021-915e86dc8bed")
COVER_IMAGE = sorted(GEN_DIR.glob("*.png"))[0]

FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size=size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, max_width: int, fnt: ImageFont.FreeTypeFont) -> List[str]:
    if not text:
        return []
    lines: List[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        cur = ""
        for ch in paragraph:
            trial = cur + ch
            if draw.textlength(trial, font=fnt) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
    return lines


def draw_multiline(draw, xy, text, fnt, fill, max_width, line_gap=8):
    lines = wrap_text(draw, text, max_width, fnt)
    x, y = xy
    bbox = draw.textbbox((0, 0), "测", font=fnt)
    h = bbox[3] - bbox[1]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += h + line_gap
    return y


def rounded(draw, box, fill, outline=None, width=1, radius=22):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def base_slide(dark: bool = False):
    img = Image.new("RGB", (W, H), DARK if dark else BG)
    draw = ImageDraw.Draw(img)
    if not dark:
      draw.rectangle((0, 0, 18, H), fill=ACCENT)
    return img, draw


def header(draw, kicker, title, subtitle=None, dark=False):
    kfill = "#233847" if dark else ACCENT_SOFT
    kcolor = WHITE if dark else ACCENT
    tcolor = WHITE if dark else INK
    scolor = "#D8E0E6" if dark else MUTED
    rounded(draw, (62, 40, 250, 76), kfill, radius=18)
    draw.text((84, 48), kicker, font=font(24, True), fill=kcolor)
    y = draw_multiline(draw, (62, 100), title, font(40, True), tcolor, 930, 10)
    if subtitle:
        draw_multiline(draw, (62, y + 8), subtitle, font(22), scolor, 930, 6)
    draw.line((62, 238, 1538, 238), fill="#314350" if dark else LINE, width=2)


def footer(draw, page, dark=False):
    c = "#C9D3DB" if dark else MUTED
    l = "#314350" if dark else LINE
    draw.line((62, 872, 1538, 872), fill=l, width=1)
    draw.text((62, 878), "基于求解旅行商问题的蚁群算法的设计与实现", font=font(12), fill=c)
    p = str(page)
    tw = draw.textlength(p, font=font(13, True))
    draw.text((1520 - tw, 876), p, font=font(13, True), fill=c)


def card(draw, box, title, body, accent=ACCENT, fill=PAPER, title_size=28, body_size=22):
    rounded(draw, box, fill, outline=LINE, width=2, radius=24)
    x1, y1, x2, y2 = box
    draw.rectangle((x1 + 22, y1 + 20, x1 + 72, y1 + 26), fill=accent)
    draw.text((x1 + 22, y1 + 36), title, font=font(title_size, True), fill=INK)
    draw_multiline(draw, (x1 + 22, y1 + 86), body, font(body_size), MUTED, x2 - x1 - 44, 8)


def stat_card(draw, box, value, label, note="", accent=ACCENT):
    rounded(draw, box, PAPER, outline=LINE, width=2, radius=22)
    x1, y1, x2, y2 = box
    draw.ellipse((x1 + 18, y1 + 18, x1 + 36, y1 + 36), fill=accent)
    draw.text((x1 + 18, y1 + 46), value, font=font(34, True), fill=INK)
    draw.text((x1 + 18, y1 + 98), label, font=font(18), fill=MUTED)
    if note:
        draw_multiline(draw, (x1 + 18, y1 + 126), note, font(14), MUTED, x2 - x1 - 36, 4)


def bullets(draw, x, y, items, width, bullet_color=ACCENT, size=22, gap=14):
    for item in items:
        draw.ellipse((x, y + 12, x + 10, y + 22), fill=bullet_color)
        draw_multiline(draw, (x + 20, y), item, font(size), INK, width - 20, 6)
        y += 40 + gap


def mini_tag(draw, x, y, text, fill=GOLD_SOFT, color=INK):
    rounded(draw, (x, y, x + 122, y + 30), fill, radius=14)
    tw = draw.textlength(text, font=font(14, True))
    draw.text((x + (122 - tw) / 2, y + 6), text, font=font(14, True), fill=color)


def bar_chart(draw, x, y, w, h, data, max_value, colors):
    label_w = 250
    row_h = h / len(data)
    bar_w = w - label_w - 80
    for i, (label, value) in enumerate(data):
        row_y = y + i * row_h
        draw.text((x, row_y + 6), label, font=font(20), fill=INK)
        draw.rounded_rectangle((x + label_w, row_y + 18, x + label_w + bar_w, row_y + 42), 10, fill="#ECE6DC")
        width = max(18, bar_w * value / max_value)
        draw.rounded_rectangle((x + label_w, row_y + 18, x + label_w + width, row_y + 42), 10, fill=colors[i])
        draw.text((x + label_w + width + 12, row_y + 14), f"{value:.2f}", font=font(18), fill=MUTED)


def simple_table(draw, x, y, col_widths, rows, row_h=46, header_fill=BLUE_SOFT, body_fill=PAPER, size=18):
    for r, row in enumerate(rows):
        cx = x
        for c, cell in enumerate(row):
            fill = header_fill if r == 0 else body_fill
            draw.rectangle((cx, y + r * row_h, cx + col_widths[c], y + (r + 1) * row_h), fill=fill, outline=LINE, width=2)
            max_w = col_widths[c] - 20
            lines = wrap_text(draw, str(cell), max_w, font(size, r == 0))
            ty = y + r * row_h + 10
            for line in lines[:2]:
                tw = draw.textlength(line, font=font(size, r == 0))
                tx = cx + 10 if c == 0 else cx + (col_widths[c] - tw) / 2
                draw.text((tx, ty), line, font=font(size, r == 0), fill=INK)
                ty += 20
            cx += col_widths[c]


def slide1():
    img, draw = base_slide(True)
    draw.text((72, 52), "本科毕业设计学术答辩", font=font(18, True), fill="#D7E0E7")
    draw_multiline(draw, (72, 106), "基于求解旅行商问题的蚁群算法\n设计与实现", font(54, True), WHITE, 560, 10)
    draw_multiline(draw, (72, 262), "以基础蚁群算法为核心，结合自适应参数、遗传算法与 2-opt 局部搜索，提升 TSP 求解效果", font(24), "#D7E0E7", 560, 8)
    rounded(draw, (72, 360, 386, 486), "#1E2D3A", outline="#314250", width=2, radius=24)
    draw_multiline(draw, (96, 388), "答辩人：林重帆\n专业：数据科学与大数据技术\n指导教师：夏传良", font(25), WHITE, 260, 10)
    vals = [("7.88%", "最优路径降低"), ("74.7%", "收敛速度提升"), ("795.23", "最佳组合均值")]
    for i, (v, l) in enumerate(vals):
        x = 72 + i * 154
        rounded(draw, (x, 524, x + 138, 632), "#18252F", outline="#314250", width=2, radius=22)
        draw.text((x + 16, 544), v, font=font(34, True), fill=[ACCENT, "#79D2B5", "#F2C96D"][i])
        draw.text((x + 16, 590), l, font=font(17), fill="#D7E0E7")
    art = Image.open(COVER_IMAGE).convert("RGB")
    art = ImageOps.fit(art, (560, 580), method=Image.Resampling.LANCZOS)
    img.paste(art, (968, 84))
    footer(draw, 1, True)
    return img


def slide2():
    img, draw = base_slide()
    header(draw, "研究背景", "TSP 难在组合爆炸，启发式方法更适合中大规模求解", "旅行商问题是组合优化中的经典 NP-hard 问题，也是本文选择蚁群算法的现实起点。")
    card(draw, (62, 274, 500, 742), "问题本质", "给定 n 个城市及两两距离，寻找一条经过所有城市恰好一次并返回起点的最短回路。\n\n随着城市规模增大，路径数量呈阶乘式增长，穷举法在实际中不可行。", ACCENT)
    bullets(draw, 88, 542, ["路径数量随规模快速爆炸", "精确算法适合小规模问题", "工程上需要兼顾效率与解质量"], 350, ACCENT, 22, 12)
    rounded(draw, (528, 274, 980, 492), PAPER, outline=LINE, width=2, radius=24)
    draw.rectangle((552, 296, 602, 302), fill=BLUE)
    draw.text((552, 320), "应用场景", font=font(28, True), fill=INK)
    draw_multiline(draw, (552, 372), "典型场景包括物流配送、电路板钻孔、DNA 排序和网络路由，说明该问题兼具理论意义与工程价值。", font(20), MUTED, 388, 8)
    mini_tag(draw, 552, 430, "物流配送", BLUE_SOFT)
    mini_tag(draw, 690, 430, "电路钻孔", PAPER)
    mini_tag(draw, 552, 468, "DNA 排序", BLUE_SOFT)
    mini_tag(draw, 690, 468, "网络路由", PAPER)
    card(draw, (1010, 274, 1534, 742), "为什么选 ACO", "蚁群算法具有正反馈、并行搜索和较强鲁棒性，适合复杂解空间中的近优搜索。", GREEN)
    draw.text((1036, 470), "论文选择 ACO 的原因", font=font(18, True), fill=MUTED)
    bullets(draw, 1036, 504, ["适合复杂解空间中的近优搜索", "兼顾解质量、并行性与工程实现性", "为后续变种改进预留清晰接口"], 430, GREEN, 20, 10)
    draw.text((1036, 650), "但传统 ACO 仍存在收敛慢、易陷局部最优和参数敏感等问题。", font=font(18), fill=MUTED)
    stat_card(draw, (528, 536, 680, 676), "NP-hard", "问题属性", "难以精确求全局最优", ACCENT)
    stat_card(draw, (702, 536, 854, 676), "ACO", "选用方法", "兼顾质量与效率", GREEN)
    stat_card(draw, (876, 536, 980, 676), "TSP", "研究对象", "标准路径优化问题", BLUE)
    rounded(draw, (528, 698, 980, 760), "#F1ECE2", outline=LINE, width=2, radius=18)
    draw.text((552, 718), "研究背景的核心逻辑：问题规模很大，精确法代价过高，因此需要以基础 ACO 为起点展开后续改进。", font=font(20, True), fill=INK)
    footer(draw, 2)
    return img


def slide3():
    img, draw = base_slide()
    header(draw, "研究现状", "国内外研究从基础 ACO 逐步走向变种与混合优化", "论文综述指出：单一算法难以兼顾全局搜索与局部强化，因此混合策略成为主流趋势。")
    card(draw, (62, 278, 490, 640), "基础蚁群算法发展", "Dorigo 提出 ACO 后，研究者陆续发展出 Ant System、ACS、MMAS 等变种，通过增强信息素机制和状态转移规则改善搜索性能。", ACCENT)
    card(draw, (520, 278, 960, 640), "TSP 求解方法演进", "TSP 求解从动态规划、分支定界等精确算法，扩展到模拟退火、禁忌搜索、遗传算法、粒子群与蚁群等元启发式方法。", BLUE)
    card(draw, (990, 278, 1534, 640), "当前趋势", "近年来更强调多策略融合，例如“参数自适应 + 群智能”“遗传 + 局部搜索”等，目标是在解质量、速度与稳定性之间取得更优平衡。", GREEN)
    rounded(draw, (62, 676, 1534, 772), "#F1ECE2", outline=LINE, width=2, radius=22)
    draw.text((92, 704), "论文切入点：不再单纯优化 ACO 某一个环节，而是围绕基础 ACO 组合三种改进策略，考察各自作用及协同效果。", font=font(28, True), fill=INK)
    footer(draw, 3)
    return img


def slide4():
    img, draw = base_slide()
    header(draw, "理论基础", "论文的理论基础由 TSP 数学模型、ACO、GA 与 2-opt 共同构成", "答辩时这一页的作用是帮助评委快速建立后续算法设计的知识框架。")
    for i, (title, body, fill, accent) in enumerate([
        ("TSP 数学模型", "目标是在完全图中找到最短 Hamilton 回路，是后续所有算法的优化对象。", ACCENT_SOFT, ACCENT),
        ("基础 ACO", "通过信息素与启发函数协同引导蚂蚁构造路径。", BLUE_SOFT, BLUE),
        ("遗传算法", "通过选择、交叉和变异维持种群多样性。", GREEN_SOFT, GREEN),
        ("2-opt 局部搜索", "通过反转路径片段消除交叉并压缩路径长度。", GOLD_SOFT, GOLD),
    ]):
        x = 72 + i * 376
        rounded(draw, (x, 322, x + 340, 610), fill, outline=LINE, width=2, radius=24)
        draw.rectangle((x + 22, 344, x + 70, 350), fill=accent)
        draw.text((x + 22, 368), title, font=font(28, True), fill=INK)
        draw_multiline(draw, (x + 22, 420), body, font(22), MUTED, 294, 8)
    rounded(draw, (72, 666, 1534, 782), PAPER, outline=LINE, width=2, radius=22)
    draw.text((94, 704), "答辩逻辑：先解释基础 ACO 为什么能解 TSP，再说明为什么需要自适应参数、GA 和 2-opt 的逐层增强。", font=font(28, True), fill=INK)
    footer(draw, 4)
    return img


def slide5():
    img, draw = base_slide()
    header(draw, "基础 ACO 原理", "基础蚁群算法通过正反馈机制把随机搜索组织成协同搜索", "其灵感来源于蚂蚁觅食：较短路径往返更快，信息素积累更快，因此会逐步被更多个体选择。")
    for idx, (num, title, body) in enumerate([
        ("01", "随机探索", "蚂蚁从不同城市出发，先在解空间中构造可行路径。"),
        ("02", "信息素累积", "较优路径被多次经过后，会在边上留下更多信息素。"),
        ("03", "群体收敛", "高浓度信息素进一步提升被选择概率，形成正反馈。"),
    ]):
        x = 92 + idx * 246
        draw.ellipse((x, 334, x + 76, 410), fill=[BLUE, ACCENT, GREEN][idx])
        tw = draw.textlength(num, font=font(26, True))
        draw.text((x + (76 - tw) / 2, 352), num, font=font(26, True), fill=WHITE)
        draw.text((x - 8, 432), title, font=font(24, True), fill=INK)
        draw_multiline(draw, (x - 18, 476), body, font(18), MUTED, 150, 6)
    card(draw, (868, 286, 1534, 646), "映射到 TSP", "蚂蚁 -> 候选解构造代理\n城市 -> 图中的节点\n边上的信息素 -> 路径优劣的历史记忆\n启发函数 -> 距离倒数 1/d\n目标 -> 形成总长度最短的闭合回路", BLUE)
    rounded(draw, (868, 664, 1534, 762), "#F2EEE6", outline=LINE, width=2, radius=20)
    draw.text((892, 702), "核心理解：基础 ACO 的价值，不在“单只蚂蚁多聪明”，而在群体反馈能持续压缩搜索范围。", font=font(24, True), fill=INK)
    footer(draw, 5)
    return img


def slide6():
    img, draw = base_slide()
    header(draw, "基础 ACO 机制", "状态转移规则与信息素更新共同驱动路径搜索", "论文采用 Ant-Cycle 模型，更强调整条路径质量对信息素强化的影响。")
    rounded(draw, (62, 286, 760, 590), PAPER, outline=LINE, width=2, radius=24)
    draw.rectangle((86, 306, 136, 312), fill=ACCENT)
    draw.text((86, 330), "状态转移规则", font=font(28, True), fill=INK)
    draw.text((86, 388), "P(i,j) ∝ [τij^α × ηij^β]", font=font(32, True), fill=INK)
    draw_multiline(draw, (86, 446), "τij 表示信息素浓度，ηij = 1 / dij 表示启发函数；α 控制经验依赖程度，β 控制距离启发强度。", font(21), MUTED, 620, 8)
    bullets(draw, 86, 510, ["α 越大，越依赖历史路径信息", "β 越大，越偏向贪心选近城市"], 620, ACCENT, 17, 6)
    rounded(draw, (844, 286, 1534, 590), PAPER, outline=LINE, width=2, radius=24)
    draw.rectangle((868, 306, 918, 312), fill=GREEN)
    draw.text((868, 330), "信息素更新机制", font=font(28, True), fill=INK)
    draw.text((868, 388), "τij(t+1) = (1-ρ)τij(t) + Δτij", font=font(30, True), fill=INK)
    draw_multiline(draw, (868, 446), "ρ 控制信息素挥发速度；路径越短，释放的信息素越多，从而对后续搜索形成更强引导。", font(21), MUTED, 620, 8)
    bullets(draw, 868, 510, ["ρ 大：探索更强，但收敛较慢", "ρ 小：利用更强，但更易早熟收敛"], 620, GREEN, 17, 6)
    rounded(draw, (62, 620, 1534, 760), PAPER, outline=LINE, width=2, radius=24)
    draw.rectangle((86, 640, 136, 646), fill=BLUE)
    draw.text((86, 664), "基本流程", font=font(28, True), fill=INK)
    draw.text((86, 696), "allowk 约束蚂蚁只访问尚未经过的城市；论文采用 Ant-Cycle，是因为它更适合 TSP 这类以整条路径质量为核心的优化问题。", font=font(20), fill=MUTED)
    steps = ["初始化参数", "构造路径", "计算路径质量", "挥发与强化", "终止判断", "输出最优解"]
    for i, step in enumerate(steps):
        x = 108 + i * 234
        rounded(draw, (x, 724, x + 180, 752), "#F1ECE2", outline=LINE, width=2, radius=18)
        draw.text((x + 18, 729), f"{i+1:02d}", font=font(17, True), fill=BLUE)
        draw.text((x + 58, 727), step, font=font(18, True), fill=INK)
        if i < len(steps) - 1:
            draw.line((x + 180, 738, x + 214, 738), fill=LINE, width=3)
            draw.polygon([(x + 214, 738), (x + 202, 732), (x + 202, 744)], fill=LINE)
    footer(draw, 6)
    return img


def slide7():
    img, draw = base_slide()
    header(draw, "传统 ACO 的不足", "慢收敛、易陷局部最优、参数敏感，是本文改进的直接动因", "这页需要把“为什么要改”讲透，后面的所有变种都由这三类问题引出。")
    card(draw, (72, 294, 494, 646), "收敛速度偏慢", "基础 ACO 需要通过多轮迭代逐步积累信息素。论文实验中，传统 ACO 平均收敛次数为 8.3 次。", ACCENT)
    card(draw, (526, 294, 978, 646), "局部最优风险", "早期路径一旦被过度强化，可能导致搜索迅速偏向次优区域，后续蚂蚁难以跳出。", GREEN)
    card(draw, (1010, 294, 1518, 646), "参数设置敏感", "α、β、ρ 等参数会显著影响探索与利用平衡，不同组合对结果差异明显。", BLUE)
    rounded(draw, (72, 690, 1518, 782), "#F2EEE6", outline=LINE, width=2, radius=22)
    draw.text((98, 724), "因此，论文选择从三个层面改进：参数层、自身搜索层、路径局部优化层。", font=font(30, True), fill=INK)
    footer(draw, 7)
    return img


def slide8():
    img, draw = base_slide()
    header(draw, "改进策略设计", "三类变种分别作用于参数、种群多样性和局部路径质量", "这三种策略都基于基础 ACO，但介入位置不同，因此作用机制和收益不同。")
    card(draw, (62, 286, 496, 724), "自适应参数", "作用层：参数层\n\nα 从 0.5 线性增至 2.5，β 从 4.0 线性降至 1.0。\n\n目的：前期增强探索，后期增强利用，缓解固定参数导致的搜索僵化。", ACCENT)
    bullets(draw, 92, 590, ["改善搜索节奏", "独立提升幅度有限", "主要价值在收敛行为优化"], 360, ACCENT, 16, 8)
    card(draw, (530, 286, 966, 724), "遗传算法增强", "作用层：群体搜索层\n\n引入锦标赛选择、顺序交叉 OX、交换/逆转变异和精英保留。\n\n目的：保持候选路径多样性，提高跳出局部最优的能力。", GREEN)
    bullets(draw, 560, 556, ["扩大搜索范围", "增强中后期全局搜索", "随机性相对更强"], 360, GREEN, 18, 8)
    card(draw, (1000, 286, 1534, 724), "2-opt 局部搜索", "作用层：路径质量层\n\n通过检查不相邻边的反转收益，消除路径交叉和局部冗余。\n\n目的：在已有可行路径基础上直接压缩路径长度。", BLUE)
    bullets(draw, 1030, 556, ["直接改善路径质量", "显著加快收敛", "会带来额外计算时间"], 450, BLUE, 18, 8)
    footer(draw, 8)
    return img


def slide9():
    img, draw = base_slide()
    header(draw, "系统设计与实现", "论文不仅提出算法，还实现了一个可视化 TSP 求解系统", "系统基于 Python 与 PyQt5，支持参数配置、策略切换、结果展示和数据导出。")
    mini_tag(draw, 72, 268, "系统架构")
    for i, (title, body, fill, accent) in enumerate([
        ("城市生成", "生成城市坐标与问题实例", BLUE_SOFT, BLUE),
        ("距离计算", "构建距离矩阵与启发信息", PAPER, BLUE),
        ("基础 ACO", "完成路径构造与信息素更新", ACCENT_SOFT, ACCENT),
        ("策略增强", "可选接入自适应、GA、2-opt", GREEN_SOFT, GREEN),
        ("结果分析", "输出路径图、收敛曲线与 JSON 数据", GOLD_SOFT, GOLD),
    ]):
        x = 84 + i * 296
        rounded(draw, (x, 324, x + 228, 472), fill, outline=LINE, width=2, radius=22)
        draw.rectangle((x + 20, 346, x + 64, 352), fill=accent)
        draw.text((x + 20, 372), title, font=font(26, True), fill=INK)
        draw_multiline(draw, (x + 20, 414), body, font(18), MUTED, 184, 6)
    card(draw, (72, 536, 484, 766), "界面层", "图形界面支持：城市数量、蚂蚁数量、参数设置、策略启停、最优路径显示、收敛曲线绘制、结果导出。", BLUE)
    card(draw, (520, 536, 980, 766), "核心数据结构", "论文定义了 City、AlgorithmResult 和 OptimizationStrategy 等结构，使算法、可视化和实验分析共享统一接口。", GREEN)
    card(draw, (1014, 536, 1534, 766), "实现价值", "系统把理论、算法与实验验证串联起来，使论文不仅停留在方法设计层，还具备可演示与可扩展性。", ACCENT)
    footer(draw, 9)
    return img


def slide10():
    img, draw = base_slide()
    header(draw, "实验设计", "8 组算法组合用于拆分独立效果、协同效果与全融合效果", "实验条件统一：100 个城市、50 只蚂蚁、最大迭代 1000 次，并比较解质量、时间、收敛和稳定性。")
    stat_card(draw, (72, 286, 236, 424), "100", "城市规模", "统一采用 100 个城市", BLUE)
    stat_card(draw, (252, 286, 416, 424), "50", "蚂蚁数量", "每轮搜索个体数", ACCENT)
    stat_card(draw, (432, 286, 596, 424), "1000", "最大迭代", "控制收敛上限", GREEN)
    stat_card(draw, (612, 286, 776, 424), "8", "实验分组", "覆盖单项与组合策略", GOLD)
    simple_table(draw, 72, 452, [74, 280, 500], [
        ["编号", "算法组合", "核心改进策略"],
        ["1", "传统 ACO", "无改进（基准对照组）"],
        ["2", "自适应参数", "α/β 参数动态调整"],
        ["3", "遗传算法", "引入选择、交叉、变异算子"],
        ["4", "2-opt", "路径局部搜索优化"],
        ["5", "自适应参数 + 遗传算法", "参数自适应 + 遗传算子"],
        ["6", "自适应参数 + 2-opt", "参数自适应 + 局部搜索"],
        ["7", "遗传算法 + 2-opt", "遗传算子 + 局部搜索"],
        ["8", "自适应参数 + 遗传算法 + 2-opt", "三者全融合"],
    ], row_h=38, size=17)
    card(draw, (962, 286, 1534, 498), "评价指标", "最优距离\n运行时间\n收敛次数\n首次迭代距离\n最后下降迭代\n收缩距离\n变异系数 CV", GOLD, body_size=17)
    card(draw, (962, 528, 1534, 760), "实验目的", "不仅比较“谁最好”，还要解释：\n1. 哪个策略最关键\n2. 哪种组合最稳\n3. 多策略叠加是否总能更优", BLUE, body_size=18)
    footer(draw, 10)
    return img


def slide11():
    img, draw = base_slide()
    header(draw, "单一策略实验结果", "在单独改进策略中，2-opt 对解质量和收敛速度提升最显著", "相比自适应参数和遗传增强，2-opt 直接作用于路径结构，因此提升更稳定也更明显。")
    bar_chart(draw, 72, 300, 780, 250, [
        ("传统 ACO", 865.61),
        ("自适应参数", 851.33),
        ("遗传算法", 831.42),
        ("2-opt", 798.22),
    ], 900, [BLUE, ACCENT, GREEN, GOLD])
    draw.text((72, 264), "平均最优距离对比", font=font(28, True), fill=INK)
    stat_card(draw, (920, 296, 1088, 454), "7.79%", "2-opt 路径改进幅度", "相对传统 ACO", GOLD)
    stat_card(draw, (1106, 296, 1274, 454), "2.0", "2-opt 收敛次数", "传统 ACO 为 8.3", GREEN)
    stat_card(draw, (1292, 296, 1518, 454), "840.97", "首次迭代距离", "说明早期路径质量改善明显", ACCENT)
    card(draw, (920, 498, 1518, 760), "结论", "自适应参数主要改善搜索节奏，独立增益仅 1.65%；遗传算法增强了全局搜索，但波动更大；2-opt 直接修正路径交叉，是单一策略中效果最突出的改进。", ACCENT)
    footer(draw, 11)
    return img


def slide12():
    img, draw = base_slide()
    header(draw, "组合策略实验结果", "GA + 2-opt 综合最优，而全融合更适合作为完整系统方案", "这一页要讲清：不是策略越多越好，而是有效协同优于简单叠加。")
    bar_chart(draw, 72, 300, 680, 230, [
        ("传统 ACO", 865.61),
        ("2-opt", 798.22),
        ("遗传 + 2-opt", 795.23),
        ("全融合", 797.45),
    ], 870, [BLUE, GREEN, ACCENT, GOLD])
    draw.text((72, 266), "代表性组合的平均最优距离", font=font(28, True), fill=INK)
    simple_table(draw, 800, 300, [240, 150, 150, 170], [
        ["组合", "最优距离", "运行时间(s)", "稳定性 CV"],
        ["遗传 + 2-opt", "795.23", "39.85", "0.48%"],
        ["全融合", "797.45", "39.71", "0.48%"],
        ["自适应 + 2-opt", "797.68", "43.76", "0.32%"],
        ["2-opt", "798.22", "44.06", "0.26%"],
    ], row_h=52, size=20)
    card(draw, (72, 590, 460, 770), "关键发现 1", "排名前四的方案全部包含 2-opt，说明它是提升路径质量和稳定性的决定性因素。", GREEN)
    card(draw, (560, 590, 1034, 770), "关键发现 2", "GA + 2-opt 以 795.23 取得综合最优，验证了“全局探索 + 局部强化”的协同最有效。", ACCENT)
    card(draw, (1062, 590, 1534, 770), "关键发现 3", "全融合方案没有拿到第一，但兼顾了解质量、时间和系统完整性，适合作为论文系统方案展示。", BLUE)
    footer(draw, 12)
    return img


def slide13():
    img, draw = base_slide()
    header(draw, "综合结论", "论文最重要的实验结论：2-opt 是关键因素，GA + 2-opt 是最优组合", "这一页直接对应论文第五章和第六章的核心结论。")
    card(draw, (72, 292, 476, 732), "主要结论", "1. 基础 ACO 能够有效求解 TSP，但存在慢收敛、局部最优和参数敏感问题。\n2. 2-opt 是最关键的改进策略。\n3. 遗传算法 + 2-opt 取得综合最优。\n4. 多策略简单叠加并不一定更优。", ACCENT)
    card(draw, (576, 292, 1012, 732), "创新点", "1. 提出融合多种改进思路的混合蚁群算法。\n2. 设计了自适应参数调整机制。\n3. 实现了遗传算法与蚁群算法的结合。\n4. 开发了可视化 TSP 求解系统。", GREEN)
    card(draw, (1040, 292, 1534, 732), "论文启示", "局部搜索的重要性非常突出；真正有效的混合优化应强调协同，而不是把更多策略机械堆在一起。\n\n从论文结果看，改进策略的价值并不只在“更短”，也体现在更稳定、更适合系统实现与展示。", BLUE)
    footer(draw, 13)
    return img


def slide14():
    img, draw = base_slide()
    header(draw, "不足与展望", "论文已证明方法有效，但在规模扩展、理论分析和标准化测试方面仍有提升空间", "答辩中这一页建议讲得克制，体现你对工作边界和后续方向的清醒认识。")
    card(draw, (72, 292, 514, 742), "当前不足", "1. 问题规模继续增大时，整体运行时间仍会明显增加。\n2. 自适应参数机制仍不够完善，仍需结合具体问题调参。\n3. 暂不支持 TSPLIB 等标准实例直接导入。\n4. 对混合算法收敛性与作用机理的理论分析还不充分。", ACCENT)
    card(draw, (548, 292, 1002, 742), "算法改进方向", "1. 研究 3-opt、Lin-Kernighan 等更强局部搜索。\n2. 引入并行计算提升大规模实例效率。\n3. 探索强化学习等更智能的动态参数优化方法。", GREEN)
    card(draw, (1036, 292, 1534, 742), "系统与应用拓展", "1. 增加 TSPLIB 支持，方便标准化对比。\n2. 丰富热力图、箱线图和动态过程展示。\n3. 拓展到车辆路径、作业调度等其他组合优化问题。", BLUE)
    footer(draw, 14)
    return img


def slide15():
    img, draw = base_slide(True)
    draw.text((72, 224), "感谢各位老师聆听", font=font(56, True), fill=WHITE)
    draw.text((72, 304), "恳请批评指正", font=font(30), fill="#D8E0E6")
    art = Image.open(COVER_IMAGE).convert("RGB")
    art = ImageOps.fit(art, (560, 560), method=Image.Resampling.LANCZOS)
    img.paste(art, (944, 156))
    rounded(draw, (944, 730, 1504, 804), "#1D2B36", outline="#314250", width=2, radius=22)
    tw = draw.textlength("Question & Answer", font=font(28, True))
    draw.text((944 + (560 - tw) / 2, 750), "Question & Answer", font=font(28, True), fill=WHITE)
    footer(draw, 15, True)
    return img


SLIDES = [
    slide1, slide2, slide3, slide4, slide5,
    slide6, slide7, slide8, slide9, slide10,
    slide11, slide12, slide13, slide14, slide15,
]


def make_contact_sheet(paths: List[Path], out_path: Path):
    cols = 3
    thumb_w = 480
    thumb_h = 270
    gap = 24
    rows = math.ceil(len(paths) / cols)
    canvas = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * thumb_h + (rows + 1) * gap), "#ECE6DB")
    for i, path in enumerate(paths):
        im = Image.open(path).convert("RGB")
        im = ImageOps.fit(im, (thumb_w, thumb_h), method=Image.Resampling.LANCZOS)
        x = gap + (i % cols) * (thumb_w + gap)
        y = gap + (i // cols) * (thumb_h + gap)
        canvas.paste(im, (x, y))
    canvas.save(out_path)


def main():
    paths = []
    for i, fn in enumerate(SLIDES, 1):
        img = fn()
        path = OUT_DIR / f"slide_{i:02d}.png"
        img.save(path)
        paths.append(path)
    make_contact_sheet(paths, OUT_DIR / "contact_sheet.png")


if __name__ == "__main__":
    main()
