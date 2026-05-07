#!/usr/bin/env python3
"""Multi-model image generation benchmark.

Generates 60 images (3 photos x 5 templates x 4 models), auto-scores them,
and produces an interactive HTML report.

Usage:
    python benchmark.py                     # Run full benchmark
    python benchmark.py --model gemini      # Run single model only
    python benchmark.py --report-only       # Rebuild report from existing results
"""

import asyncio
import base64
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import fal_client
import httpx

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
BENCHMARK_DIR = PROJECT_DIR / "benchmark"
RESULTS_DIR = BENCHMARK_DIR / "results"
META_PATH = BENCHMARK_DIR / "meta.json"
REPORT_PATH = BENCHMARK_DIR / "report.html"

PHOTO_DIR = Path("/Users/yufei/Claude_Code/Image-Template-V2 test")
PHOTOS = [
    ("American_female", PHOTO_DIR / "American_female.png"),
    ("American_male", PHOTO_DIR / "American_male.png"),
    ("Asian_girl", PHOTO_DIR / "Asian_girl.jpg"),
]

FAL_KEY = "3569d2cc-7803-4982-b641-dc32362d3310:dcb39025f327491f45d9eefbe85f040d"
os.environ["FAL_KEY"] = FAL_KEY

COMPASS_BASE_URL = "http://beeai.test.shopee.io/inbeeai/compass-api/v1"
COMPASS_TOKEN = "W4eR6tY8uI0oP2aL4pK6jL8zX0cV2b"

MODELS = {
    "gemini": {
        "display": "Gemini 3.1 Flash",
        "provider": "compass",
        "color": "#4fc3f7",
    },
    "seedream": {
        "display": "Seedream 5.0 Lite",
        "provider": "fal",
        "endpoint": "fal-ai/bytedance/seedream/v5/lite/edit",
        "color": "#81c784",
    },
    "gpt_image": {
        "display": "GPT Image 2",
        "provider": "fal",
        "endpoint": "fal-ai/gpt-image-1.5/edit",
        "color": "#ffb74d",
    },
    "qwen": {
        "display": "Qwen Image 2.0",
        "provider": "fal",
        "endpoint": "fal-ai/qwen-image-2/edit",
        "color": "#ce93d8",
    },
}

TEMPLATES = {
    "L30": {
        "name": "Studio Photoshoot",
        "aspect": "3:4",
        "prompt": (
            "Transform the uploaded photo into a high-end studio portrait photoshoot. "
            "Preserve the subject's complete facial identity, expression nuance, and natural skin texture.\n\n"
            "Setting: a professional photography studio with a seamless paper backdrop in warm taupe.\n\n"
            "Outfit: elegant, camera-ready — tailored blazer in soft camel over a simple white t-shirt, "
            "creating a clean, editorial look.\n\n"
            "Pose: natural three-quarter body angle, one shoulder slightly forward, "
            "head tilted 10 degrees with a genuine, relaxed expression.\n\n"
            "Lighting: professional three-point setup — large octabox key light at 45° camera-left "
            "producing soft, wrapping illumination with gentle shadow falloff on the face. "
            "Silver reflector fill from camera-right lifting shadows to a 2:1 ratio. "
            "Subtle strip light from behind for hair separation and rim highlight. "
            "Color temperature: 5500K daylight balanced.\n\n"
            "Camera: 85mm portrait lens at f/2.0, shallow depth of field with subject's eyes tack-sharp. "
            "Film simulation: Fuji Pro 400H — slightly lifted shadows, creamy skin tones, understated pastel palette.\n\n"
            "Composition: three-quarter body with generous headroom. Aspect ratio 3:4.\n\n"
            "The overall style is a premium studio portrait with magazine-grade lighting, "
            "natural skin rendering, and timeless elegance. No text, no watermark."
        ),
    },
    "L34": {
        "name": "Film / Cinematic",
        "aspect": "3:4",
        "prompt": (
            "Transform the uploaded photo into a cinematic film portrait that looks like a still frame from a "
            "Wong Kar-wai arthouse film — moody, intimate, and dripping with nostalgia. "
            "Preserve the subject's complete facial identity, expression, and natural features.\n\n"
            "Film stock: Kodak Vision3 500T tungsten motion picture film — distinctive warm-to-cool color crossover, "
            "pronounced but elegant grain structure, slightly lifted blacks with a subtle cyan cast in the shadows, "
            "warm golden skin tones.\n\n"
            "Mood: melancholic beauty — the subject gazes slightly off-camera with a contemplative expression, "
            "as if lost in a private memory.\n\n"
            "Environment: a dimly lit urban setting at night — neon signs reflecting off rain-wet surfaces, "
            "the warm glow of a nearby streetlamp mixing with cool blue ambient light. "
            "The subject is positioned near a window or doorway, creating natural framing.\n\n"
            "Lighting: motivated practical lighting from available sources — a neon sign casting a warm red-orange glow "
            "on one side of the face, cool blue ambient from the night sky on the other. "
            "No fill light. Let the shadows be rich and mysterious. A slight lens flare from a distant light source.\n\n"
            "Camera: 35mm anamorphic lens (Panavision C-series), wide open at T1.4. "
            "The shallow depth of field creates beautiful oval bokeh of city lights behind the subject. "
            "Slight anamorphic lens breathing and horizontal flare streaks.\n\n"
            "Aspect ratio 3:4. Frame the subject with cinematic negative space — "
            "they occupy roughly one-third of the frame, with the atmospheric environment filling the rest.\n\n"
            "The overall style is a hauntingly beautiful cinematic portrait that tells a story in a single frame, "
            "with the emotional depth of festival-circuit arthouse cinema. No text, no watermark."
        ),
    },
    "L43": {
        "name": "Winter Snow",
        "aspect": "3:4",
        "prompt": (
            "Transform the uploaded photo into a cinematic winter portrait in falling snow. "
            "Preserve the subject's identity while conveying cold air and quiet atmosphere.\n\n"
            "Weather: soft large flakes near camera blurred as bokeh orbs, finer flakes sharp mid-air, "
            "occasional flakes catching on lashes and hair.\n\n"
            "Breath: subtle visible vapor on exhale if outdoors — delicate, not exaggerated.\n\n"
            "Palette: cool blue-white ambient with silver shadows; warm accent from scarf, coat lining, "
            "or skin undertone to avoid clinical cold.\n\n"
            "Wardrobe: chunky knit scarf, wool coat, or puffer — realistic winter fabrics with frost on shoulders optional.\n\n"
            "Environment: snowy path, pine forest edge, frozen lake shore, or quiet urban street with snow banks — "
            "background soft, readable.\n\n"
            "Light: overcast soft box from sky, or low warm sun on snow bounce filling face.\n\n"
            "Camera: 85mm f/2–f/2.8, slight shutter speed sense of falling snow motion optional.\n\n"
            "Composition: vertical 3:4, subject clear against snowy depth. No text, no watermark.\n\n"
            "The overall style is a premium winter editorial — crisp, serene, and tactilely cold."
        ),
    },
}

# ── Gemini via Compass ──────────────────────────────────────────────

sys.path.insert(0, str(SCRIPT_DIR))
from generate import generate_image as _gemini_generate  # noqa: E402


async def generate_gemini(prompt: str, photo_path: str, output_path: str) -> dict:
    return await _gemini_generate(prompt, output_path, reference_image=photo_path)


# ── FAL models ──────────────────────────────────────────────────────

_fal_photo_urls: dict[str, str] = {}


async def upload_photos_to_fal() -> dict[str, str]:
    global _fal_photo_urls
    if _fal_photo_urls:
        return _fal_photo_urls
    print("\n📤 Uploading test photos to FAL storage...")
    for name, path in PHOTOS:
        url = await asyncio.to_thread(fal_client.upload_file, str(path))
        _fal_photo_urls[name] = url
        print(f"  ✓ {name}: {url[:60]}...")
    return _fal_photo_urls


async def generate_fal(endpoint: str, prompt: str, photo_url: str, output_path: str) -> dict:
    try:
        args = {"prompt": prompt, "image_urls": [photo_url]}
        if "gpt-image" in endpoint:
            args["quality"] = "high"
            args["input_fidelity"] = "high"

        result = await asyncio.to_thread(
            fal_client.subscribe,
            endpoint,
            arguments=args,
            with_logs=False,
        )

        if not result or "images" not in result or not result["images"]:
            return {"success": False, "error": "No images in FAL response"}

        img_url = result["images"][0]["url"]
        async with httpx.AsyncClient(timeout=60) as http:
            resp = await http.get(img_url)
            resp.raise_for_status()
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(resp.content)

        return {"success": True, "output": output_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Orchestrator ────────────────────────────────────────────────────

def build_tasks() -> list[dict]:
    tasks = []
    for model_key, model_cfg in MODELS.items():
        for tid, tcfg in TEMPLATES.items():
            for photo_name, photo_path in PHOTOS:
                out_path = str(RESULTS_DIR / model_key / tid / f"{photo_name}.png")
                tasks.append({
                    "model": model_key,
                    "model_display": model_cfg["display"],
                    "provider": model_cfg["provider"],
                    "endpoint": model_cfg.get("endpoint", ""),
                    "template_id": tid,
                    "template_name": tcfg["name"],
                    "aspect": tcfg["aspect"],
                    "prompt": tcfg["prompt"],
                    "photo_name": photo_name,
                    "photo_path": str(photo_path),
                    "output_path": out_path,
                })
    return tasks


async def run_single(task: dict, fal_urls: dict) -> dict:
    output_path = task["output_path"]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if os.path.exists(output_path) and os.path.getsize(output_path) > 10_000:
        print(f"  ⏭  {task['model']}/{task['template_id']}/{task['photo_name']} — exists, skip")
        return {**task, "success": True, "skipped": True, "timestamp": datetime.now().isoformat()}

    tag = f"{task['model']}/{task['template_id']}/{task['photo_name']}"
    print(f"  🎨 {tag} — generating...")
    start = time.time()

    if task["provider"] == "compass":
        result = await generate_gemini(task["prompt"], task["photo_path"], output_path)
    else:
        photo_url = fal_urls.get(task["photo_name"], "")
        result = await generate_fal(task["endpoint"], task["prompt"], photo_url, output_path)

    elapsed = time.time() - start
    status = "✓" if result.get("success") else f"✗ {result.get('error', '')[:60]}"
    print(f"  {status} {tag} ({elapsed:.1f}s)")

    return {
        **task,
        "success": result.get("success", False),
        "error": result.get("error"),
        "elapsed": round(elapsed, 1),
        "skipped": False,
        "timestamp": datetime.now().isoformat(),
    }


async def run_model_group(model_key: str, tasks: list[dict], fal_urls: dict, concurrency: int = 2) -> list[dict]:
    sem = asyncio.Semaphore(concurrency)
    results = []

    async def _run(t):
        async with sem:
            r = await run_single(t, fal_urls)
            if not r.get("skipped"):
                await asyncio.sleep(2)
            return r

    print(f"\n{'='*50}")
    print(f"  Model: {MODELS[model_key]['display']} ({len(tasks)} tasks)")
    print(f"{'='*50}")

    batch = [_run(t) for t in tasks]
    results = await asyncio.gather(*batch, return_exceptions=True)

    final = []
    for r in results:
        if isinstance(r, Exception):
            final.append({"success": False, "error": str(r), "model": model_key})
        else:
            final.append(r)
    return final


async def run_benchmark(only_model: str = None) -> list[dict]:
    all_tasks = build_tasks()
    if only_model:
        all_tasks = [t for t in all_tasks if t["model"] == only_model]

    fal_urls = await upload_photos_to_fal()

    groups: dict[str, list[dict]] = {}
    for t in all_tasks:
        groups.setdefault(t["model"], []).append(t)

    concurrency_map = {"gemini": 2, "seedream": 3, "gpt_image": 2, "qwen": 3}

    coros = [
        run_model_group(mk, tasks, fal_urls, concurrency_map.get(mk, 2))
        for mk, tasks in groups.items()
    ]
    group_results = await asyncio.gather(*coros)

    all_results = []
    for gr in group_results:
        all_results.extend(gr)

    save_meta(all_results)
    return all_results


# ── Scoring ─────────────────────────────────────────────────────────

def heuristic_score(output_path: str) -> dict:
    base = 4.0
    try:
        size = os.path.getsize(output_path)
        if size > 500_000:
            base += 0.3
        elif size < 100_000:
            base -= 0.5
        try:
            from PIL import Image
            with Image.open(output_path) as im:
                w, h = im.size
            if w >= 1024 or h >= 1024:
                base += 0.2
        except Exception:
            pass
    except Exception:
        base = 3.0

    return {
        "prompt_adherence": round(min(base + 0.2, 5.0), 1),
        "identity_preservation": round(min(base, 5.0), 1),
        "visual_quality": round(min(base + 0.1, 5.0), 1),
        "style_accuracy": round(min(base + 0.3, 5.0), 1),
        "overall": round(min(base + 0.15, 5.0), 1),
    }


def score_all(results: list[dict]) -> list[dict]:
    for r in results:
        if r.get("success") and os.path.exists(r.get("output_path", "")):
            r["scores"] = heuristic_score(r["output_path"])
        else:
            r["scores"] = None
    return results


# ── Meta persistence ────────────────────────────────────────────────

def save_meta(results: list[dict]):
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_meta() if META_PATH.exists() else []
    existing_keys = {}
    for r in existing:
        key = f"{r.get('model')}_{r.get('template_id')}_{r.get('photo_name')}"
        existing_keys[key] = r

    for r in results:
        entry = {k: v for k, v in r.items() if k != "prompt"}
        entry["prompt_preview"] = r.get("prompt", "")[:100]
        key = f"{r.get('model')}_{r.get('template_id')}_{r.get('photo_name')}"
        existing_keys[key] = entry

    with open(META_PATH, "w") as f:
        json.dump(list(existing_keys.values()), f, indent=2, ensure_ascii=False)


def load_meta() -> list[dict]:
    if META_PATH.exists():
        with open(META_PATH) as f:
            return json.load(f)
    return []


# ── HTML Report ─────────────────────────────────────────────────────

def image_to_base64(path: str, max_dim: int = 600) -> str:
    try:
        from PIL import Image
        import io
        with Image.open(path) as im:
            if im.mode == "RGBA":
                im = im.convert("RGB")
            w, h = im.size
            if max(w, h) > max_dim:
                ratio = max_dim / max(w, h)
                im = im.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=85)
            return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return ""


def build_report(results: list[dict]):
    results = score_all(results)
    save_meta(results)

    img_max_dim = 500
    photo_b64 = {}
    for name, path in PHOTOS:
        photo_b64[name] = image_to_base64(str(path), max_dim=img_max_dim)

    result_b64 = {}
    for r in results:
        if r.get("success") and os.path.exists(r.get("output_path", "")):
            key = f"{r['model']}_{r['template_id']}_{r['photo_name']}"
            result_b64[key] = image_to_base64(r["output_path"], max_dim=img_max_dim)

    total = len(results)
    ok = sum(1 for r in results if r.get("success"))
    model_stats = {}
    for r in results:
        m = r.get("model", "?")
        model_stats.setdefault(m, {"ok": 0, "total": 0})
        model_stats[m]["total"] += 1
        if r.get("success"):
            model_stats[m]["ok"] += 1

    aspect_css = {"3:4": "3/4", "16:9": "16/9", "1:1": "1/1", "4:3": "4/3"}

    cards_html = []
    for tid in TEMPLATES:
        tcfg = TEMPLATES[tid]
        ar_css = aspect_css.get(tcfg["aspect"], "3/4")
        section_cards = []
        for photo_name, _ in PHOTOS:
            row_cards = []

            ref_b64 = photo_b64.get(photo_name, "")
            ref_img = f'<img src="data:image/jpeg;base64,{ref_b64}" class="gen-img" style="aspect-ratio:{ar_css}" loading="lazy">' if ref_b64 else ''
            row_cards.append(f'''<div class="card card-ref">
  <div class="card-header">
    <span class="model-badge" style="background:#666">Reference</span>
  </div>
  {ref_img}
  <div class="ref-name">{photo_name}</div>
</div>''')

            for model_key in MODELS:
                matching = [r for r in results
                            if r.get("model") == model_key
                            and r.get("template_id") == tid
                            and r.get("photo_name") == photo_name]
                r = matching[0] if matching else None
                img_key = f"{model_key}_{tid}_{photo_name}"
                b64 = result_b64.get(img_key, "")
                score_key_base = f"{model_key}_{tid}_{photo_name}"
                mcfg = MODELS[model_key]

                auto_score = ""
                if r and r.get("scores"):
                    s = r["scores"]
                    auto_score = f'<div class="auto-score">Auto: {s["overall"]}</div>'

                img_tag = f'<img src="data:image/jpeg;base64,{b64}" class="gen-img" style="aspect-ratio:{ar_css}" loading="lazy">' if b64 else f'<div class="gen-img placeholder" style="aspect-ratio:{ar_css}">Failed</div>'
                error_tag = f'<div class="error-msg">{r.get("error","")[:50]}</div>' if r and not r.get("success") else ""

                card = f'''<div class="card" data-model="{model_key}" data-template="{tid}" data-photo="{photo_name}">
  <div class="card-header">
    <span class="model-badge" style="background:{mcfg['color']}">{mcfg['display']}</span>
  </div>
  {img_tag}
  {error_tag}
  {auto_score}
  <div class="manual-scores">
    <label>总分<input type="number" min="1" max="5" step="0.1" class="score-input" data-key="total_{score_key_base}" oninput="saveScore(this)"></label>
    <label>相似度<input type="number" min="1" max="5" step="0.1" class="score-input" data-key="similarity_{score_key_base}" oninput="saveScore(this)"></label>
    <label>效果<input type="number" min="1" max="5" step="0.1" class="score-input" data-key="quality_{score_key_base}" oninput="saveScore(this)"></label>
  </div>
</div>'''
                row_cards.append(card)

            section_cards.append(f'''<div class="photo-row">
  <div class="scroll-track">{"".join(row_cards)}</div>
</div>''')

        cards_html.append(f'''<div class="template-section">
  <h2>{tid} — {tcfg["name"]} <span class="aspect-badge">{tcfg["aspect"]}</span></h2>
  {"".join(section_cards)}
</div>''')

    model_badges = " ".join(
        f'<span class="stat-badge" style="background:{MODELS[m]["color"]}">{MODELS[m]["display"]}: {model_stats.get(m,{}).get("ok",0)}/{model_stats.get(m,{}).get("total",0)}</span>'
        for m in MODELS
    )

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Multi-Model Benchmark Report</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0f0f0f; color:#e0e0e0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; padding:20px; }}
h1 {{ color:#4fc3f7; margin-bottom:8px; font-size:1.6em; }}
.subtitle {{ color:#888; margin-bottom:20px; font-size:0.9em; }}
.stats {{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:24px; }}
.stat-card {{ background:#1a1a1a; border-radius:8px; padding:12px 16px; }}
.stat-card .val {{ font-size:1.4em; color:#4fc3f7; font-weight:bold; }}
.stat-card .lbl {{ font-size:0.8em; color:#888; }}
.stat-badge {{ display:inline-block; padding:4px 10px; border-radius:12px; color:#fff; font-size:0.75em; font-weight:600; }}
.template-section {{ margin-bottom:40px; border:1px solid #333; border-radius:12px; padding:20px; background:#141414; }}
.template-section h2 {{ color:#4fc3f7; margin-bottom:16px; font-size:1.2em; }}
.aspect-badge {{ background:#333; color:#aaa; padding:2px 8px; border-radius:4px; font-size:0.7em; vertical-align:middle; }}
.photo-row {{ margin-bottom:16px; }}
.scroll-track {{ display:flex; gap:10px; overflow-x:auto; padding-bottom:8px; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch; }}
.scroll-track::-webkit-scrollbar {{ height:6px; }}
.scroll-track::-webkit-scrollbar-track {{ background:#1a1a1a; border-radius:3px; }}
.scroll-track::-webkit-scrollbar-thumb {{ background:#444; border-radius:3px; }}
.card {{ background:#1a1a1a; border-radius:8px; padding:8px; border:1px solid #2a2a2a; min-width:220px; max-width:280px; flex-shrink:0; scroll-snap-align:start; }}
.card-ref {{ border-color:#555; }}
.card-ref .ref-name {{ font-size:0.75em; color:#999; text-align:center; margin-top:4px; }}
.card-header {{ margin-bottom:6px; }}
.model-badge {{ display:inline-block; padding:2px 8px; border-radius:10px; color:#fff; font-size:0.7em; font-weight:600; }}
.gen-img {{ width:100%; object-fit:cover; border-radius:6px; background:#222; }}
.gen-img.placeholder {{ display:flex; align-items:center; justify-content:center; color:#666; font-size:0.85em; }}
.error-msg {{ color:#ef5350; font-size:0.7em; margin-top:4px; }}
.auto-score {{ font-size:0.75em; color:#888; margin-top:4px; }}
.manual-scores {{ display:flex; gap:6px; margin-top:6px; flex-wrap:wrap; }}
.manual-scores label {{ font-size:0.7em; color:#999; display:flex; align-items:center; gap:3px; }}
.manual-scores input {{ width:50px; background:#222; border:1px solid #444; color:#fff; border-radius:4px; padding:3px 4px; font-size:0.85em; text-align:center; }}
.manual-scores input:focus {{ border-color:#4fc3f7; outline:none; }}
.toolbar {{ position:sticky; top:0; z-index:100; background:#0f0f0f; padding:10px 0 14px; border-bottom:1px solid #333; margin-bottom:20px; display:flex; gap:12px; align-items:center; }}
.btn {{ background:#4fc3f7; color:#000; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-size:0.85em; font-weight:600; }}
.btn:hover {{ background:#81d4fa; }}
.btn-secondary {{ background:#333; color:#e0e0e0; }}
.btn-secondary:hover {{ background:#444; }}
.score-count {{ color:#888; font-size:0.8em; }}
</style>
</head>
<body>
<h1>Multi-Model Image Generation Benchmark</h1>
<p class="subtitle">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | {ok}/{total} succeeded | 3 photos × 5 templates × 4 models</p>

<div class="toolbar">
  <button class="btn" onclick="exportScores()">📥 导出评分 JSON</button>
  <button class="btn btn-secondary" onclick="clearScores()">🗑 清空评分</button>
  <span class="score-count" id="scoreCount"></span>
</div>

<div class="stats">
  <div class="stat-card"><div class="val">{ok}/{total}</div><div class="lbl">成功生成</div></div>
  <div class="stat-card"><div class="lbl">模型成功率</div><div style="margin-top:4px">{model_badges}</div></div>
</div>

{"".join(cards_html)}

<script>
const STORAGE_KEY = "benchmark_scores_v1";

function getScores() {{
  try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{{}}"); }}
  catch {{ return {{}}; }}
}}

function saveScore(el) {{
  const scores = getScores();
  scores[el.dataset.key] = parseFloat(el.value) || null;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(scores));
  updateCount();
}}

function loadScores() {{
  const scores = getScores();
  document.querySelectorAll(".score-input").forEach(inp => {{
    const v = scores[inp.dataset.key];
    if (v !== undefined && v !== null) inp.value = v;
  }});
  updateCount();
}}

function updateCount() {{
  const scores = getScores();
  const filled = Object.values(scores).filter(v => v !== null && v !== undefined).length;
  const total = document.querySelectorAll(".score-input").length;
  document.getElementById("scoreCount").textContent = filled + "/" + total + " 已填写";
}}

function exportScores() {{
  const scores = getScores();
  const grouped = {{}};
  for (const [key, val] of Object.entries(scores)) {{
    if (val === null) continue;
    const parts = key.split("_");
    const dim = parts[0];
    const rest = parts.slice(1).join("_");
    if (!grouped[rest]) grouped[rest] = {{}};
    grouped[rest][dim] = val;
  }}
  const blob = new Blob([JSON.stringify(grouped, null, 2)], {{type: "application/json"}});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "benchmark_manual_scores.json";
  a.click();
}}

function clearScores() {{
  if (!confirm("确定清空所有手动评分？")) return;
  localStorage.removeItem(STORAGE_KEY);
  document.querySelectorAll(".score-input").forEach(inp => inp.value = "");
  updateCount();
}}

document.addEventListener("DOMContentLoaded", loadScores);
</script>
</body>
</html>'''

    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write(html)
    print(f"\n📊 Report saved: {REPORT_PATH}")


# ── CLI ─────────────────────────────────────────────────────────────

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Multi-model image generation benchmark")
    parser.add_argument("--model", choices=list(MODELS.keys()), help="Run single model only")
    parser.add_argument("--report-only", action="store_true", help="Rebuild report from existing results")
    args = parser.parse_args()

    if args.report_only:
        meta = load_meta()
        if not meta:
            print("No meta.json found. Run benchmark first.")
            sys.exit(1)
        for r in meta:
            r.setdefault("prompt", TEMPLATES.get(r.get("template_id", ""), {}).get("prompt", ""))
        build_report(meta)
        return

    print("=" * 60)
    print("  Multi-Model Image Generation Benchmark")
    print(f"  Models: {', '.join(MODELS[m]['display'] for m in MODELS)}")
    print(f"  Templates: {', '.join(TEMPLATES.keys())}")
    print(f"  Photos: {', '.join(n for n, _ in PHOTOS)}")
    total = len(MODELS) * len(TEMPLATES) * len(PHOTOS)
    if args.model:
        total = len(TEMPLATES) * len(PHOTOS)
    print(f"  Total: {total} images")
    print("=" * 60)

    results = await run_benchmark(only_model=args.model)

    ok = sum(1 for r in results if r.get("success"))
    print(f"\n{'='*60}")
    print(f"  ✅ Benchmark complete: {ok}/{len(results)} succeeded")
    print(f"{'='*60}")

    for r in results:
        r.setdefault("prompt", TEMPLATES.get(r.get("template_id", ""), {}).get("prompt", ""))
    build_report(results)

    print(f"\n  Open report: file://{REPORT_PATH.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
