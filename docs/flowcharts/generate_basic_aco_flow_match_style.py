from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont


OUT_PATH = Path("docs/flowcharts/thesis_basic_aco_flow_optimized.png")

WIDTH = 1400
HEIGHT = 1700
BG = "#FFFFFF"
BOX_FILL = "#EAF2FB"
BOX_BORDER = "#8DB3E2"
DIAMOND_FILL = "#FFF2CC"
DIAMOND_BORDER = "#D4A24A"
ARROW = "#6B7280"
TEXT = "#1F2937"
BLACK = "#222222"


def load_font(size: int, bold: bool = False):
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


def draw_centered_text(draw, box, text, font, fill=TEXT, spacing=10):
    x1, y1, x2, y2 = box
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x1 + (x2 - x1 - tw) / 2
    ty = y1 + (y2 - y1 - th) / 2 - 2
    draw.multiline_text((tx, ty), text, font=font, fill=fill, spacing=spacing, align="center")


def rounded_box(draw, box, text, font=FONT, radius=28):
    draw.rounded_rectangle(box, radius=radius, fill=BOX_FILL, outline=BOX_BORDER, width=4)
    draw_centered_text(draw, box, text, font)


def diamond(draw, center, w, h, text, font=FONT_SMALL):
    cx, cy = center
    points = [
        (cx, cy - h // 2),
        (cx + w // 2, cy),
        (cx, cy + h // 2),
        (cx - w // 2, cy),
    ]
    draw.polygon(points, fill=DIAMOND_FILL, outline=DIAMOND_BORDER, width=4)
    draw_centered_text(
        draw,
        (cx - w // 2 + 18, cy - h // 2 + 14, cx + w // 2 - 18, cy + h // 2 - 14),
        text,
        font,
    )


def arrow_head(draw, start, end, color=ARROW, size=18):
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


def poly_arrow(draw, points, color=ARROW, width=6):
    draw.line(points, fill=color, width=width, joint="curve")
    arrow_head(draw, points[-2], points[-1], color=color)


def label(draw, pos, text):
    bbox = draw.textbbox((0, 0), text, font=FONT_LABEL)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x, y = pos
    draw.rounded_rectangle(
        (x - tw / 2 - 10, y - th / 2 - 4, x + tw / 2 + 10, y + th / 2 + 4),
        radius=10,
        fill=BG,
    )
    draw.text((x - tw / 2, y - th / 2 - 1), text, font=FONT_LABEL, fill=TEXT)


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    cx = WIDTH // 2
    box_w = 520
    box_h = 98

    start_center = (cx, 70)
    end_center = (cx, 1600)

    box1 = (cx - box_w // 2, 140, cx + box_w // 2, 140 + box_h)
    d1 = (cx, 335, 250, 156)
    box2 = (cx - box_w // 2, 450, cx + box_w // 2, 450 + box_h)
    box3 = (cx - box_w // 2, 610, cx + box_w // 2, 610 + box_h)
    box4 = (cx - 150, 770, cx + 150, 770 + 98)
    box5 = (cx - box_w // 2, 1040, cx + box_w // 2, 1040 + box_h)

    draw.ellipse((start_center[0] - 18, start_center[1] - 18, start_center[0] + 18, start_center[1] + 18), fill=BLACK)
    rounded_box(draw, box1, "初始化参数与信息素")
    diamond(draw, (d1[0], d1[1]), d1[2], d1[3], "继续迭代?")
    rounded_box(draw, box2, "按概率构建路径")
    rounded_box(draw, box3, "计算路径并更新最优解")
    rounded_box(draw, box4, "更新信息素", font=FONT_SMALL)
    rounded_box(draw, box5, "输出最优路径")

    poly_arrow(draw, [(cx, 92), (cx, box1[1])])
    poly_arrow(draw, [(cx, box1[3]), (cx, d1[1] - d1[3] // 2)])
    poly_arrow(draw, [(cx, d1[1] + d1[3] // 2), (cx, box2[1])])
    label(draw, (cx - 56, 410), "是")
    poly_arrow(draw, [(cx, box2[3]), (cx, box3[1])])
    poly_arrow(draw, [(cx, box3[3]), (cx, box4[1])])
    poly_arrow(draw, [(cx, box4[3]), (cx, box5[1])])
    poly_arrow(draw, [(cx, box5[3]), (cx, 1568)])

    d1_left = (d1[0] - d1[2] // 2, d1[1])
    box5_left_mid = (box5[0], (box5[1] + box5[3]) // 2)
    poly_arrow(draw, [d1_left, (150, d1_left[1]), (150, box5_left_mid[1]), box5_left_mid])
    label(draw, (200, 325), "否")

    box4_right_mid = (box4[2], (box4[1] + box4[3]) // 2)
    d1_right = (d1[0] + d1[2] // 2, d1[1])
    poly_arrow(draw, [box4_right_mid, (1050, box4_right_mid[1]), (1050, d1_right[1]), d1_right])

    draw.ellipse((end_center[0] - 28, end_center[1] - 28, end_center[0] + 28, end_center[1] + 28), fill=BLACK)
    draw.ellipse((end_center[0] - 18, end_center[1] - 18, end_center[0] + 18, end_center[1] + 18), fill=BG)
    draw.ellipse((end_center[0] - 9, end_center[1] - 9, end_center[0] + 9, end_center[1] + 9), fill=BLACK)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT_PATH, dpi=(220, 220), optimize=True)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
