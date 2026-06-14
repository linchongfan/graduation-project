from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


OUT_PATH = Path("docs/flowcharts/thesis_two_opt_flow_optimized.png")

WIDTH = 1400
HEIGHT = 1900
BG = "#FFFFFF"
BOX_FILL = "#EAF2FB"
BOX_BORDER = "#8DB3E2"
DIAMOND_FILL = "#FFF2CC"
DIAMOND_BORDER = "#D4A24A"
ARROW = "#6B7280"
TEXT = "#1F2937"
BLACK = "#222222"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


FONT = load_font(44)
FONT_SMALL = load_font(40)
FONT_LABEL = load_font(34, bold=True)


def draw_centered_text(draw: ImageDraw.ImageDraw, box, text: str, font, fill=TEXT, spacing=10):
    x1, y1, x2, y2 = box
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x1 + (x2 - x1 - tw) / 2
    ty = y1 + (y2 - y1 - th) / 2 - 2
    draw.multiline_text((tx, ty), text, font=font, fill=fill, spacing=spacing, align="center")


def rounded_box(draw: ImageDraw.ImageDraw, box, text: str, font=FONT, radius=28):
    draw.rounded_rectangle(box, radius=radius, fill=BOX_FILL, outline=BOX_BORDER, width=4)
    draw_centered_text(draw, box, text, font)


def diamond(draw: ImageDraw.ImageDraw, center, w: int, h: int, text: str, font=FONT_SMALL):
    cx, cy = center
    points = [
        (cx, cy - h // 2),
        (cx + w // 2, cy),
        (cx, cy + h // 2),
        (cx - w // 2, cy),
    ]
    draw.polygon(points, fill=DIAMOND_FILL, outline=DIAMOND_BORDER, width=4)
    draw_centered_text(draw, (cx - w // 2 + 18, cy - h // 2 + 14, cx + w // 2 - 18, cy + h // 2 - 14), text, font)


def arrow_head(draw: ImageDraw.ImageDraw, start, end, color=ARROW, width=6, size=18):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux = dx / length
    uy = dy / length
    px = -uy
    py = ux
    base_x = end[0] - ux * size
    base_y = end[1] - uy * size
    left = (base_x + px * size * 0.55, base_y + py * size * 0.55)
    right = (base_x - px * size * 0.55, base_y - py * size * 0.55)
    draw.polygon([end, left, right], fill=color)


def poly_arrow(draw: ImageDraw.ImageDraw, points, color=ARROW, width=6):
    draw.line(points, fill=color, width=width, joint="curve")
    arrow_head(draw, points[-2], points[-1], color=color, width=width)


def label(draw: ImageDraw.ImageDraw, pos, text: str):
    bbox = draw.textbbox((0, 0), text, font=FONT_LABEL)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x, y = pos
    pad_x = 10
    pad_y = 4
    box = (x - tw / 2 - pad_x, y - th / 2 - pad_y, x + tw / 2 + pad_x, y + th / 2 + pad_y)
    draw.rounded_rectangle(box, radius=10, fill=BG)
    draw.text((x - tw / 2, y - th / 2 - 1), text, font=FONT_LABEL, fill=TEXT)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    cx = WIDTH // 2
    box_w = 520
    box_h = 98
    tall_h = 124

    nodes = {
        "box1": (cx - box_w // 2, 140, cx + box_w // 2, 140 + box_h),
        "box2": (cx - box_w // 2, 300, cx + box_w // 2, 300 + box_h),
        "box3": (cx - box_w // 2, 460, cx + box_w // 2, 460 + box_h),
        "box4": (cx - box_w // 2, 620, cx + box_w // 2, 620 + box_h),
        "box5": (cx - box_w // 2, 940, cx + box_w // 2, 940 + tall_h),
        "box6": (cx - box_w // 2, 1520, cx + box_w // 2, 1520 + box_h),
    }

    diamonds = {
        "d1": (cx, 820, 250, 156),
        "d2": (cx, 1165, 300, 176),
        "d3": (cx, 1385, 300, 176),
    }

    start_center = (cx, 70)
    end_center = (cx, 1735)

    poly_arrow(draw, [(cx, 92), (cx, 140)])
    poly_arrow(draw, [(cx, nodes["box1"][3]), (cx, nodes["box2"][1])])
    poly_arrow(draw, [(cx, nodes["box2"][3]), (cx, nodes["box3"][1])])
    poly_arrow(draw, [(cx, nodes["box3"][3]), (cx, nodes["box4"][1])])
    poly_arrow(draw, [(cx, nodes["box4"][3]), (cx, diamonds["d1"][1] - diamonds["d1"][3] // 2)])

    poly_arrow(draw, [(cx, diamonds["d1"][1] + diamonds["d1"][3] // 2), (cx, nodes["box5"][1])])
    label(draw, (cx - 56, 900), "是")

    d1_right = (diamonds["d1"][0] + diamonds["d1"][2] // 2, diamonds["d1"][1])
    d2_right = (diamonds["d2"][0] + diamonds["d2"][2] // 2, diamonds["d2"][1])
    poly_arrow(draw, [d1_right, (1010, d1_right[1]), (1010, d2_right[1]), d2_right])
    label(draw, (930, 790), "否")

    poly_arrow(draw, [(cx, nodes["box5"][3]), (cx, diamonds["d2"][1] - diamonds["d2"][3] // 2)])

    d2_left = (diamonds["d2"][0] - diamonds["d2"][2] // 2, diamonds["d2"][1])
    box4_left_mid = (nodes["box4"][0], (nodes["box4"][1] + nodes["box4"][3]) // 2)
    poly_arrow(draw, [d2_left, (210, d2_left[1]), (210, box4_left_mid[1]), box4_left_mid])
    label(draw, (260, 1105), "是")

    poly_arrow(draw, [(cx, diamonds["d2"][1] + diamonds["d2"][3] // 2), (cx, diamonds["d3"][1] - diamonds["d3"][3] // 2)])
    label(draw, (cx - 56, 1275), "否")

    d3_left = (diamonds["d3"][0] - diamonds["d3"][2] // 2, diamonds["d3"][1])
    box2_left_mid = (nodes["box2"][0], (nodes["box2"][1] + nodes["box2"][3]) // 2)
    poly_arrow(draw, [d3_left, (145, d3_left[1]), (145, box2_left_mid[1]), box2_left_mid])
    label(draw, (200, 1325), "是")

    poly_arrow(draw, [(cx, diamonds["d3"][1] + diamonds["d3"][3] // 2), (cx, nodes["box6"][1])])
    label(draw, (cx - 56, 1495), "否")
    poly_arrow(draw, [(cx, nodes["box6"][3]), (cx, 1704)])

    draw.ellipse((start_center[0] - 18, start_center[1] - 18, start_center[0] + 18, start_center[1] + 18), fill=BLACK)

    rounded_box(draw, nodes["box1"], "选取待优化路径")
    rounded_box(draw, nodes["box2"], "置本轮改进标志为否")
    rounded_box(draw, nodes["box3"], "枚举一组不相邻边对")
    rounded_box(draw, nodes["box4"], "计算距离变化量  ΔL")
    diamond(draw, (diamonds["d1"][0], diamonds["d1"][1]), diamonds["d1"][2], diamonds["d1"][3], "ΔL < 0 ?")
    rounded_box(draw, nodes["box5"], "执行路径片段反转\n并置改进标志为是")
    diamond(draw, (diamonds["d2"][0], diamonds["d2"][1]), diamonds["d2"][2], diamonds["d2"][3], "还有未检查的\n边对?")
    diamond(draw, (diamonds["d3"][0], diamonds["d3"][1]), diamonds["d3"][2], diamonds["d3"][3], "本轮是否有\n改进?")
    rounded_box(draw, nodes["box6"], "输出优化后的路径")

    draw.ellipse((end_center[0] - 28, end_center[1] - 28, end_center[0] + 28, end_center[1] + 28), fill=BLACK)
    draw.ellipse((end_center[0] - 18, end_center[1] - 18, end_center[0] + 18, end_center[1] + 18), fill=BG)
    draw.ellipse((end_center[0] - 9, end_center[1] - 9, end_center[0] + 9, end_center[1] + 9), fill=BLACK)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT_PATH, dpi=(220, 220), optimize=True)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
