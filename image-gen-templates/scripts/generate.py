#!/usr/bin/env python3
"""Image generation client for Gemini 3.1 Flash Image via Compass LLM Proxy.

Reused and adapted from image-gen-skill project. Provides:
- Config loading (config.json / env vars)
- Gemini API client management
- Single image generation with optional reference image
- Batch generation for template evaluation
"""

import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai import types

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_PATHS = [
    PROJECT_DIR / "config.json",
    Path.home() / ".cursor" / "skills" / "image-gen-templates" / "config.json",
    Path.home() / ".cursor" / "skills" / "image-gen" / "config.json",
    Path.home() / ".claude" / "skills" / "image-gen-templates" / "config.json",
    Path.home() / ".claude" / "skills" / "image-gen" / "config.json",
]

DEFAULT_BASE_URL = "http://beeai.test.shopee.io/inbeeai/compass-api/v1"
DEFAULT_IMAGE_MODEL = "gemini-3.1-flash-image-preview"


def load_config() -> dict:
    cfg: dict = {}
    for path in CONFIG_PATHS:
        if path.exists():
            try:
                with open(path) as f:
                    file_cfg = json.load(f)
                if "compass_api" in file_cfg:
                    cfg = file_cfg["compass_api"]
                    break
            except Exception:
                continue

    for env_key in ("COMPASS_CLIENT_TOKEN", "COMPASS_API_KEY"):
        val = os.environ.get(env_key)
        if val:
            cfg["client_token"] = val
            break
    if os.environ.get("COMPASS_BASE_URL"):
        cfg["base_url"] = os.environ["COMPASS_BASE_URL"]

    cfg.setdefault("base_url", DEFAULT_BASE_URL)
    cfg.setdefault("image_model", DEFAULT_IMAGE_MODEL)
    return cfg


_GENAI_CLIENT: genai.Client | None = None


def get_client() -> genai.Client:
    global _GENAI_CLIENT
    if _GENAI_CLIENT is None:
        cfg = load_config()
        if not cfg.get("client_token"):
            print(
                "ERROR: Compass API key not found.\n"
                "Options (any one will work):\n"
                "  1. export COMPASS_API_KEY='your_key'\n"
                "  2. export COMPASS_CLIENT_TOKEN='your_key'\n"
                "  3. python3 generate.py 'prompt' --api-key YOUR_KEY\n"
                "  4. Edit config.json and set compass_api.client_token"
            )
            sys.exit(1)
        _GENAI_CLIENT = genai.Client(
            api_key=cfg["client_token"],
            http_options=types.HttpOptions(base_url=cfg["base_url"]),
        )
    return _GENAI_CLIENT


def get_model_name() -> str:
    return load_config().get("image_model", DEFAULT_IMAGE_MODEL)


async def generate_image(
    prompt: str,
    output_path: str,
    reference_image: str = None,
) -> dict:
    """Call Gemini 3.1 Flash Image. Returns result dict with success/error/output."""
    client = get_client()
    model = get_model_name()

    parts: list[types.Part] = []

    if reference_image and os.path.exists(reference_image):
        with open(reference_image, "rb") as f:
            img_data = f.read()
        ext = os.path.splitext(reference_image)[1].lower()
        mime_map = {
            ".png": "image/png", ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", ".webp": "image/webp",
        }
        mime_type = mime_map.get(ext, "image/jpeg")
        parts.append(types.Part.from_bytes(data=img_data, mime_type=mime_type))

    parts.append(types.Part.from_text(text=prompt))

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        if not response.candidates:
            return {"success": False, "error": "No candidates in response"}

        image_data = None
        text_response = None
        for part in response.candidates[0].content.parts:
            if part.text:
                text_response = part.text
            if part.inline_data and part.inline_data.data:
                image_data = part.inline_data.data

        if not image_data:
            return {"success": False, "error": "No image data in response", "text": text_response}

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_data)

        return {"success": True, "output": output_path, "text": text_response}

    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_for_template(
    template_id: str,
    prompt: str,
    output_dir: str,
    reference_image: str = None,
    run_index: int = 1,
) -> dict:
    """Generate an image for a specific template and save metadata."""
    output_path = os.path.join(output_dir, template_id, f"run_{run_index}.png")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"[{template_id}] Run {run_index}")
    print(f"Prompt: {prompt[:100]}...")
    if reference_image:
        print(f"Reference: {reference_image}")

    result = await generate_image(
        prompt=prompt,
        output_path=output_path,
        reference_image=reference_image,
    )

    meta = {
        "template_id": template_id,
        "run_index": run_index,
        "prompt": prompt,
        "reference_image": reference_image,
        "output": output_path if result["success"] else None,
        "success": result["success"],
        "error": result.get("error"),
        "text_response": result.get("text"),
        "timestamp": datetime.now().isoformat(),
    }

    status = "OK" if result["success"] else f"FAILED: {result.get('error')}"
    print(f"Result: {status}")

    return meta


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate image via Gemini 3.1 Flash Image (Compass API)",
        epilog="Auth: set COMPASS_API_KEY env var, use --api-key, or configure config.json",
    )
    parser.add_argument("prompt", help="The image generation prompt")
    parser.add_argument("--image", help="Reference image path (for photo-based templates)")
    parser.add_argument("--output", default=f"generated_{int(time.time())}_{uuid.uuid4().hex[:6]}.png",
                        help="Output file path (default: generated_<ts>_<id>.png)")
    parser.add_argument("--api-key", help="Compass API key (overrides env var and config.json)")
    args = parser.parse_args()

    if args.api_key:
        os.environ["COMPASS_API_KEY"] = args.api_key

    result = asyncio.run(generate_image(args.prompt, args.output, args.image))
    if result["success"]:
        print(f"Image saved: {os.path.abspath(result['output'])}")
    else:
        print(f"Failed: {result.get('error')}")
        sys.exit(1)
