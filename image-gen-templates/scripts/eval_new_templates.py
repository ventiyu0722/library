#!/usr/bin/env python3
"""Batch-generate test images for the 22 new templates (L24-L29, L36-L48, L63-L65)."""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from generate import generate_image

RESULTS_DIR = Path(__file__).parent.parent / "test" / "results"
SAMPLES_DIR = Path(__file__).parent.parent / "test" / "samples"
META_FILE = RESULTS_DIR / "evaluation-meta.json"

SELFIE = str(SAMPLES_DIR / "selfie.jpg")
PET = str(SAMPLES_DIR / "pet.jpg")

NEW_TEMPLATES = {
    "L24": {
        "name": "Game CG / Thick Paint",
        "prompt": (
            "Transform the uploaded photo into a premium AAA game cutscene illustration while preserving "
            "the subject's complete facial identity, hairstyle, and distinguishing features. "
            "This is concept-art quality digital painting for a high-budget RPG cinematic trailer. "
            "Technique: thick impasto digital brushwork — visible directional strokes on fabric and hair, "
            "loaded brushes and palette-knife edges in highlights, soft blended transitions in skin. "
            "Layered opaque color with rich saturation. Subtle specular hits on eyes, lips, and metallic accents. "
            "Lighting: dramatic rim light from behind — warm gold against cooler ambient fill. Deep readable shadows "
            "with color in the blacks (blue-violet or deep teal). "
            "Background: a painterly fantasy vista softly suggested — towering architecture and distant battle glow "
            "rendered with loose brushwork. Composition: three-quarter heroic bust. Aspect ratio 3:4. "
            "No text, no watermark. The overall style is a collector-worthy game CG portrait balancing "
            "thick-paint expressiveness with clear recognizable likeness."
        ),
        "ref": SELFIE,
    },
    "L25": {
        "name": "Vaporwave",
        "prompt": (
            "Transform the uploaded photo into a striking vaporwave aesthetic portrait. "
            "Preserve the subject's facial identity while fully embracing retro-digital surrealism. "
            "Scene: marble Roman bust fragments, Greek columns, and palm silhouettes drifting in soft haze. "
            "Color: dominant gradients of electric purple, teal, and hot pink with smooth diagonal blends. "
            "VHS artifacts: subtle horizontal scanlines, slight chromatic aberration, mild tracking jitter, "
            "and soft phosphor glow. Glitch accents: small RGB channel splits on outer contours, "
            "occasional scan-line breaks across non-facial areas, tiny datamoshing hints in background only. "
            "Lighting: flat-to-soft frontal fill with neon edge lights — cyan from one side, magenta from the other. "
            "Background: infinite perspective grid or sun-disk over hazy horizon with floating geometric shards. "
            "Composition: centered bust, square 1:1. No readable text, no watermark. "
            "The overall style is refined vaporwave artwork: nostalgic, slightly uncanny."
        ),
        "ref": SELFIE,
    },
    "L26": {
        "name": "Printmaking / Woodblock",
        "prompt": (
            "Transform the uploaded photo into a traditional relief printmaking portrait — as if pulled from a carved "
            "woodblock or linoleum plate. Preserve recognizable likeness through simplified planes and bold graphic shapes. "
            "Technique: carved-line aesthetic — tapering line weight, slight irregularities, occasional white specks "
            "where the block would not ink. Flat color shapes separated by crisp edges; no soft airbrush. "
            "Limited palette of 3 to 5 ink layers — deep black line work, mid flat for skin, one shadow tone, "
            "and one or two accent colors. Visible wood grain or plate pressure marks in large flat areas, "
            "slight ink density variation at edges. "
            "Background: bold decorative flat shapes — radiating lines, stylized botanicals in the same limited palette. "
            "Composition: portrait 3:4, figure prominent, generous margin suggesting paper edge. "
            "No text, no watermark. The overall style is gallery-quality woodcut / linocut interpretation: "
            "graphic, tactile, and unmistakably printmaking."
        ),
        "ref": SELFIE,
    },
    "L27": {
        "name": "Fine Brush / Gongbi",
        "prompt": (
            "Transform the uploaded photo into a refined gongbi-style Chinese painting — contemporary gongbi sensibility — "
            "while preserving the subject's facial identity and calm, dignified presence. "
            "Support: fine silk with subtle fiber texture and mineral glow of traditional pigments. "
            "Technique: extremely fine controlled brush lines for hair strands, eyelashes, and fabric weave; "
            "smooth even color fills in skin with delicate rose-tinged undertones and soft cool shadows. "
            "Layered transparent washes build depth without losing clarity. "
            "Palette: classical mineral colors — malachite green, azurite blue, cinnabar red accents, "
            "ivory and ochre skin tones, touches of delicate gold leaf on hair ornaments. "
            "Attire: elegant updated hanfu with fine pattern work, subtle botanical embroidery. "
            "Background: sparse branches, orchids, distant misty mountains. "
            "Lighting: soft even illumination, modeling through color temperature and fine edge lines. "
            "Composition: vertical portrait 3:4, optional small red seal mark in corner. "
            "No modern objects, no watermark. The overall style is museum-quality contemporary gongbi portrait."
        ),
        "ref": SELFIE,
    },
    "L28": {
        "name": "Pen Sketch / Simple Line",
        "prompt": (
            "Transform the uploaded photo into a quick, confident pen sketch on bright white paper. "
            "Preserve the subject's identity through line economy — gesture, proportion, and characteristic contours. "
            "Tool: fine-nib fountain pen — consistent single-weight line with occasional pressure swell on curves. "
            "Lines are fast but intentional: continuous contours where possible, minimal scratchy re-strokes. "
            "Detail level: sparing — suggest eyes with simple lids and a dot for pupils, indicate hair "
            "with flowing contour bundles, define clothing with a handful of crisp folds. "
            "Shading: almost none — at most light parallel hatching under the chin and nose for grounding. "
            "No full gray tones, no stipple fields. "
            "Negative space: generous white paper around the figure. "
            "Composition: head-and-shoulders, centered, square 1:1. No color, no text, no watermark. "
            "The overall style is an illustrator's on-location pen capture: lively, readable, and charmingly incomplete."
        ),
        "ref": SELFIE,
    },
    "L29": {
        "name": "Dark Fairy Tale",
        "prompt": (
            "Transform the uploaded photo into a dark fairy tale illustration in the spirit of Tim Burton — "
            "spiky silhouettes, elongated forms, and playful dread. "
            "Preserve the subject's recognizable features while stretching proportions slightly for storybook eeriness. "
            "Figure: subtle elongation; eyes large and luminous with deep shadows; hair wild, geometric, or wind-swept "
            "into sharp graphic shapes. Skin: pale, cool desaturation with strategic pops of crimson — lips, a ribbon, a rose. "
            "Environment: a twisted fairytale forest — crooked gate, spiral hill, stylized trees like clawed hands, "
            "curling fog, paper-thin crescent moon. "
            "Lighting: cool moonlight key with faint under-light for supernatural unease; long soft shadows. "
            "Texture: slightly matte storybook painted surface — visible brush strokes, subtle film grain. "
            "Composition: vertical 3:4, dynamic silhouette readable at thumbnail size. "
            "No text, no watermark. The overall style is a dark fairy tale character portrait: eerie, elegant, emotionally narrative."
        ),
        "ref": SELFIE,
    },
    "L36": {
        "name": "Indoor Scene Portrait",
        "prompt": (
            "Transform the uploaded photo into a polished indoor lifestyle portrait. "
            "Preserve the subject's complete facial identity, skin texture, and expression. "
            "Setting: subject near a tall window, soft daylight raking across the face from the side, "
            "subtle shadow falloff on the far cheek. Cozy restaurant elements visible in soft background — "
            "warm tungsten practicals, wood paneling, patterned tile. "
            "Wardrobe: natural everyday clothing consistent with the interior. "
            "Camera: 50mm full-frame equivalent, f/1.8, natural perspective, shallow depth of field "
            "isolating the subject from pleasant environmental blur with recognizable interior shapes. "
            "Color grade: film-inspired — gentle contrast, warm shadows. "
            "Composition: 3:4 vertical, subject with breathing room, eye-line engaging. "
            "No text, no watermark. The overall style is a believable high-quality indoor portrait — "
            "intimate, contextual, and naturally lit."
        ),
        "ref": SELFIE,
    },
    "L37": {
        "name": "Dark Mood Portrait",
        "prompt": (
            "Transform the uploaded photo into a low-key, emotionally intense portrait. "
            "Preserve the subject's facial identity while pushing exposure toward deliberate shadow. "
            "Lighting: a single dominant hard source — a narrow window slash placing strong highlights on one side "
            "of the face while the rest falls into deep detailed shadow (not crushed black — retain subtle color in the darks). "
            "Mood: contemplative — eyes catch a small catch-light so the gaze remains alive. "
            "Skin: retain texture — pores and micro-contrast visible in lit areas; shadow side soft and mysterious. "
            "Color: desaturated overall with slight teal in shadows and warm neutral in highlights. "
            "Background: minimal and dark — bare wall, a few practical highlights optional, no clutter. "
            "Camera: 85mm portrait lens, wide aperture, subtle natural grain. "
            "Composition: tight to medium framing, 3:4 vertical. "
            "No text, no watermark. The overall style is an editorial dark-mood portrait: cinematic and emotionally weighted."
        ),
        "ref": SELFIE,
    },
    "L38": {
        "name": "Iconic Location Shot",
        "prompt": (
            "Transform the uploaded photo into a striking environmental portrait at an iconic location. "
            "Preserve the subject's identity, pose logic, and proportions. "
            "Setting: the subject stands before a vast vermillion red wall reminiscent of the Forbidden City — "
            "even, weathered lacquer texture, subtle horizontal seams, and a thin stone base at the bottom. "
            "Monumental scale emphasizing the figure. "
            "Lighting: soft overcast or open shade for even skin tones on the red wall. "
            "Wardrobe: timeless simple clothing that contrasts cleanly with the backdrop — ivory, black, or deep jade. "
            "Camera: medium telephoto to compress the subject against the massive wall, f/2.8-f/4 for slight "
            "environmental readability. "
            "Composition: vertical 3:4, subject off-center following rule of thirds, with generous red wall negative space. "
            "No text, no watermark. The overall style is a travel-editorial hero shot — iconic, dignified, "
            "and immediately readable as a cultural landmark portrait."
        ),
        "ref": SELFIE,
    },
    "L39": {
        "name": "Spring Floral Portrait",
        "prompt": (
            "Transform the uploaded photo into a soft spring floral portrait. "
            "Preserve the subject's complete facial identity while surrounding them with abundant cherry blossoms. "
            "Blossoms frame the face — foreground petals blurred large, mid-ground branches crisply detailed, "
            "background a gentle bokeh of flowers and sky. Some petals drifting through the air, frozen mid-fall. "
            "Light: soft pastel daylight — high-key but not blown — slight pink bounce from petals onto skin. "
            "Wardrobe: light spring clothing — linen or chiffon in cream, blush, or soft blue — "
            "harmonizing with the floral palette. "
            "Color grade: airy, romantic, slightly desaturated greens with luminous highlights. "
            "Camera: 85mm f/1.4, creamy bokeh, gentle lens glow. "
            "Composition: vertical 3:4, subject centered, face sharp. "
            "No text, no watermark. The overall style is a seasonal editorial portrait — fresh, romantic, "
            "and unmistakably spring."
        ),
        "ref": SELFIE,
    },
    "L40": {
        "name": "Natural Light & Shadow",
        "prompt": (
            "Transform the uploaded photo into a sun-drenched outdoor portrait celebrating natural light patterns. "
            "Preserve the subject's identity while emphasizing interplay between light and shadow. "
            "Key effect: dappled tree shadow patterns — broken leaf-shaped highlights and soft organic shadows "
            "projected across the face, neck, and shoulders, moving with the contours of the features. "
            "Hair: strong rim and backlight so individual strands glow — golden halo, subtle flyaways catching specular highlights. "
            "Environment: park or garden path — green foliage soft in background, sun filtering through canopy. "
            "Time: late morning or golden hour — warm sun, high dynamic range handled naturally. "
            "Skin: retain texture; dappled patches should feel photographic, not painted-on. "
            "Camera: 85mm, wide aperture, slight flare acceptable. "
            "Composition: 3:4 vertical, intimate framing, eyes sharp. "
            "No text, no watermark. The overall style is a fine-art natural-light portrait — organic, fresh, and technically sophisticated."
        ),
        "ref": SELFIE,
    },
    "L41": {
        "name": "Sunset / Golden Hour",
        "prompt": (
            "Transform the uploaded photo into a wide cinematic sunset portrait. "
            "Preserve the subject's identity — strong rim-lit profile with balanced exposure against glowing sky. "
            "Sky: layered sunset — deep amber near horizon, rose and coral mid-band, cooling violet higher up — "
            "optional thin cloud streaks catching fire. "
            "Subject: strong warm edge light outlining hair and shoulders, face partially in soft fill from sky bounce — "
            "still identifiable. Gentle sun bloom and optional anamorphic flare streak. "
            "Environment: open horizon — sea, lake, or field — horizon low in frame for maximum sky drama. "
            "Camera: wide to normal focal length for landscape orientation, deep depth of field. "
            "Composition: 16:9 horizontal, epic negative space, emotional scale. "
            "No text, no watermark. The overall style is a cinematic golden-hour environmental portrait — "
            "warm, vast, and emotionally open."
        ),
        "ref": SELFIE,
    },
    "L42": {
        "name": "Retro Film & Polaroid",
        "prompt": (
            "Transform the uploaded photo into an instant-film snapshot aesthetic. "
            "Preserve the subject's identity and casual energy while emulating analog capture. "
            "Format: classic Polaroid — thick white bottom border and thinner side/top borders — image area square. "
            "Color science: faded warm shift — lifted blacks, slightly crushed shadows, cyan-leaning shadows optional, "
            "gentle highlight bloom. Skin creamy with nostalgic warmth. "
            "Texture: fine film grain, micro-dust specks, subtle roller marks at edges — authentic, not dirty. "
            "Scenario: casual car interior selfie at dusk with street bokeh through window. "
            "Flash: direct on-camera flash with sharp falloff, slight hotspot on forehead. "
            "Composition: square 1:1 including the Polaroid frame as part of the image. "
            "No modern UI, no watermark. The overall style is a believable vintage instant print — "
            "intimate, imperfect, and emotionally nostalgic."
        ),
        "ref": SELFIE,
    },
    "L43": {
        "name": "Winter Snow Portrait",
        "prompt": (
            "Transform the uploaded photo into a cinematic winter portrait in falling snow. "
            "Preserve the subject's identity while conveying cold air and quiet atmosphere. "
            "Weather: soft large flakes near camera blurred as bokeh orbs, finer flakes sharp mid-air, "
            "occasional flakes catching on lashes and hair. "
            "Breath: subtle visible vapor on exhale — delicate, not exaggerated. "
            "Palette: cool blue-white ambient with silver shadows; warm accent from scarf and coat lining. "
            "Wardrobe: chunky knit scarf, wool coat — realistic winter fabrics with frost on shoulders optional. "
            "Environment: snowy path with pine forest edge — background soft, readable. "
            "Light: overcast soft box from sky with low warm sun on snow bounce filling face. "
            "Camera: 85mm f/2, slight shutter speed sense of falling snow motion. "
            "Composition: vertical 3:4, subject clear against snowy depth. "
            "No text, no watermark. The overall style is a premium winter editorial — crisp, serene, and tactilely cold."
        ),
        "ref": SELFIE,
    },
    "L44": {
        "name": "Beach & Underwater",
        "prompt": (
            "Transform the uploaded photo into a sun-drenched beach portrait. "
            "Preserve the subject's identity while committing fully to the coastal environment. "
            "Setting: bright golden hour shore — sparkling wet sand, gentle surf foam, sea sparkle bokeh, "
            "wind in hair, sun cream natural highlights on skin, polarized sky gradient. "
            "Wardrobe: light summer dress or casual beach clothing — fabric behavior matches wind and moisture. "
            "Light: warm golden hour backlight with sun flare, subject lit by warm ambient bounce. "
            "Camera: 35mm or 50mm with sun flare control, shallow depth of field on crashing waves. "
            "Composition: 3:4 vertical, dynamic but readable. "
            "No text, no watermark. The overall style is a high-end travel or swim editorial — "
            "luminous, aquatic, and escapist."
        ),
        "ref": SELFIE,
    },
    "L45": {
        "name": "Fantasy / Magical Scene",
        "prompt": (
            "Transform the uploaded photo into a magical fantasy scene portrait. "
            "Preserve the subject's facial identity while embedding them in a cinematic wizarding world. "
            "Setting: a grand magic academy great hall — floating candles in mid-air, warm flicker on stone arches, "
            "distant stained glass, dust motes glowing in light beams, subtle blue magical ambient in shadowed vaults. "
            "Magic effects: soft spell shimmer around hands, faint rune particles, gentle wand-spark trail. "
            "Eyes: subtle starfield or constellation reflection in pupils — mystical but still human. "
            "Wardrobe: structured robes with house-scarf accents — tailored, not cosplay cheap. "
            "Atmosphere: wonder, warmth, slight mystery — chiaroscuro from candle key with cool fill from magical sources. "
            "Camera: cinematic portrait lens, shallow depth, background architecture readable. "
            "Composition: vertical 3:4, subject heroic. No copyrighted names, no text overlay. "
            "The overall style is a premium fantasy cinematic still — Harry-Potter-adjacent mood."
        ),
        "ref": SELFIE,
    },
    "L46": {
        "name": "Social Media / Street Style",
        "prompt": (
            "Transform the uploaded photo into a high-engagement social-media-ready portrait. "
            "Preserve the subject's identity while optimizing for contemporary social-media-ready aesthetics. "
            "Mood: effortless confidence — natural street fashion, subtle attitude, clean skin with realistic texture. "
            "Setting: urban street corner with soft background compression, city bokeh. "
            "Styling: layered OOTD — jacket, tee, accessories with clear silhouette; hair and makeup current but believable. "
            "Composition: vertical 3:4 with intentional negative space in upper area for future text or stickers. "
            "Color grade: slightly lifted shadows, gentle teal-orange — platform-ready pop without clipping. "
            "Camera: 50mm-85mm feel, wide aperture, crisp eye AF. "
            "No actual text or watermark in image. "
            "The overall style is a polished plog / street-style aesthetic — shareable, trendy, and identity-true."
        ),
        "ref": SELFIE,
    },
    "L48": {
        "name": "Photo Grid Layout",
        "prompt": (
            "Transform the uploaded photo into a single square image containing a 3x1 horizontal triptych — "
            "three equal-width panels side by side, unified cherry blossom theme, same subject throughout. "
            "Layout: three panels with thin white gutters between — consistent width, clean alignment. "
            "Subject consistency: the same person in all three panels — hairstyle and outfit coherent. "
            "Panel 1: wider environmental framing with blossoms. Panel 2: medium bust. Panel 3: tight detail on eyes or profile. "
            "Theme: cherry blossom session — petals in each panel, pink-white palette, soft daylight, romantic cohesive mood. "
            "Each panel: different pose and crop — left: subject looking over shoulder; center: straight-on soft smile; "
            "right: close profile with petals falling past cheek. "
            "Color grade: unified across panels — matched white balance and contrast. "
            "Output: one image, square 1:1. No text, no watermark. "
            "The overall style is a polished social triptych — cohesive, romantic, and ready for platform posting."
        ),
        "ref": SELFIE,
    },
    "L63": {
        "name": "Image Outpainting",
        "prompt": (
            "Perform seamless image outpainting on the uploaded photograph. "
            "Extend the canvas equally on left and right by approximately 25% additional width per side "
            "while preserving the original pixels in the central region unchanged. "
            "The expanded regions must feel as if they were photographed in the same moment — same lens perspective, "
            "same depth of field, same color science, same grain — not a collage. "
            "Continue existing scene geometry: architecture continues with matching vanishing lines; "
            "ground plane continues with consistent texture; sky matches gradient and haze. "
            "Lighting: extrapolate light direction and quality — shadows, highlights, and bounce light must agree. "
            "Style lock: match photographic medium of the source — no style drift at the seam. "
            "Seams: absolutely invisible — no hard lines, no resolution mismatch, no sudden sharpness change. "
            "Do not crop or rescale the original subject. Do not add text or watermark. "
            "The overall result is a believable wider frame that looks like it was always shot this way."
        ),
        "ref": SELFIE,
    },
    "L64": {
        "name": "Object Removal",
        "prompt": (
            "Remove the background distractions from the uploaded photograph with invisible inpainting. "
            "Target: any distracting background elements — tourists, signs, wires, trash — while keeping the main subject "
            "completely untouched. The edit should read as if the objects never existed. "
            "Reconstruction: fill cleared regions with structurally appropriate continuation — sidewalk continues, "
            "wall texture matches, foliage follows natural growth patterns, sky gradient uninterrupted. "
            "Lighting and color: match surrounding exposure, noise/grain profile, and depth of field. "
            "Edges: preserve the silhouette integrity of the main subject; do not alter face, hands, or clothing. "
            "Do not change composition crop, aspect ratio, or camera angle. No text, no watermark. "
            "The overall result is a clean photograph suitable for print — distraction removed, authenticity retained."
        ),
        "ref": SELFIE,
    },
    "L65": {
        "name": "Image Enhancement",
        "prompt": (
            "Enhance the uploaded photograph for clarity and perceived resolution without changing composition or framing. "
            "Goals: improve micro-contrast and edge definition, recover fine detail in hair, eyes, and fabric weave, "
            "and reduce noise — while avoiding halos, crunchy oversharpening, or waxy skin. "
            "Lighting: gently optimize exposure — lift shadow detail slightly, roll off harsh highlights. "
            "Color: maintain white balance fidelity; optional subtle vibrance without shifting skin hue. "
            "Skin: preserve pores and natural texture — denoise luminance noise more than color noise; "
            "no beauty-filter blur. "
            "Sharpening: deconvolution-style detail recovery on eyes and lashes, moderate global clarity, "
            "no white outlines on edges. "
            "Do not alter facial identity, body shape, or scene content. Do not crop. Do not add text or watermark. "
            "The overall result should read as the same photo taken with a better lens and sensor."
        ),
        "ref": SELFIE,
    },
}


async def run_all():
    meta_path = META_FILE
    existing_meta = {}
    if meta_path.exists():
        with open(meta_path) as f:
            existing_meta = json.load(f)

    for tid, tpl in NEW_TEMPLATES.items():
        out_dir = RESULTS_DIR / tid
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / "run_1.png")

        if os.path.exists(out_path):
            print(f"[{tid}] Already exists, skipping")
            continue

        print(f"\n{'='*60}")
        print(f"[{tid}] {tpl['name']}")
        print(f"Prompt: {tpl['prompt'][:120]}...")
        if tpl.get("ref"):
            print(f"Reference: {tpl['ref']}")

        result = await generate_image(
            prompt=tpl["prompt"],
            output_path=out_path,
            reference_image=tpl.get("ref"),
        )

        meta_entry = {
            "template_id": tid,
            "template_name": tpl["name"],
            "prompt": tpl["prompt"],
            "reference_image": tpl.get("ref"),
            "output": out_path if result["success"] else None,
            "success": result["success"],
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat(),
        }

        existing_meta[tid] = meta_entry
        with open(meta_path, "w") as f:
            json.dump(existing_meta, f, indent=2, ensure_ascii=False)

        status = "OK" if result["success"] else f"FAILED: {result.get('error')}"
        print(f"Result: {status}")

        if result["success"]:
            await asyncio.sleep(2)

    print(f"\n{'='*60}")
    print(f"Done! Results in: {RESULTS_DIR}")
    successes = sum(1 for t in NEW_TEMPLATES if (RESULTS_DIR / t / "run_1.png").exists())
    print(f"Success: {successes}/{len(NEW_TEMPLATES)}")


if __name__ == "__main__":
    asyncio.run(run_all())
