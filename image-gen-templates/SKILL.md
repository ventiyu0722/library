---
name: image-gen-templates
description: >-
  High-heat template-based image generation skill with 74 curated templates covering
  stylization, photo scenes, portraits, pets, editing tools, social media, and professional
  design across 3 categories (Life & Entertainment / Media & Work / Professional Design).
  Matches user intent to specific templates for one-click, high-quality generation
  using Gemini 3.1 Flash Image (Nano Banana 2). Install to discover all templates
  or describe what you want and get matched instantly.
---

# Image Generation — High-Heat Template Skill

74 curated high-quality templates for one-click image generation via Gemini 3.1 Flash Image.

## When to Use

- User asks to generate, create, edit, design, transform, or stylize any image
- User wants to explore creative image generation possibilities
- User uploads a photo (or multiple photos) and wants to transform / stylize them
- Skill was just installed and user has no specific request yet

**When NOT to use (prefer `image_blog` instead):**
- User uploads multiple photos and wants a **multi-panel comic strip with narrative** (storyboard, emotional arc, panel layout) — use `image_blog` (life-comic) instead
- User wants a **photo blog / travel log / life summary** from photos — use `image_blog` (photo-blog) instead

## Image Generation — Dual Mode

This skill supports TWO image generation modes. Always try Mode A first; if unavailable,
automatically fall back to Mode B.

### Mode A: MCP Tool (preferred if available)

Call `imagen_generate` MCP tool with the final prompt. For templates requiring a reference
image, pass the user's image via `image_url`.

### Mode B: Direct Script Call (works in ANY sandbox)

When `imagen_generate` MCP tool is NOT available, use the bundled Python script to call
Gemini 3.1 Flash Image directly via Compass API. The script lives at
`scripts/generate.py` relative to this skill directory.

**Setup** (one-time, run in shell):
```bash
# Option 1: Set env var (recommended for sandboxes)
export COMPASS_API_KEY='your_compass_api_key_here'

# Option 2: Edit config.json in the skill directory with your key
# (already pre-configured if the user provided their key)
```

**Usage — Shell command**:
```bash
# Text-only generation
python3 <SKILL_DIR>/scripts/generate.py "your prompt here" --output result.png

# With reference image (for photo-based templates)
python3 <SKILL_DIR>/scripts/generate.py "your prompt here" --image photo.jpg --output result.png
```

**Usage — Inline Python** (when you need more control):
```python
import asyncio, sys, os
sys.path.insert(0, os.path.join('<SKILL_DIR>', 'scripts'))
from generate import generate_image

result = asyncio.run(generate_image(
    prompt="your prompt here",
    output_path="result.png",
    reference_image="photo.jpg",  # optional
))
# result = {"success": True, "output": "result.png"} or {"success": False, "error": "..."}
```

Replace `<SKILL_DIR>` with the actual path to this skill directory.

### Mode Detection

At the start of every generation request:
1. Check if `imagen_generate` MCP tool is available → use Mode A
2. Otherwise → use Mode B (script). Verify `COMPASS_API_KEY` env var or `config.json`
   has a valid `client_token`. If neither exists, ask the user for their Compass API key.

## Multiple Image Handling

When the user uploads **multiple photos** and wants the **same style** applied to each:

**IMPORTANT**: Process each image **individually** in separate API calls. Do NOT pass
multiple `image_urls` in a single `imagen_generate` call — this causes URL fetch timeouts.

### Mode A (MCP): Sequential calls
```
For each uploaded image:
  → call imagen_generate(prompt=<style_prompt>, image_url=<single_image_url>)
  → collect result
Present all results together.
```

### Mode B (Script): Batch command
```bash
# Pass a directory or comma-separated files
python3 <SKILL_DIR>/scripts/generate.py "style prompt" \
    --images /path/to/photos/ --output ./styled_output/

# Or specific files
python3 <SKILL_DIR>/scripts/generate.py "style prompt" \
    --images "photo1.jpg,photo2.jpg,photo3.jpg" --output ./styled_output/
```

### Inline Python (batch)
```python
import asyncio, sys, os
sys.path.insert(0, os.path.join('<SKILL_DIR>', 'scripts'))
from generate import generate_batch

results = asyncio.run(generate_batch(
    prompt="style prompt here",
    images=["photo1.jpg", "photo2.jpg", "photo3.jpg"],
    output_dir="./styled_output/",
    concurrency=2,
))
# results = [{"index": 1, "source": "...", "output": "...", "success": True}, ...]
```

## Master Workflow

```
START
│
├─ User has NO specific request (just installed / browsing)
│  └─ → PROACTIVE SHOWCASE (Section 2)
│
├─ User has a request (text / text+image)
│  ├─ → INTENT MATCHING (Section 3)
│  │   ├─ Template matched → TEMPLATE GENERATION (Section 4)
│  │   └─ No match → FALLBACK direct generation (Section 5)
│  │
│  └─ → QUALITY CHECK (Section 6)
│       ├─ Pass → Show result + suggest related templates
│       └─ Fail → RETRY (max 2) with surgical edit
│
END
```

---

## Section 1: Template Registry

74 templates organized in 3 categories. Read `TEMPLATES.md` in the same skill directory
for the full prompt patterns.

### L: Life & Entertainment (58 templates)

#### Stylization (29 templates)

| ID | Template | Keywords (EN) | Input |
|----|----------|---------------|-------|
| L01 | Chibi Cartoon | chibi, Q-version, cute cartoon, mini me | Photo |
| L02 | 3D Pixar Animation | 3D, Pixar, Disney, animated | Photo |
| L03 | Comic / Manga | comic, manga, graphic novel | Photo |
| L04 | Sketch / Pencil | sketch, pencil, drawing, graphite | Photo |
| L05 | Clay / Claymation | clay, claymation, plasticine, stop-motion | Photo |
| L06 | 80s Retro Animation | 80s, retro, synthwave, vintage cartoon | Photo |
| L07 | Retro-Futurism | retro-future, space age, vintage sci-fi | Photo |
| L08 | Ukiyo-e / Chinese Painting | ukiyo-e, Chinese painting, ink wash | Photo |
| L09 | Watercolor Portrait | watercolor, aquarelle, painting | Photo |
| L10 | K-Pop Star | K-Pop, Korean idol, idol photo | Photo |
| L11 | Imperial / Royal | imperial, royal, king, queen, emperor | Photo |
| L12 | 90s Yearbook | 90s, yearbook, high school, retro photo | Photo |
| L13 | High Fashion | high fashion, vogue, editorial, couture | Photo |
| L14 | Cyberpunk Portrait | cyberpunk, neon, cyber, futuristic | Photo |
| L15 | Oil Painting / Classical | oil painting, classical, renaissance | Photo |
| L16 | Pixel Art | pixel art, 8-bit, retro game, 16-bit | Photo |
| L17 | Flat / Vector Illustration | flat, vector, minimalist illustration | Photo |
| L18 | Anime | anime, Japanese animation, cartoon | Photo |
| L19 | Wool Felt / Needle Felt | wool felt, needle felt, felted | Photo |
| L20 | Colored Pencil | colored pencil, Prismacolor, crayon | Photo |
| L21 | Pop Art | pop art, Warhol, Lichtenstein | Photo |
| L22 | Miniature / Diorama | miniature, diorama, tilt-shift | Photo |
| L23 | Children's Drawing | children drawing, kid art, crayon | Photo |
| L24 | Game CG / Thick Paint | game CG, digital painting, thick paint | Photo |
| L25 | Vaporwave | vaporwave, aesthetic, retrowave, glitch | Photo |
| L26 | Printmaking / Woodblock | printmaking, woodblock, linocut | Photo |
| L27 | Fine Brush / Gongbi | gongbi, fine brush, meticulous | Photo |
| L28 | Pen Sketch / Simple Line | pen sketch, line drawing, ink pen | Photo |
| L29 | Dark Fairy Tale | dark fairy tale, gothic, Tim Burton | Photo |

#### Portrait & Photo Scenes (18 templates)

| ID | Template | Keywords (EN) | Input |
|----|----------|---------------|-------|
| L30 | Studio Photoshoot | photoshoot, studio, professional portrait | Photo |
| L31 | ID Photo | ID photo, passport, headshot | Photo |
| L32 | Emoji / Sticker Pack | emoji, sticker, emoticon | Photo |
| L33 | Avatar / Profile Picture | avatar, profile, pfp, icon | Photo |
| L34 | Film / Cinematic Portrait | film photography, cinematic, movie still | Photo |
| L35 | Dreamy / Hazy Portrait | dreamy, hazy, soft focus, ethereal | Photo |
| L36 | Indoor Scene Portrait | indoor, side angle, restaurant vintage | Photo |
| L37 | Dark Mood Portrait | dark mood, low-key, moody | Photo |
| L38 | Iconic Location Shot | red wall, landmark, Forbidden City | Photo |
| L39 | Spring Floral Portrait | spring, cherry blossom, pear blossom | Photo |
| L40 | Natural Light & Shadow | dappled light, tree shadow, sunlight | Photo |
| L41 | Sunset / Golden Hour | sunset, golden hour, silhouette | Photo |
| L42 | Retro Film & Polaroid | polaroid, film, vintage camera | Photo |
| L43 | Winter Snow Portrait | winter, snow, frosty, cold | Photo |
| L44 | Beach & Underwater | beach, underwater, ocean, diving | Photo |
| L45 | Fantasy / Magical Scene | magic, wizard, fantasy, spell | Photo |
| L46 | Social Media / Street Style | OOTD, Plog, street style | Photo |
| L48 | Photo Grid Layout | grid, triptych, photo grid | Photo |

#### Pets & Babies (5 templates)

| ID | Template | Keywords (EN) | Input |
|----|----------|---------------|-------|
| L50 | Pet Stylization | cute pet, pet portrait, kawaii pet | Pet photo |
| L51 | Baby Comic Grid | baby comic, baby expressions, grid | Baby photo |
| L52 | Pet VOGUE Magazine | pet magazine, pet cover, VOGUE | Pet photo |
| L53 | Pet Costume Play | pet costume, pet mugshot, pet dress-up | Pet photo |
| L54 | Pet Humanization | pet humanization, anthropomorphic | Pet photo |

#### Try-on, Editing & Enhancement (6 templates)

| ID | Template | Keywords (EN) | Input |
|----|----------|---------------|-------|
| L60 | Outfit Change | outfit, clothes, wardrobe, try-on | Photo + text |
| L61 | Hairstyle Change | hairstyle, haircut, hair color | Photo + text |
| L62 | Background Change | background, backdrop, remove bg | Photo + text |
| L63 | Image Outpainting | outpaint, expand, extend canvas | Photo + direction |
| L64 | Object Removal | remove, erase, delete object | Photo + target |
| L65 | Image Enhancement | enhance, sharpen, upscale, super resolution | Photo |

### M: Media & Work (8 templates)

| ID | Template | Keywords (EN) | Input |
|----|----------|---------------|-------|
| M01 | Social Media Post | social media, Instagram, quote card | Text (+photo) |
| M02 | Poster Design | poster, flyer, banner, event | Text |
| M03 | Storyboard / Comic Strip | storyboard, comic strip, panels | Text (+photo) |
| M04 | Handwritten Poster | handwritten, bulletin, class poster | Text |
| M05 | Illustration | illustration, artwork, digital art | Text |
| M06 | YouTube Thumbnail | YouTube, thumbnail, video cover | Text (+photo) |
| M07 | Educational Visual | educational, infographic, diagram | Text |
| M08 | Picture Book Illustration | picture book, storybook, bedtime | Text |

### P: Professional Design (8 templates)

| ID | Template | Keywords (EN) | Input |
|----|----------|---------------|-------|
| P01 | E-commerce Main Image | e-commerce, product, Amazon, shop | Product photo/text |
| P02 | Sticker Set Design | sticker set, character stickers | Photo |
| P03 | Interior Design | interior, room design, home decor | Room photo |
| P04 | Logo Design | logo, brand, identity, icon | Text |
| P05 | Merchandise Design | merchandise, keychain, figure | Photo/text |
| P06 | Coloring Book Page | coloring, line art, coloring page | Text (+photo) |
| P07 | Game Asset Design | game character, concept art, game asset | Text/photo |
| P08 | Product Marketing Design | marketing, ad creative, campaign | Product + text |

---

## Section 2: Proactive Showcase

When the skill is activated and the user has NO specific image request, present this
template menu to inspire exploration. Use this EXACT format:

```
I can help you create amazing images with 74 high-quality templates! Here are the
most popular ones to try:

🎨 **STYLIZATION** (29 styles to transform your photo)
  • Chibi Cartoon — Turn yourself into an adorable Q-version character
  • 3D Pixar Animation — Become a Disney/Pixar movie character
  • Anime — Beautiful Japanese animation style portrait
  • Oil Painting — Classical masterpiece portrait
  • Game CG / Thick Paint — AAA game cutscene illustration
  • Vaporwave — 90s aesthetic with glitch effects
  • Dark Fairy Tale — Tim Burton-esque gothic whimsy
  • Gongbi / Fine Brush — Traditional Chinese meticulous painting
  • Pixel Art, Wool Felt, Pop Art, Miniature, and 18 more...

📸 **PORTRAITS & PHOTO SCENES** (18 templates)
  • K-Pop Star — Get the idol concept photo treatment
  • Film / Cinematic — Moody arthouse movie still portrait
  • Indoor Scene — Cozy café or studio apartment vibes
  • Spring Floral — Cherry blossom dreamy portrait
  • Dark Mood — Low-key dramatic emotional portrait
  • Sunset / Golden Hour — Warm backlit silhouette
  • Retro Film & Polaroid — Vintage instant camera look
  • Winter Snow — Snowflake falling ethereal portrait
  • Beach, Fantasy, Street Style, Beauty Close-up, Photo Grid...

🐾 **PETS & BABIES**
  • Pet Humanization — Your pet in a business suit
  • Pet Costume Play — Your pet's hilarious mugshot or "working" photo
  • Pet VOGUE Magazine — Your pet on a fashion magazine cover
  • Baby Comic Grid — Adorable 4-panel baby expression comic

✏️ **EDITING & ENHANCEMENT**
  • Outfit Change — Try on any clothes instantly
  • Hairstyle Change — Preview a new look
  • Background Change — Teleport to any location
  • Image Outpainting — Expand your photo canvas
  • Object Removal — Erase unwanted objects seamlessly
  • Image Enhancement — Make blurry photos crystal clear

🎯 **MEDIA & DESIGN**
  • YouTube Thumbnail — High-impact clickable video covers
  • Picture Book — Magical storybook illustrations
  • Game Asset Design — Professional concept art sheets
  • Product Marketing — Premium ad campaign visuals
  • Poster, Logo, E-commerce, Interior Design, and more...

Just upload a photo and tell me which template to use, or describe what you want
and I'll match the best template for you!
```

---

## Section 3: Intent Matching

When the user provides a request, match it to a template using these rules:

### Step 1: Check for direct keyword match

Scan the user's request (in any language) against ALL keyword columns in the
Template Registry above. If a keyword matches, select that template.

### Step 2: Check for intent patterns

| User intent pattern | Matched template |
|---------------------|-----------------|
| "turn me into" / "make me look like" + style word | L category stylization (match specific style) |
| "turn me into [style]" / "generate [style] for me" | L01-L29 |
| photo + "cartoon" / "anime" | L01 (Chibi) or L03 (Comic) |
| photo + "3D" / "Pixar" | L02 |
| photo + "sketch" / "draw" | L04 |
| photo + "clay" / "claymation" | L05 |
| photo + "Chinese style" / "ink wash" | L08 |
| photo + "watercolor" / "aquarelle" | L09 |
| photo + "oil painting" / "classical" | L15 |
| photo + "pixel" / "8-bit" / "retro game" | L16 |
| photo + "flat" / "vector" / "illustration" | L17 |
| photo + "anime" / "Japanese animation" | L18 |
| photo + "wool felt" / "needle felt" | L19 |
| photo + "colored pencil" / "crayon" | L20 |
| photo + "pop art" / "Warhol" | L21 |
| photo + "miniature" / "diorama" | L22 |
| photo + "children drawing" / "kid art" | L23 |
| photo + "game CG" / "thick paint" / "digital painting" | L24 |
| photo + "vaporwave" / "aesthetic" / "retrowave" | L25 |
| photo + "printmaking" / "woodblock" | L26 |
| photo + "gongbi" / "fine brush" | L27 |
| photo + "pen sketch" / "line drawing" | L28 |
| photo + "dark fairy tale" / "gothic" / "Tim Burton" | L29 |
| photo + "portrait" / "photoshoot" | L30 |
| photo + "ID photo" / "passport" | L31 |
| photo + "sticker" / "emoji" | L32 |
| photo + "avatar" / "profile" | L33 |
| photo + "cinematic" / "film photography" | L34 |
| photo + "dreamy" / "hazy" / "soft focus" | L35 |
| photo + "indoor" / "side angle" / "cafe" | L36 |
| photo + "dark mood" / "low-key" / "moody" | L37 |
| photo + "red wall" / "landmark" / "ancient architecture" | L38 |
| photo + "spring" / "cherry blossom" / "floral" | L39 |
| photo + "dappled light" / "tree shadow" / "sunlight" | L40 |
| photo + "sunset" / "golden hour" | L41 |
| photo + "polaroid" / "instant film" / "retro" | L42 |
| photo + "snow" / "winter" | L43 |
| photo + "beach" / "underwater" / "ocean" | L44 |
| photo + "magic" / "fantasy" / "wizard" | L45 |
| photo + "OOTD" / "Plog" / "street style" | L46 |
| photo + "grid" / "triptych" | L48 |
| pet photo + styling keywords | L50 |
| baby photo + "comic" / "grid" | L51 |
| pet photo + "magazine" / "VOGUE" | L52 |
| pet photo + "mugshot" / "costume" / "dress-up" | L53 |
| pet photo + "humanize" / "as human" | L54 |
| photo + "outfit" / "try on" / "wardrobe" | L60 |
| photo + "hairstyle" / "hair" | L61 |
| photo + "background" / "backdrop" | L62 |
| photo + "outpaint" / "expand" / "extend canvas" | L63 |
| photo + "remove" / "erase" / "delete object" | L64 |
| photo + "enhance" / "sharpen" / "upscale" | L65 |
| text about social media / quotes / cards | M01 |
| text about events / posters / flyers | M02 |
| text about stories / panels / storyboard | M03 |
| text about bulletin / handwritten poster | M04 |
| text about illustration / artwork / scene | M05 |
| text about YouTube / thumbnail / thumbnail / video cover | M06 |
| text about educational / infographic / educational / diagram | M07 |
| text about picture book / storybook / picture book | M08 |
| product + "e-commerce" / "product shot" | P01 |
| photo + "sticker set" / "sticker design" | P02 |
| room photo + "design" / "renovation" | P03 |
| text about logo / brand / identity | P04 |
| photo/text + "figurine" / "keychain" / "figure" | P05 |
| text about coloring / coloring / line art | P06 |
| text about game / game / character design / concept art | P07 |
| text/product about marketing / marketing / ad / campaign | P08 |

### Step 3: Ambiguity resolution

If multiple templates could match:
1. Prefer the MORE SPECIFIC template (e.g., "chibi cartoon" → L01, not generic L03)
2. If the user provided a photo, prefer photo-based templates
3. If still ambiguous, ask the user to choose between the top 2-3 candidates

### Step 4: No match → Fallback (Section 5)

---

## Section 4: Template Generation

Once a template is matched:

1. **Read the template** from `TEMPLATES.md` (file in the same skill directory)
2. **Fill placeholders** with user-provided information:
   - Use the user's description for `{placeholder}` values
   - For unfilled placeholders, use the `default:` value in the template
   - For photo-based templates, the user's uploaded image is the reference
3. **Construct the final prompt** by completing the template pattern
4. **Generate the image** using the appropriate mode (see "Image Generation — Dual Mode"):
   - **Mode A** (MCP tool): call `imagen_generate` with `text` = completed prompt, `image_url` = user's reference image
   - **Mode B** (script): call `generate.py` via shell or inline Python:
     ```bash
     python3 <SKILL_DIR>/scripts/generate.py "completed prompt" --image user_photo.jpg --output output.png
     ```
5. **Run Quality Check** (Section 6)
6. **Present the result** to the user with:
   - The generated image
   - A brief description of what was generated
   - 2-3 related template suggestions for further exploration

---

## Section 5: Fallback — Direct Generation (No Template Match)

When NO template in this skill matches the user's request, **generate directly**
using the user's original query as the prompt basis, without any template.

### When to Fallback

- User's request is a valid image generation/editing task, BUT does not match any
  of the 74 templates in Section 1
- User explicitly asks for something outside the template categories (e.g., food
  photography, landscape, architecture, abstract art, custom character design)
- User's intent is ambiguous after Step 3 (Section 3) and none of the top candidates
  feel like a good fit

### How to Fallback

1. **Pass the user's original query as-is** — do NOT rewrite or optimize the prompt.
   Forward the user's raw text (and reference image if provided) directly to the
   generation tool.
2. **Generate the image** using fallback priority:
   - **Priority 1: `imagen_generate` MCP tool** — the AI assistant's built-in image
     generation tool. Call it directly with the user's original query text (and
     reference image if the user provided one). This is the preferred fallback path.
   - **Priority 2: Python script** — if `imagen_generate` MCP tool is NOT available,
     use `scripts/generate.py` to call Gemini API directly via Compass (same as
     Mode B in "Image Generation — Dual Mode" above), passing the user's raw query.
3. **Run Quality Check** (Section 6 still applies)

### After Fallback Generation

- Show the result to the user
- Suggest the 2-3 closest matching templates from THIS skill for their next attempt
- Example: "I generated this using a direct prompt. Next time, you might also like
  **Cyberpunk Portrait** or **Illustration** for similar vibes!"

---

## Section 6: Quality Check & Retry

After every generation, perform a quality check based on the template category:

### Quality Criteria by Category

| Category | Critical checks |
|----------|----------------|
| L: Stylization (L01-L29) | Face identity preserved? Target style accurately applied? No artifacts? |
| L: Portrait/Scenes (L30-L48) | Face identity preserved? Scene/mood accurate? Professional quality? |
| L: Pets/Babies (L50-L54) | Pet/baby features preserved? Style consistent? Appealing result? |
| L: Editing (L60-L65) | ONLY target area changed? Everything else preserved? Natural transitions? |
| M: Media & Work (M01-M08) | All text spelled correctly? Layout professional? Visual hierarchy clear? |
| P: Professional (P01-P08) | Professional quality? Text accurate? Style appropriate for use case? |

### Retry Protocol

If the quality check identifies issues:

1. **Identify the specific failing element** (face, text, background, style, etc.)
2. **Construct a surgical edit prompt** targeting ONLY the failing element:
   ```
   "Keep everything exactly the same in this image, but fix [specific issue].
   Do not change [list of elements to preserve]."
   ```
3. **Re-generate** using the previous output as reference image + the edit prompt
4. **Maximum 2 retries** — if still failing after 2 retries, show the best result
   and explain what could be improved

### Text Accuracy Special Handling

For templates with text rendering (M01, M02, M04, P04):
- After generation, carefully verify ALL text character by character
- If any text is misspelled or malformed, always retry with emphasis:
  ```
  "Render the text EXACTLY as: '[correct text]'. Each letter must be
  perfect and clearly legible. No misspellings, no text warping."
  ```

---

## Section 7: Prompt Optimization Rules (apply to ALL templates)

These rules override any conflicting template defaults:

1. **Always English prompts** — even if user speaks Chinese, the prompt to the model must be in English
2. **Identity preservation** — for any photo-based template, always include "preserve the subject's exact facial identity" or equivalent
3. **Aspect ratio** — always state explicitly in the prompt
4. **No text unless requested** — append "No text, no watermark" unless the template specifically includes text
5. **Style anchoring** — every prompt ends with a ≤20-word style summary sentence
6. **Negative constraints** — every prompt includes 2-5 specific exclusions at the end

---

## Conversational Guidelines

- **Hide template IDs from user** — NEVER expose internal template IDs (L01, M02, P03,
  etc.) in any user-facing output, including messages, suggestions, showcase menus, and
  error text. Always refer to templates by their **display name only** (e.g., say
  "Chibi Cartoon" not "L01" or "L01 — Chibi Cartoon"). The IDs are internal-only
  identifiers reserved for backend tracing and debugging.
- **Template tracing** — Every time a template is matched or executed, record the
  template ID for analytics. **NEVER output any trace, log, or debug text in your
  response to the user** — in agent mode, ALL text output is user-visible; there is
  no stderr or hidden channel. Acceptable recording methods:
  1. Mode B (script): pass `--trace-id L01` as a CLI argument (the script handles logging)
  2. Include the template ID in the tool call arguments if the tool supports a `trace_id` field
  3. If no silent channel is available, simply skip trace logging — never compromise
     user experience for internal debugging
- **One generation at a time** — do not batch multiple templates
- **Show, don't tell** — generate first, explain after
- **Suggest next steps** — always recommend 2-3 related templates after showing a result,
  using display names only (no IDs)
- **Prefer editing over re-rolling** — if the user wants changes, upload the generated image as reference and make surgical edits
- **Respect user preferences** — if the user specifies parameters that differ from template defaults, use the user's values
