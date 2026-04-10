#!/usr/bin/env python3
"""Build an HTML evaluation report from template generation results.

Reads evaluation metadata and scores, generates a self-contained HTML report
with embedded images, template inventory, and quality statistics.

Usage:
    python build_report.py                      # Build from test/results/
    python build_report.py --output report.html  # Custom output path
"""

import argparse
import base64
import json
import os
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "test" / "results"
REPORT_DIR = PROJECT_DIR / "report"

TEMPLATE_INFO = {
    # L: 生活与娱乐 — 风格化
    "L01": {"name": "Chibi Cartoon", "cat": "L·Stylization", "pri": "P0", "kw": "chibi, Q版, cartoon"},
    "L02": {"name": "3D Pixar Animation", "cat": "L·Stylization", "pri": "P0", "kw": "3D, Pixar, Disney"},
    "L03": {"name": "Comic / Manga", "cat": "L·Stylization", "pri": "P0", "kw": "comic, manga, 漫画"},
    "L04": {"name": "Sketch / Pencil", "cat": "L·Stylization", "pri": "P0", "kw": "sketch, 素描, pencil"},
    "L05": {"name": "Clay / Claymation", "cat": "L·Stylization", "pri": "P0", "kw": "clay, 黏土, stop-motion"},
    "L06": {"name": "80s Retro Animation", "cat": "L·Stylization", "pri": "P0", "kw": "80s, retro, synthwave"},
    "L07": {"name": "Retro-Futurism", "cat": "L·Stylization", "pri": "P0", "kw": "retro-future, space age"},
    "L08": {"name": "Ukiyo-e / Chinese Painting", "cat": "L·Stylization", "pri": "P0", "kw": "ukiyo-e, 国风, 古风"},
    "L09": {"name": "Watercolor Portrait", "cat": "L·Stylization", "pri": "P0", "kw": "watercolor, 水彩"},
    "L10": {"name": "K-Pop Star", "cat": "L·Stylization", "pri": "P0", "kw": "K-Pop, 韩风, idol"},
    "L11": {"name": "Imperial / Royal", "cat": "L·Stylization", "pri": "P0", "kw": "imperial, 帝王, royal"},
    "L12": {"name": "90s Yearbook", "cat": "L·Stylization", "pri": "P0", "kw": "90s, yearbook, 毕业照"},
    "L13": {"name": "High Fashion", "cat": "L·Stylization", "pri": "P0", "kw": "fashion, vogue, editorial"},
    "L14": {"name": "Cyberpunk Portrait", "cat": "L·Stylization", "pri": "P0", "kw": "cyberpunk, neon, 赛博朋克"},
    "L15": {"name": "Oil Painting / Classical", "cat": "L·Stylization", "pri": "P0", "kw": "oil painting, 油画, classical"},
    "L16": {"name": "Pixel Art", "cat": "L·Stylization", "pri": "P0", "kw": "pixel art, 像素, 8-bit"},
    "L17": {"name": "Flat / Vector Illustration", "cat": "L·Stylization", "pri": "P0", "kw": "flat, vector, 平面插画"},
    "L18": {"name": "Anime / 二次元", "cat": "L·Stylization", "pri": "P0", "kw": "anime, 二次元, 动漫"},
    "L19": {"name": "Wool Felt / Needle Felt", "cat": "L·Stylization", "pri": "P0", "kw": "wool felt, 羊毛毡, felted"},
    "L20": {"name": "Colored Pencil", "cat": "L·Stylization", "pri": "P0", "kw": "colored pencil, 彩铅, crayon"},
    "L21": {"name": "Pop Art", "cat": "L·Stylization", "pri": "P0", "kw": "pop art, 波普, Warhol"},
    "L22": {"name": "Miniature / Diorama", "cat": "L·Stylization", "pri": "P0", "kw": "miniature, 微缩景观, diorama"},
    "L23": {"name": "Children's Drawing", "cat": "L·Stylization", "pri": "P0", "kw": "children drawing, 儿童画"},
    "L24": {"name": "Game CG / Thick Paint", "cat": "L·Stylization", "pri": "P0", "kw": "game CG, 厚涂, digital painting"},
    "L25": {"name": "Vaporwave", "cat": "L·Stylization", "pri": "P0", "kw": "vaporwave, 蒸汽波, aesthetic"},
    "L26": {"name": "Printmaking / Woodblock", "cat": "L·Stylization", "pri": "P0", "kw": "printmaking, 版画, woodblock"},
    "L27": {"name": "Fine Brush / Gongbi", "cat": "L·Stylization", "pri": "P0", "kw": "gongbi, 工笔, 新工笔"},
    "L28": {"name": "Pen Sketch / Simple Line", "cat": "L·Stylization", "pri": "P0", "kw": "pen sketch, 简笔画, line drawing"},
    "L29": {"name": "Dark Fairy Tale", "cat": "L·Stylization", "pri": "P0", "kw": "dark fairy tale, 暗黑童话, gothic"},
    # L: 生活与娱乐 — 写真/人像
    "L30": {"name": "Studio Photoshoot", "cat": "L·Portrait", "pri": "P0", "kw": "photoshoot, 写真, studio"},
    "L31": {"name": "ID Photo", "cat": "L·Portrait", "pri": "P0", "kw": "ID photo, 证件照, passport"},
    "L32": {"name": "Emoji / Sticker Pack", "cat": "L·Portrait", "pri": "P0", "kw": "emoji, sticker, 表情包"},
    "L33": {"name": "Avatar / Profile Picture", "cat": "L·Portrait", "pri": "P0", "kw": "avatar, 头像, profile"},
    "L34": {"name": "Film / Cinematic Portrait", "cat": "L·Portrait", "pri": "P0", "kw": "film, 电影写真, cinematic"},
    "L35": {"name": "Dreamy / Hazy Portrait", "cat": "L·Portrait", "pri": "P0", "kw": "dreamy, 朦胧, hazy"},
    "L36": {"name": "Indoor Scene Portrait", "cat": "L·Portrait", "pri": "P0", "kw": "indoor, 室内侧拍, 餐厅复古"},
    "L37": {"name": "Dark Mood Portrait", "cat": "L·Portrait", "pri": "P0", "kw": "dark mood, 暗调, low-key"},
    "L38": {"name": "Iconic Location Shot", "cat": "L·Portrait", "pri": "P0", "kw": "红墙, 中天门, 摩崖造像"},
    "L39": {"name": "Spring Floral Portrait", "cat": "L·Portrait", "pri": "P0", "kw": "spring, 樱花, 春日写真"},
    "L40": {"name": "Natural Light & Shadow", "cat": "L·Portrait", "pri": "P0", "kw": "dappled, 斑驳树影, 阳光"},
    "L41": {"name": "Sunset / Golden Hour", "cat": "L·Portrait", "pri": "P0", "kw": "sunset, 日落, golden hour"},
    "L42": {"name": "Retro Film & Polaroid", "cat": "L·Portrait", "pri": "P0", "kw": "polaroid, 拍立得, 车内胶片"},
    "L43": {"name": "Winter Snow Portrait", "cat": "L·Portrait", "pri": "P0", "kw": "snow, 雪地, 冬季写真"},
    "L44": {"name": "Beach & Underwater", "cat": "L·Portrait", "pri": "P0", "kw": "beach, 海边, underwater"},
    "L45": {"name": "Fantasy / Magical Scene", "cat": "L·Portrait", "pri": "P0", "kw": "magic, 魔法学院, fantasy"},
    "L46": {"name": "Social Media / Street Style", "cat": "L·Portrait", "pri": "P0", "kw": "OOTD, Plog, 网感头像"},
    "L48": {"name": "Photo Grid Layout", "cat": "L·Portrait", "pri": "P0", "kw": "三宫格, grid, triptych"},
    # L: 生活与娱乐 — 萌宠/宝宝
    "L50": {"name": "Pet Stylization", "cat": "L·Pets", "pri": "P0", "kw": "pet, 萌宠, kawaii"},
    "L51": {"name": "Baby Comic Grid", "cat": "L·Pets", "pri": "P0", "kw": "baby, 宝宝, comic grid"},
    "L52": {"name": "Pet VOGUE Magazine", "cat": "L·Pets", "pri": "P0", "kw": "pet magazine, VOGUE"},
    "L53": {"name": "Pet Costume Play", "cat": "L·Pets", "pri": "P0", "kw": "pet costume, 宠物入狱, mugshot"},
    "L54": {"name": "Pet Humanization", "cat": "L·Pets", "pri": "P0", "kw": "pet human, 宠物拟人"},
    # L: 生活与娱乐 — 换装/编辑
    "L60": {"name": "Outfit Change", "cat": "L·Editing", "pri": "P1", "kw": "outfit, 换装, try-on"},
    "L61": {"name": "Hairstyle Change", "cat": "L·Editing", "pri": "P1", "kw": "hairstyle, 发型, haircut"},
    "L62": {"name": "Background Change", "cat": "L·Editing", "pri": "P1", "kw": "background, 换背景"},
    "L63": {"name": "Image Outpainting", "cat": "L·Editing", "pri": "P1", "kw": "outpaint, 扩图, expand"},
    "L64": {"name": "Object Removal", "cat": "L·Editing", "pri": "P1", "kw": "remove, 消除, erase"},
    "L65": {"name": "Image Enhancement", "cat": "L·Editing", "pri": "P1", "kw": "enhance, 变清晰, sharpen"},
    # M: 日常工作与自媒体
    "M01": {"name": "Social Media Post", "cat": "M·Media", "pri": "P1", "kw": "social media, quote, 配图"},
    "M02": {"name": "Poster Design", "cat": "M·Media", "pri": "P1", "kw": "poster, 海报, flyer"},
    "M03": {"name": "Storyboard", "cat": "M·Media", "pri": "P1", "kw": "storyboard, 分镜, comic strip"},
    "M04": {"name": "Handwritten Poster", "cat": "M·Media", "pri": "P1", "kw": "手抄报, bulletin"},
    "M05": {"name": "Illustration", "cat": "M·Media", "pri": "P1", "kw": "illustration, 插画"},
    "M06": {"name": "YouTube Thumbnail", "cat": "M·Media", "pri": "P2", "kw": "YouTube, thumbnail, 缩略图"},
    "M07": {"name": "Educational Visual", "cat": "M·Media", "pri": "P2", "kw": "educational, infographic, 教育"},
    "M08": {"name": "Picture Book Illustration", "cat": "M·Media", "pri": "P1", "kw": "picture book, 绘本, storybook"},
    # P: 专业设计
    "P01": {"name": "E-commerce Main Image", "cat": "P·Design", "pri": "P1", "kw": "e-commerce, 电商, product"},
    "P02": {"name": "Sticker Set Design", "cat": "P·Design", "pri": "P1", "kw": "sticker set, 贴纸集"},
    "P03": {"name": "Interior Design", "cat": "P·Design", "pri": "P1", "kw": "interior, 家装, room"},
    "P04": {"name": "Logo Design", "cat": "P·Design", "pri": "P1", "kw": "logo, 标志, brand"},
    "P05": {"name": "Merchandise Design", "cat": "P·Design", "pri": "P1", "kw": "merchandise, 手办, figure"},
    "P06": {"name": "Coloring Book Page", "cat": "P·Design", "pri": "P1", "kw": "coloring, 涂色, line art"},
    "P07": {"name": "Game Asset Design", "cat": "P·Design", "pri": "P2", "kw": "game, 游戏, character design"},
    "P08": {"name": "Product Marketing Design", "cat": "P·Design", "pri": "P2", "kw": "marketing, 营销, ad campaign"},
}


def image_to_base64(path: str, max_dim: int = 800, quality: int = 80) -> str | None:
    """Convert image to compressed JPEG base64 data URI for HTML embedding."""
    if not os.path.exists(path):
        return None
    try:
        from PIL import Image
        import io
        img = Image.open(path)
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        data = buf.getvalue()
        return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"
    except ImportError:
        pass
    with open(path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(path)[1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}
    mime_type = mime.get(ext.lstrip("."), "image/png")
    return f"data:{mime_type};base64,{base64.b64encode(data).decode()}"


def load_scores() -> dict:
    scores_path = RESULTS_DIR / "scores.json"
    if scores_path.exists():
        with open(scores_path) as f:
            return json.load(f)
    return {}


def load_meta() -> dict:
    meta_path = RESULTS_DIR / "evaluation-meta.json"
    if meta_path.exists():
        with open(meta_path) as f:
            return json.load(f)
    return {}


def build_html(output_path: str = None):
    if output_path is None:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = str(REPORT_DIR / "template-report.html")

    scores = load_scores()
    meta = load_meta()

    inventory_rows = []
    for tid, info in sorted(TEMPLATE_INFO.items()):
        score_data = scores.get(tid, {}).get("scores", {})
        overall = score_data.get("overall", "—")
        if isinstance(overall, (int, float)):
            overall = f"{overall:.1f}"

        has_image = False
        image_html = ""
        if tid in meta:
            entries = meta[tid]
            if isinstance(entries, dict):
                entries = [entries]
            for run in entries:
                if isinstance(run, dict) and run.get("success") and run.get("output"):
                    b64 = image_to_base64(run["output"])
                    if b64:
                        image_html = f'<img src="{b64}" class="thumb" />'
                        has_image = True
                        break

        if not has_image:
            result_dir = RESULTS_DIR / tid
            if result_dir.exists():
                for img_file in sorted(result_dir.glob("*.png")):
                    b64 = image_to_base64(str(img_file))
                    if b64:
                        image_html = f'<img src="{b64}" class="thumb" />'
                        has_image = True
                        break

        status = "generated" if has_image else "pending"
        inventory_rows.append(f"""
        <tr class="{status}">
            <td>{tid}</td>
            <td>{info['name']}</td>
            <td>{info['cat']}</td>
            <td><span class="badge {info['pri'].lower()}">{info['pri']}</span></td>
            <td class="kw">{info['kw']}</td>
            <td class="score">{overall}</td>
            <td class="preview">{image_html if has_image else '<span class="no-img">—</span>'}</td>
        </tr>""")

    scored_templates = [
        (tid, s["scores"]["overall"]) for tid, s in scores.items()
        if "overall" in s.get("scores", {})
    ]
    avg_overall = sum(s for _, s in scored_templates) / len(scored_templates) if scored_templates else 0
    max_template = max(scored_templates, key=lambda x: x[1]) if scored_templates else ("—", 0)
    min_template = min(scored_templates, key=lambda x: x[1]) if scored_templates else ("—", 0)

    def _meta_entries(tid):
        entries = meta.get(tid, [])
        if isinstance(entries, dict):
            return [entries]
        return entries

    total_generated = sum(
        1 for tid in TEMPLATE_INFO
        if tid in meta and any(r.get("success") for r in _meta_entries(tid) if isinstance(r, dict))
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Image Gen Templates — Evaluation Report</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #0f0f0f; color: #e0e0e0; padding: 2rem; }}
h1 {{ font-size: 2rem; margin-bottom: 0.5rem; color: #fff; }}
h2 {{ font-size: 1.4rem; margin: 2rem 0 1rem; color: #ccc; border-bottom: 1px solid #333; padding-bottom: 0.5rem; }}
.subtitle {{ color: #888; margin-bottom: 2rem; }}
.stats {{ display: flex; gap: 2rem; margin: 1.5rem 0; flex-wrap: wrap; }}
.stat-card {{ background: #1a1a1a; border: 1px solid #333; border-radius: 12px;
  padding: 1.2rem 1.5rem; min-width: 180px; }}
.stat-card .label {{ font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }}
.stat-card .value {{ font-size: 1.8rem; font-weight: 700; color: #4fc3f7; margin-top: 0.3rem; }}
.stat-card .detail {{ font-size: 0.85rem; color: #666; margin-top: 0.2rem; }}
table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
th {{ text-align: left; padding: 0.8rem; background: #1a1a1a; color: #aaa;
  font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;
  border-bottom: 2px solid #333; }}
td {{ padding: 0.7rem 0.8rem; border-bottom: 1px solid #222; vertical-align: middle; }}
tr:hover {{ background: #1a1a1a; }}
.kw {{ font-size: 0.8rem; color: #888; max-width: 200px; }}
.score {{ font-weight: 700; color: #4fc3f7; text-align: center; }}
.badge {{ padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
.badge.p0 {{ background: #1b5e20; color: #a5d6a7; }}
.badge.p1 {{ background: #e65100; color: #ffcc80; }}
.thumb {{ width: 80px; height: 80px; object-fit: cover; border-radius: 8px; border: 1px solid #333; }}
.no-img {{ color: #555; }}
.preview {{ text-align: center; }}
.generated td:first-child {{ border-left: 3px solid #4caf50; }}
.pending td:first-child {{ border-left: 3px solid #555; }}
.footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #333; color: #555; font-size: 0.8rem; }}
</style>
</head>
<body>
<h1>Image Generation — High-Heat Template Report</h1>
<p class="subtitle">74 curated templates for Gemini 3.1 Flash Image (Nano Banana 2) — Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

<div class="stats">
  <div class="stat-card">
    <div class="label">Total Templates</div>
    <div class="value">{len(TEMPLATE_INFO)}</div>
    <div class="detail">3 categories (L/M/P)</div>
  </div>
  <div class="stat-card">
    <div class="label">Generated</div>
    <div class="value">{total_generated}/{len(TEMPLATE_INFO)}</div>
    <div class="detail">templates with images</div>
  </div>
  <div class="stat-card">
    <div class="label">Avg Overall Score</div>
    <div class="value">{avg_overall:.2f}</div>
    <div class="detail">{len(scored_templates)} scored</div>
  </div>
  <div class="stat-card">
    <div class="label">Best Template</div>
    <div class="value">{max_template[1]:.1f}</div>
    <div class="detail">{max_template[0]}</div>
  </div>
  <div class="stat-card">
    <div class="label">Needs Attention</div>
    <div class="value">{min_template[1]:.1f}</div>
    <div class="detail">{min_template[0]}</div>
  </div>
</div>

<h2>Template Inventory</h2>
<table>
<thead>
<tr><th>ID</th><th>Template</th><th>Category</th><th>Priority</th><th>Keywords</th><th>Score</th><th>Preview</th></tr>
</thead>
<tbody>
{''.join(inventory_rows)}
</tbody>
</table>

<div class="footer">
  <p>Report generated by image-gen-templates build_report.py</p>
  <p>Model: Gemini 3.1 Flash Image (Nano Banana 2) via Compass LLM Proxy</p>
</div>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Report saved to {output_path}")

    inventory_json = []
    for tid, info in sorted(TEMPLATE_INFO.items()):
        score_data = scores.get(tid, {}).get("scores", {})
        inventory_json.append({
            "id": tid,
            "name": info["name"],
            "category": info["cat"],
            "priority": info["pri"],
            "keywords": info["kw"],
            "scores": score_data,
            "has_sample": tid in meta and any(r.get("success") for r in _meta_entries(tid) if isinstance(r, dict)),
        })

    json_path = REPORT_DIR / "template-inventory.json"
    with open(json_path, "w") as f:
        json.dump(inventory_json, f, indent=2, ensure_ascii=False)
    print(f"Inventory JSON saved to {json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build evaluation report")
    parser.add_argument("--output", help="Output HTML file path")
    args = parser.parse_args()
    build_html(args.output)
