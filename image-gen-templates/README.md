# Image Generation — High-Heat Template Skill

74 curated high-quality prompt templates for one-click image generation via **Gemini 3.1 Flash Image** (Nano Banana 2). Organized into 3 major categories — **Life & Entertainment** (61), **Media & Work** (8), **Professional Design** (8) — covering stylization, photo scenes, portraits, pets, editing tools, social media, and professional design.

## Results

**74/74 templates** generated successfully. Average quality score: **4.70/5.0**

| Category | Templates | Description |
|----------|-----------|-------------|
| L · Stylization | 29 | Chibi, 3D Pixar, Manga, Oil Painting, Anime, Vaporwave, Gongbi, Dark Fairy Tale... |
| L · Portrait & Photo Scenes | 18 | Studio, Film, Indoor, Dark Mood, Spring Floral, Sunset, Snow, Fantasy, Beach... |
| L · Pets & Babies | 5 | Pet Stylization, Baby Comic, Pet VOGUE, Pet Costume, Pet Humanization |
| L · Editing & Enhancement | 6 | Outfit Change, Hairstyle, Background, Outpainting, Object Removal, Enhancement |
| M · Media & Work | 8 | Social Media, Poster, Storyboard, Illustration, YouTube Thumbnail, Picture Book... |
| P · Professional Design | 8 | E-commerce, Sticker Set, Interior Design, Logo, Game Asset, Product Marketing... |

## What It Does

This skill provides two workflows:

### 1. User-Initiated: Query → Template Match → Generate

```
User: "Turn my photo into a Q-version cartoon" + uploads selfie
  → Matches L01 (Chibi Cartoon)
  → Fills template prompt with user's image
  → Generates high-quality chibi character
  → Suggests related templates (3D Pixar, Clay, Comic)
```

### 2. Proactive: Skill showcases template menu on install

When activated without a specific request, the skill presents all 75 templates organized by category, inspiring users to explore what's possible.

## Template Coverage

Covers **all P0-P2 scenarios** from competitive analysis:

| Source | Scenarios Covered |
|--------|-------------------|
| **P0 — Stylization** | 29 style templates (Chibi → Dark Fairy Tale, including Game CG, Vaporwave, Gongbi, Printmaking, Pen Sketch) |
| **P0 — Portraits** | Studio, ID photo, Film/Cinematic, Dreamy, + 13 new photo scene templates (Indoor, Dark Mood, Red Wall, Spring Floral, Sunset, Polaroid, Snow, Beach, Fantasy, Street Style, Beauty Close-up, Photo Grid) |
| **P0 — Pets & Babies** | Pet stylization, baby comic grid, pet magazine, pet costume, pet humanization |
| **P1 — Editing** | Outfit change, hairstyle change, background change |
| **P1 — Enhancement** | Image outpainting (扩图), object removal (消除), image enhancement (变清晰) |
| **P1 — Social Media** | Quote cards, posters, storyboards, handwritten posters, illustrations, YouTube thumbnails |
| **P1 — Professional Design** | E-commerce, sticker sets, interior design, logos, merchandise, coloring books, game assets, product marketing |
| **豆包P图玩法** | 樱花三宫格, 室内侧拍, 暗调情绪, 红墙拍照, 春日写真, 斑驳树影, 日落时分, 车内胶片, 雪地人像, 海边写真, 魔法学院, 网感头像, 美甲特写... |
| **竞品功能** | ChatGPT, Grok, Doubao AI创作 全部覆盖 |

## Prompt Methodology

Each template uses the **General-Detail-General** prompt structure:

1. **Overview** — one-sentence transformation description
2. **Detail-Primary** — subject specifics (identity, clothing, materials)
3. **Detail-Secondary** — environment, lighting, camera, film stock
4. **Anchor** — ≤20-word style summary sentence
5. **Negative** — specific exclusions

Key techniques fused from multiple sources:
- **Identity Lock** from awesome-nano-banana-pro-prompts (10.7k stars)
- **Material Specificity** — "needle-felted wool", "matte obsidian with metallic flake"
- **Camera Language** — focal length, aperture, film stock
- **Text-First Hack** — specify all text before design elements
- **Per-Category Preservation** — exhaustive lists for editing templates

## Installation

### Claude Code

```bash
git clone https://github.com/yufei-eng/image-gen-templates.git

mkdir -p ~/.claude/skills/image-gen-templates
cp image-gen-templates/SKILL.md ~/.claude/skills/image-gen-templates/
cp image-gen-templates/TEMPLATES.md ~/.claude/skills/image-gen-templates/
```

### Cursor

```bash
mkdir -p ~/.cursor/skills/image-gen-templates
cp SKILL.md ~/.cursor/skills/image-gen-templates/
cp TEMPLATES.md ~/.cursor/skills/image-gen-templates/
```

## Requirements

- Python 3.10+
- `google-genai` package
- Compass LLM Proxy access (API key)

### Setup

```bash
# Option 1: Environment variable (recommended)
export COMPASS_API_KEY="your_api_key"

# Option 2: Config file
cp config.json.example config.json
# Edit and fill in your client_token
```

## Evaluation

Run the evaluation suite:

```bash
# Generate all legacy templates
python scripts/eval_templates.py

# Generate new templates (L24-L29, L36-L48, L63-L65)
python scripts/eval_new_templates.py

# Generate a single template
python scripts/eval_templates.py --template L01

# Build HTML report
python scripts/build_report.py
```

## Project Structure

```
├── SKILL.md                     # Main skill file (workflow + intent matching + quality checks)
├── TEMPLATES.md                 # 74 prompt templates with patterns and quality checklists
├── README.md                    # This file
├── scripts/
│   ├── generate.py              # Gemini API client via Compass LLM Proxy
│   ├── eval_templates.py        # Batch evaluation runner (legacy 53 templates)
│   ├── eval_new_templates.py    # Batch evaluation runner (22 new templates)
│   ├── build_report.py          # HTML report generator
│   ├── migrate_ids.py           # ID migration script (A/B/C/D/E/F → L/M/P)
│   └── auto_score_new.py        # Auto-scoring for new templates
├── test/
│   ├── samples/                 # Test input images
│   └── results/                 # Per-template generation results + scores.json
├── report/
│   ├── template-report.html     # Self-contained HTML report with embedded images
│   └── template-inventory.json  # Machine-readable template inventory
└── config.json                  # API configuration
```

## Key Features

- **74 curated templates** covering all major image generation use cases
- **3-category organization** — Life & Entertainment / Media & Work / Professional Design
- **Bilingual keyword matching** (English + Chinese) for intent classification
- **Quality self-check + retry** — per-category verification with surgical edit retry (max 2)
- **Proactive template showcase** — organized menu for discovery when no specific request
- **Fallback generation** — unmatched queries go directly to `generate_imagen` MCP tool or Python script
- **Editing tools** — outpainting, object removal, and image enhancement
- **Objective evaluation** — 5-dimension scoring with reproducible benchmarks

## License

MIT
