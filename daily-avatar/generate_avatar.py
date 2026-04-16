#!/usr/bin/env python3
"""Avatar image generation via Gemini 3.1 Flash Image through Compass LLM Proxy.

Usage:
    python3 generate_avatar.py "<prompt>" <reference_image_path> [--output-dir <dir>] [--user-id <uid>]

Outputs structured JSON to stdout. Generated image is saved to disk.
"""

import argparse
import io
import json
import math
import os
import sys
import time
import uuid
from datetime import datetime

from PIL import Image, ImageOps
from google import genai
from google.genai import types

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATHS = [
    os.path.join(SCRIPT_DIR, "config.json"),
    os.path.expanduser("~/.claude/skills/daily-avatar/config.json"),
    os.path.expanduser("~/.claude/skills/image-gen/config.json"),
]

DEFAULT_BASE_URL = "http://beeai.test.shopee.io/inbeeai/compass-api/v1"
DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
AVATAR_SIZE = 1024
HISTORY_FILE = os.path.join(SCRIPT_DIR, "history.json")


def _load_config() -> dict:
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                continue
    return {}


def _resolve_token(cfg: dict) -> str:
    token = os.environ.get("COMPASS_CLIENT_TOKEN", "")
    if token:
        return token
    return cfg.get("compass_api", {}).get("client_token", "")


def _fix_orientation(img: Image.Image) -> Image.Image:
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass
    return img


def _center_crop_square(img: Image.Image) -> Image.Image:
    """Crop to 1:1 from center."""
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def _prepare_reference(path: str, target_size: int = AVATAR_SIZE) -> tuple[bytes, str]:
    """Load reference image: fix orientation, center-crop to square, resize, return JPEG bytes."""
    img = Image.open(path)
    img = _fix_orientation(img)
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    img = _center_crop_square(img)
    if img.size[0] != target_size:
        img = img.resize((target_size, target_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue(), "image/jpeg"


def _append_history(entry: dict, max_entries: int = 30):
    """Append generation record to local history file."""
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        history.append(entry)
        if len(history) > max_entries:
            history = history[-max_entries:]
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _output_json(data: dict):
    """Print structured JSON to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def generate_avatar(
    prompt: str,
    reference_path: str,
    output_dir: str = ".",
    user_id: str = "local",
) -> dict:
    """Generate avatar image. Returns structured result dict."""
    cfg = _load_config()
    token = _resolve_token(cfg)
    if not token:
        return {
            "success": False,
            "error": "Compass API client_token not found. Set COMPASS_CLIENT_TOKEN env var or configure config.json.",
            "error_code": "TOKEN_MISSING",
        }

    base_url = cfg.get("compass_api", {}).get("base_url", DEFAULT_BASE_URL)
    model = cfg.get("compass_api", {}).get("image_model", DEFAULT_MODEL)

    client = genai.Client(
        api_key=token,
        http_options=types.HttpOptions(base_url=base_url),
    )

    parts: list[types.Part] = []

    if not os.path.exists(reference_path):
        return {
            "success": False,
            "error": f"Reference image not found: {reference_path}",
            "error_code": "REF_NOT_FOUND",
        }

    try:
        img_data, mime_type = _prepare_reference(reference_path)
        parts.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load reference image: {e}",
            "error_code": "REF_LOAD_FAILED",
        }

    parts.append(types.Part.from_text(text=prompt))

    print(f"Calling {model} via Compass LLM Proxy...", file=sys.stderr)

    try:
        response = client.models.generate_content(
            model=model,
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
    except Exception as e:
        return {
            "success": False,
            "error": f"API call failed: {e}",
            "error_code": "API_FAILED",
        }

    if not response.candidates:
        return {
            "success": False,
            "error": "No candidates returned from API",
            "error_code": "NO_CANDIDATES",
        }

    text_content = ""
    saved_images = []

    os.makedirs(output_dir, exist_ok=True)

    for part in response.candidates[0].content.parts:
        if part.text:
            text_content += part.text
        if part.inline_data and part.inline_data.data:
            mime = part.inline_data.mime_type or "image/png"
            ext_map = {"image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}
            ext = ext_map.get(mime, ".jpg")
            filename = f"avatar_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(part.inline_data.data)
            size_kb = len(part.inline_data.data) / 1024
            saved_images.append({
                "path": os.path.abspath(filepath),
                "size_kb": round(size_kb, 1),
                "mime_type": mime,
            })

    if not saved_images:
        return {
            "success": False,
            "error": "No image generated by the model",
            "error_code": "NO_IMAGE",
            "model_notes": text_content,
        }

    gen_id = uuid.uuid4().hex[:12]
    now_iso = datetime.now().astimezone().isoformat()

    result = {
        "success": True,
        "id": gen_id,
        "user_id": user_id,
        "image_path": saved_images[0]["path"],
        "image_size_kb": saved_images[0]["size_kb"],
        "all_images": saved_images,
        "model_notes": text_content,
        "prompt_used": prompt,
        "reference_image": os.path.abspath(reference_path),
        "model": model,
        "generated_at": now_iso,
    }

    history_cfg = cfg.get("history", {})
    if history_cfg.get("enabled", True):
        _append_history({
            "id": gen_id,
            "user_id": user_id,
            "image_path": saved_images[0]["path"],
            "reference_image": os.path.abspath(reference_path),
            "prompt": prompt,
            "model_notes": text_content,
            "generated_at": now_iso,
        }, max_entries=history_cfg.get("max_entries", 30))

    return result


def main():
    parser = argparse.ArgumentParser(description="Daily Avatar Image Generator")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("reference", help="Path to reference avatar image")
    parser.add_argument("--output-dir", default=".", help="Directory to save generated images")
    parser.add_argument("--user-id", default="local", help="User ID for history tracking")
    args = parser.parse_args()

    result = generate_avatar(
        prompt=args.prompt,
        reference_path=args.reference,
        output_dir=args.output_dir,
        user_id=args.user_id,
    )

    _output_json(result)

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
