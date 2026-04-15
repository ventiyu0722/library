#!/usr/bin/env python3
"""Build the effect table CSV and ordered image folder matching the PDF layout."""

import csv
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "test" / "results"
OUTPUT_DIR = Path.home() / "Desktop" / "模板效果表"
IMAGES_DIR = OUTPUT_DIR / "output_images"

ROWS = [
    # (序号, 场景大类, 玩法, template_id, input_query, photo_type)
    # photo_type: "selfie", "pet", "baby", "room", None (text-only)

    # 1. 生活与娱乐-风格化 (29)
    (1, "1.生活与娱乐-风格化", "Q版卡通", "L01", "把我的照片变成Q版卡通风格", "selfie"),
    (2, "1.生活与娱乐-风格化", "3D皮克斯", "L02", "把我变成3D皮克斯动画角色", "selfie"),
    (3, "1.生活与娱乐-风格化", "漫画", "L03", "把我的照片转成漫画风格", "selfie"),
    (4, "1.生活与娱乐-风格化", "素描", "L04", "帮我画一张素描肖像", "selfie"),
    (5, "1.生活与娱乐-风格化", "黏土", "L05", "把我变成黏土动画角色", "selfie"),
    (6, "1.生活与娱乐-风格化", "80年代复古", "L06", "把我变成80年代复古动画风格", "selfie"),
    (7, "1.生活与娱乐-风格化", "复古科幻", "L07", "把我变成复古科幻风格", "selfie"),
    (8, "1.生活与娱乐-风格化", "浮世绘/国风", "L08", "把我的照片变成浮世绘国风", "selfie"),
    (9, "1.生活与娱乐-风格化", "水彩", "L09", "帮我画一张水彩肖像", "selfie"),
    (10, "1.生活与娱乐-风格化", "K-Pop", "L10", "把我变成K-Pop偶像风格", "selfie"),
    (11, "1.生活与娱乐-风格化", "帝王", "L11", "把我变成帝王画像风格", "selfie"),
    (12, "1.生活与娱乐-风格化", "90年代毕业照", "L12", "把我变成90年代毕业照风格", "selfie"),
    (13, "1.生活与娱乐-风格化", "高级时尚", "L13", "把我变成高级时尚杂志风格", "selfie"),
    (14, "1.生活与娱乐-风格化", "赛博朋克", "L14", "把我变成赛博朋克风格", "selfie"),
    (15, "1.生活与娱乐-风格化", "油画", "L15", "把我变成古典油画风格", "selfie"),
    (16, "1.生活与娱乐-风格化", "像素", "L16", "把我变成像素风格", "selfie"),
    (17, "1.生活与娱乐-风格化", "扁平插画", "L17", "把我变成扁平矢量插画风格", "selfie"),
    (18, "1.生活与娱乐-风格化", "二次元", "L18", "把我变成二次元动漫风格", "selfie"),
    (19, "1.生活与娱乐-风格化", "羊毛毡", "L19", "把我变成羊毛毡风格", "selfie"),
    (20, "1.生活与娱乐-风格化", "彩铅", "L20", "把我变成彩铅画风格", "selfie"),
    (21, "1.生活与娱乐-风格化", "波普", "L21", "把我变成波普艺术风格", "selfie"),
    (22, "1.生活与娱乐-风格化", "微缩景观", "L22", "把我变成微缩景观小人国风格", "selfie"),
    (23, "1.生活与娱乐-风格化", "儿童画", "L23", "把我变成儿童画风格", "selfie"),
    (24, "1.生活与娱乐-风格化", "游戏CG厚涂", "L24", "把我变成游戏CG厚涂风格", "selfie"),
    (25, "1.生活与娱乐-风格化", "蒸汽波", "L25", "把我变成蒸汽波风格", "selfie"),
    (26, "1.生活与娱乐-风格化", "版画", "L26", "把我变成版画风格", "selfie"),
    (27, "1.生活与娱乐-风格化", "工笔", "L27", "把我变成工笔画风格", "selfie"),
    (28, "1.生活与娱乐-风格化", "简笔画", "L28", "把我变成简笔画风格", "selfie"),
    (29, "1.生活与娱乐-风格化", "暗黑童话", "L29", "把我变成暗黑童话风格", "selfie"),

    # 1. 生活与娱乐-写真生成 (18)
    (30, "1.生活与娱乐-写真生成", "写真", "L30", "帮我拍一张专业写真", "selfie"),
    (31, "1.生活与娱乐-写真生成", "证件照", "L31", "帮我生成一张证件照", "selfie"),
    (32, "1.生活与娱乐-写真生成", "表情包", "L32", "用我的照片做一套表情包", "selfie"),
    (33, "1.生活与娱乐-写真生成", "头像", "L33", "帮我生成一个个性头像", "selfie"),
    (34, "1.生活与娱乐-写真生成", "电影写真", "L34", "把我的照片变成电影写真风格", "selfie"),
    (35, "1.生活与娱乐-写真生成", "朦胧肖像", "L35", "帮我生成朦胧梦幻风格的肖像", "selfie"),
    (36, "1.生活与娱乐-写真生成", "室内侧拍", "L36", "帮我生成一张室内侧拍写真", "selfie"),
    (37, "1.生活与娱乐-写真生成", "暗调情绪", "L37", "帮我拍一张暗调情绪写真", "selfie"),
    (38, "1.生活与娱乐-写真生成", "红墙拍照", "L38", "帮我在红墙前拍一张照片", "selfie"),
    (39, "1.生活与娱乐-写真生成", "春日樱花写真", "L39", "帮我拍一张樱花春日写真", "selfie"),
    (40, "1.生活与娱乐-写真生成", "斑驳树影", "L40", "帮我拍一张斑驳树影光影写真", "selfie"),
    (41, "1.生活与娱乐-写真生成", "日落时分", "L41", "帮我拍一张日落时分的写真", "selfie"),
    (42, "1.生活与娱乐-写真生成", "车内胶片拍立得", "L42", "帮我生成一张车内胶片拍立得风格照片", "selfie"),
    (43, "1.生活与娱乐-写真生成", "冬季雪景", "L43", "帮我拍一张冬天下雪的写真", "selfie"),
    (44, "1.生活与娱乐-写真生成", "海边写真", "L44", "帮我拍一张海边写真", "selfie"),
    (45, "1.生活与娱乐-写真生成", "魔法学院", "L45", "把我变成魔法学院的学生", "selfie"),
    (46, "1.生活与娱乐-写真生成", "网感OOTD", "L46", "帮我拍一张网感OOTD街拍", "selfie"),
    (47, "1.生活与娱乐-写真生成", "樱花三宫格", "L48", "帮我做一张樱花主题三宫格", "selfie"),

    # 1. 生活与娱乐-萌宠/宝宝 (5)
    (48, "1.生活与娱乐-萌宠/宝宝", "萌宠风格化", "L50", "把我的宠物变成萌宠风格化", "pet"),
    (49, "1.生活与娱乐-萌宠/宝宝", "宠物VOGUE杂志", "L52", "帮我的宠物拍一张VOGUE杂志封面", "pet"),
    (50, "1.生活与娱乐-萌宠/宝宝", "宠物入狱", "L53", "帮我的宠物拍一张入狱照", "pet"),
    (51, "1.生活与娱乐-萌宠/宝宝", "宠物拟人", "L54", "把我的宠物拟人化", "pet"),
    (52, "1.生活与娱乐-萌宠/宝宝", "宝宝漫画宫格", "L51", "帮我的宝宝做一张漫画表情宫格", "baby"),

    # 2. 日常工作与自媒体-编辑工具 (6)
    (53, "2.日常工作与自媒体-编辑工具", "换装（换成西装）", "L60", "帮我换装，换成西装", "selfie"),
    (54, "2.日常工作与自媒体-编辑工具", "换发型（短发）", "L61", "帮我换个短发发型", "selfie"),
    (55, "2.日常工作与自媒体-编辑工具", "换背景（沙滩）", "L62", "帮我把背景换成沙滩", "selfie"),
    (56, "2.日常工作与自媒体-编辑工具", "扩图（左右各扩30%）", "L63", "帮我把照片左右各扩展30%", "selfie"),
    (57, "2.日常工作与自媒体-编辑工具", "消除（去掉背景杂物）", "L64", "帮我把背景杂物消除掉", "selfie"),
    (58, "2.日常工作与自媒体-编辑工具", "变清晰", "L65", "帮我把照片变清晰", "selfie"),

    # 2. 日常工作与自媒体-Social Media配图 (1)
    (59, "2.日常工作与自媒体-Social Media配图", "Social Media Post", "M01", "帮我生成一张'Stay Hungry, Stay Foolish'的名言配图", None),

    # 2. 日常工作与自媒体-海报 (4)
    (60, "2.日常工作与自媒体-海报", "Poster Design", "M02", "帮我设计一张春季音乐会海报", None),
    (61, "2.日常工作与自媒体-海报", "Handwritten Poster", "M04", "帮我做一张环保主题手抄报", None),
    (62, "2.日常工作与自媒体-海报", "Illustration", "M05", "帮我画一幅吉卜力风格的浮空岛插画", None),
    (63, "2.日常工作与自媒体-海报", "Picture Book Illustration", "M08", "帮我画一幅小狐狸发现树洞的绘本插画", None),

    # 2. 日常工作与自媒体-动画图/分镜图 (1)
    (64, "2.日常工作与自媒体-动画图/分镜图", "Storyboard", "M03", "帮我画一个4格漫画讲述一天的生活", None),

    # 2. 日常工作与自媒体-YouTube缩略图 (1)
    (65, "2.日常工作与自媒体-YouTube缩略图", "YouTube Thumbnail", "M06", "帮我做一张'AI工具TOP10'的YouTube缩略图", None),

    # 2. 日常工作与自媒体-教育类视觉图 (1)
    (66, "2.日常工作与自媒体-教育类视觉图", "Educational Visual", "M07", "帮我做一张光合作用的教学图", None),

    # 3. 专业设计 (8)
    (67, "3.专业设计", "E-commerce Main Image", "P01", "帮我做一张蜂蜜产品电商头图", None),
    (68, "3.专业设计", "Sticker Set Design", "P02", "用我的照片做一套贴纸集", "selfie"),
    (69, "3.专业设计", "Interior Design", "P03", "帮我把房间设计成北欧简约风", "room"),
    (70, "3.专业设计", "Logo Design", "P04", "帮我设计一个ALPINE品牌的山峰Logo", None),
    (71, "3.专业设计", "Merchandise Design", "P05", "用我的照片做一个手办", "selfie"),
    (72, "3.专业设计", "Coloring Book Page", "P06", "帮我画一页童话涂色书", None),
    (73, "3.专业设计", "Game Asset Design", "P07", "帮我设计一个RPG战斗法师角色", None),
    (74, "3.专业设计", "Product Marketing Design", "P08", "帮我设计一张耳机产品营销图", None),
]

PHOTO_LABEL = {
    "selfie": "[上传自拍照] ",
    "pet": "[上传宠物照] ",
    "baby": "[上传宝宝照] ",
    "room": "[上传房间照] ",
}


def find_image(tid: str) -> str | None:
    d = RESULTS_DIR / tid
    if not d.exists():
        return None
    for ext in ["png", "jpg", "jpeg"]:
        for f in sorted(d.glob(f"*.{ext}")):
            return str(f)
    return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / "效果表.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["序号", "场景大类", "玩法", "模板ID", "input", "output图片文件名"])

        ok = 0
        miss = 0
        for idx, cat, play, tid, query, photo in ROWS:
            full_input = PHOTO_LABEL.get(photo, "") + query
            img = find_image(tid)
            if img:
                fname = f"{idx:02d}_{tid}_{play}.png"
                fname = fname.replace("/", "_").replace("（", "(").replace("）", ")")
                dest = IMAGES_DIR / fname
                shutil.copy2(img, dest)
                writer.writerow([idx, cat, play, tid, full_input, fname])
                ok += 1
            else:
                writer.writerow([idx, cat, play, tid, full_input, "（未生成）"])
                miss += 1

    print(f"CSV saved: {csv_path}")
    print(f"Images: {ok} copied, {miss} missing")
    print(f"Folder: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
