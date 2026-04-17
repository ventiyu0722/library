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

### L: 生活与娱乐 Life & Entertainment (58 templates)

#### Stylization (29 templates)

| ID | Template | Keywords (EN) | Keywords (ZH) | Input |
|----|----------|---------------|---------------|-------|
| L01 | Chibi Cartoon | chibi, Q-version, cute cartoon, mini me | Q版, 卡通, 萌版, 迷你 | Photo |
| L02 | 3D Pixar Animation | 3D, Pixar, Disney, animated | 3D, 皮克斯, 迪士尼, 动画 | Photo |
| L03 | Comic / Manga | comic, manga, graphic novel | 漫画, 日漫 | Photo |
| L04 | Sketch / Pencil | sketch, pencil, drawing, graphite | 素描, 铅笔画, 手绘 | Photo |
| L05 | Clay / Claymation | clay, claymation, plasticine, stop-motion | 黏土, 粘土, 定格动画 | Photo |
| L06 | 80s Retro Animation | 80s, retro, synthwave, vintage cartoon | 80年代, 复古, 怀旧动画 | Photo |
| L07 | Retro-Futurism | retro-future, space age, vintage sci-fi | 未来复古, 复古科幻 | Photo |
| L08 | Ukiyo-e / Chinese Painting | ukiyo-e, Chinese painting, ink wash | 浮世绘, 国画, 国风, 古风, 水墨 | Photo |
| L09 | Watercolor Portrait | watercolor, aquarelle, painting | 水彩, 水彩画 | Photo |
| L10 | K-Pop Star | K-Pop, Korean idol, idol photo | K-Pop, 韩风, 韩国偶像, 明星 | Photo |
| L11 | Imperial / Royal | imperial, royal, king, queen, emperor | 帝王, 皇帝, 王室, 帝王范 | Photo |
| L12 | 90s Yearbook | 90s, yearbook, high school, retro photo | 90年代, 毕业照, 复古照 | Photo |
| L13 | High Fashion | high fashion, vogue, editorial, couture | 高级时尚, 时尚大片, 杂志 | Photo |
| L14 | Cyberpunk Portrait | cyberpunk, neon, cyber, futuristic | 赛博朋克, 赛博, 霓虹 | Photo |
| L15 | Oil Painting / Classical | oil painting, classical, renaissance | 油画, 古典, 印象派 | Photo |
| L16 | Pixel Art | pixel art, 8-bit, retro game, 16-bit | 像素, 像素风, 像素画 | Photo |
| L17 | Flat / Vector Illustration | flat, vector, minimalist illustration | 平面插画, 扁平风, 矢量 | Photo |
| L18 | Anime / 二次元 | anime, 二次元, Japanese animation | 二次元, 动漫, 番剧 | Photo |
| L19 | Wool Felt / Needle Felt | wool felt, needle felt, felted | 羊毛毡, 毛毡, 手工毡 | Photo |
| L20 | Colored Pencil | colored pencil, Prismacolor, crayon | 彩铅, 彩铅画, 彩色铅笔 | Photo |
| L21 | Pop Art | pop art, Warhol, Lichtenstein | 波普, 波普艺术, 名画风 | Photo |
| L22 | Miniature / Diorama | miniature, diorama, tilt-shift | 微缩景观, 微缩, 小人国 | Photo |
| L23 | Children's Drawing | children drawing, kid art, crayon | 儿童绘画, 儿童画, 童画 | Photo |
| L24 | Game CG / Thick Paint | game CG, digital painting, thick paint | 游戏CG, CG厚涂, 厚涂 | Photo |
| L25 | Vaporwave | vaporwave, aesthetic, retrowave, glitch | 蒸汽波, 蒸汽波美学 | Photo |
| L26 | Printmaking / Woodblock | printmaking, woodblock, linocut | 版画, 木版画, 油墨印刷 | Photo |
| L27 | Fine Brush / Gongbi | gongbi, fine brush, meticulous | 工笔, 新工笔, 工笔画 | Photo |
| L28 | Pen Sketch / Simple Line | pen sketch, line drawing, ink pen | 钢笔速写, 简笔画, 线描 | Photo |
| L29 | Dark Fairy Tale | dark fairy tale, gothic, Tim Burton | 暗黑童话, 哥特, 暗黑 | Photo |

#### Portrait & Photo Scenes (18 templates)

| ID | Template | Keywords (EN) | Keywords (ZH) | Input |
|----|----------|---------------|---------------|-------|
| L30 | Studio Photoshoot | photoshoot, studio, professional portrait | 写真, 棚拍, 专业照 | Photo |
| L31 | ID Photo | ID photo, passport, headshot | 证件照, 一寸照, 登记照 | Photo |
| L32 | Emoji / Sticker Pack | emoji, sticker, emoticon | 表情包, 贴纸, 表情 | Photo |
| L33 | Avatar / Profile Picture | avatar, profile, pfp, icon | 头像, 个性头像, 头像生成 | Photo |
| L34 | Film / Cinematic Portrait | film photography, cinematic, movie still | 电影写真, 胶片, 电影感 | Photo |
| L35 | Dreamy / Hazy Portrait | dreamy, hazy, soft focus, ethereal | 朦胧, 朦胧肖像, 梦幻 | Photo |
| L36 | Indoor Scene Portrait | indoor, side angle, restaurant vintage | 室内侧拍, 室内自拍, 室内, 餐厅复古 | Photo |
| L37 | Dark Mood Portrait | dark mood, low-key, moody | 暗调, 暗调情绪, 低调 | Photo |
| L38 | Iconic Location Shot | red wall, landmark, Forbidden City | 红墙, 中天门, 摩崖造像, 古建筑 | Photo |
| L39 | Spring Floral Portrait | spring, cherry blossom, pear blossom | 春日写真, 樱花, 梨花, 蔷薇 | Photo |
| L40 | Natural Light & Shadow | dappled light, tree shadow, sunlight | 斑驳树影, 阳光特写, 发丝发光 | Photo |
| L41 | Sunset / Golden Hour | sunset, golden hour, silhouette | 日落, 落日叠影, 黄金时段 | Photo |
| L42 | Retro Film & Polaroid | polaroid, film, vintage camera | 车内胶片, 拍立得, 古早自拍 | Photo |
| L43 | Winter Snow Portrait | winter, snow, frosty, cold | 下雪天, 雪地人像, 冬季写真, 清冷雪景 | Photo |
| L44 | Beach & Underwater | beach, underwater, ocean, diving | 海边写真, 水下写真, 水中 | Photo |
| L45 | Fantasy / Magical Scene | magic, wizard, fantasy, spell | 魔法学院, 变成岛主, 星空眼眸 | Photo |
| L46 | Social Media / Street Style | OOTD, Plog, street style | 网感头像, OOTD, Plog, 站姐 | Photo |
| L48 | Photo Grid Layout | grid, triptych, photo grid | 三宫格, 樱花三宫格, 宫格 | Photo |

#### Pets & Babies (5 templates)

| ID | Template | Keywords (EN) | Keywords (ZH) | Input |
|----|----------|---------------|---------------|-------|
| L50 | Pet Stylization | cute pet, pet portrait, kawaii pet | 萌宠, 宠物造型, 宠物 | Pet photo |
| L51 | Baby Comic Grid | baby comic, baby expressions, grid | 宝宝, 宝宝漫画, 宫格 | Baby photo |
| L52 | Pet VOGUE Magazine | pet magazine, pet cover, VOGUE | 宠物杂志, 宠物封面 | Pet photo |
| L53 | Pet Costume Play | pet costume, pet mugshot, pet dress-up | 宠物入狱, 萌宠打工, 宠物变装 | Pet photo |
| L54 | Pet Humanization | pet humanization, anthropomorphic | 宠物拟人, 宠物拟人化 | Pet photo |

#### Try-on, Editing & Enhancement (6 templates)

| ID | Template | Keywords (EN) | Keywords (ZH) | Input |
|----|----------|---------------|---------------|-------|
| L60 | Outfit Change | outfit, clothes, wardrobe, try-on | 换装, 换衣服, 试穿 | Photo + text |
| L61 | Hairstyle Change | hairstyle, haircut, hair color | 发型, 换发型, 理发 | Photo + text |
| L62 | Background Change | background, backdrop, remove bg | 换背景, 抠图, 背景 | Photo + text |
| L63 | Image Outpainting | outpaint, expand, extend canvas | 扩图, 扩展, 外扩 | Photo + direction |
| L64 | Object Removal | remove, erase, delete object | 消除, 擦除, 移除物体 | Photo + target |
| L65 | Image Enhancement | enhance, sharpen, upscale, super resolution | 变清晰, 增强, 超分辨率 | Photo |

### M: 日常工作与自媒体 Media & Work (8 templates)

| ID | Template | Keywords (EN) | Keywords (ZH) | Input |
|----|----------|---------------|---------------|-------|
| M01 | Social Media Post | social media, Instagram, quote card | 配图, 朋友圈, 社交, 名言 | Text (+photo) |
| M02 | Poster Design | poster, flyer, banner, event | 海报, 传单, 横幅 | Text |
| M03 | Storyboard / Comic Strip | storyboard, comic strip, panels | 分镜, 漫画条, 故事板 | Text (+photo) |
| M04 | Handwritten Poster | handwritten, bulletin, class poster | 手抄报, 板报 | Text |
| M05 | Illustration | illustration, artwork, digital art | 插画, 插图, 绘画 | Text |
| M06 | YouTube Thumbnail | YouTube, thumbnail, video cover | YouTube缩略图, 封面, 视频封面 | Text (+photo) |
| M07 | Educational Visual | educational, infographic, diagram | 教育, 知识图, 教学图 | Text |
| M08 | Picture Book Illustration | picture book, storybook, bedtime | 绘本, 童话, 儿童读物 | Text |

### P: 专业设计 Professional Design (8 templates)

| ID | Template | Keywords (EN) | Keywords (ZH) | Input |
|----|----------|---------------|---------------|-------|
| P01 | E-commerce Main Image | e-commerce, product, Amazon, shop | 电商, 头图, 产品图 | Product photo/text |
| P02 | Sticker Set Design | sticker set, character stickers | 贴纸集, 表情贴纸 | Photo |
| P03 | Interior Design | interior, room design, home decor | 家装, 室内设计, 装修 | Room photo |
| P04 | Logo Design | logo, brand, identity, icon | Logo, 标志, 品牌 | Text |
| P05 | Merchandise Design | merchandise, keychain, figure | 手办, 钥匙扣, 周边 | Photo/text |
| P06 | Coloring Book Page | coloring, line art, coloring page | 涂色, 线稿, 涂色页 | Text (+photo) |
| P07 | Game Asset Design | game character, concept art, game asset | 游戏, 游戏角色, 游戏资产 | Text/photo |
| P08 | Product Marketing Design | marketing, ad creative, campaign | 营销, 广告, 产品营销 | Product + text |

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
  • Anime / 二次元 — Beautiful Japanese animation style portrait
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
| "turn me into" / "变成" / "make me look like" + style word | L category stylization (match specific style) |
| "把我变成" / "帮我生成...风格" | L01-L29 |
| photo + "cartoon" / "anime" / "卡通" / "动漫" | L01 (Chibi) or L03 (Comic) |
| photo + "3D" / "皮克斯" / "Pixar" | L02 |
| photo + "sketch" / "draw" / "素描" | L04 |
| photo + "clay" / "黏土" | L05 |
| photo + "古风" / "国风" / "水墨" | L08 |
| photo + "水彩" / "watercolor" | L09 |
| photo + "油画" / "oil painting" / "classical" / "古典" | L15 |
| photo + "像素" / "pixel" / "8-bit" / "retro game" | L16 |
| photo + "扁平" / "flat" / "vector" / "平面插画" | L17 |
| photo + "二次元" / "anime" / "动漫" / "番剧" | L18 |
| photo + "羊毛毡" / "wool felt" / "needle felt" / "毛毡" | L19 |
| photo + "彩铅" / "colored pencil" / "彩色铅笔" | L20 |
| photo + "波普" / "pop art" / "Warhol" / "名画风" | L21 |
| photo + "微缩" / "miniature" / "diorama" / "小人国" | L22 |
| photo + "儿童画" / "children drawing" / "kid art" / "童画" | L23 |
| photo + "游戏CG" / "game CG" / "厚涂" / "digital painting" | L24 |
| photo + "蒸汽波" / "vaporwave" / "aesthetic" / "retrowave" | L25 |
| photo + "版画" / "printmaking" / "woodblock" / "木版画" | L26 |
| photo + "工笔" / "gongbi" / "fine brush" / "新工笔" | L27 |
| photo + "速写" / "简笔画" / "pen sketch" / "line drawing" | L28 |
| photo + "暗黑童话" / "dark fairy tale" / "gothic" / "Tim Burton" | L29 |
| photo + "写真" / "portrait" / "photoshoot" | L30 |
| photo + "证件照" / "ID photo" / "passport" | L31 |
| photo + "表情包" / "sticker" / "emoji" | L32 |
| photo + "头像" / "avatar" / "profile" | L33 |
| photo + "电影" / "cinematic" / "film photography" / "胶片" | L34 |
| photo + "朦胧" / "dreamy" / "hazy" / "梦幻" / "soft focus" | L35 |
| photo + "室内" / "indoor" / "室内侧拍" / "餐厅" | L36 |
| photo + "暗调" / "dark mood" / "low-key" / "暗调情绪" | L37 |
| photo + "红墙" / "red wall" / "中天门" / "摩崖造像" / "古建筑" | L38 |
| photo + "春日" / "樱花" / "cherry blossom" / "梨花" / "蔷薇" | L39 |
| photo + "树影" / "斑驳" / "dappled light" / "阳光" / "发丝发光" | L40 |
| photo + "日落" / "sunset" / "golden hour" / "落日" | L41 |
| photo + "拍立得" / "polaroid" / "车内胶片" / "古早自拍" | L42 |
| photo + "雪" / "snow" / "冬季" / "冬天" / "下雪" | L43 |
| photo + "海边" / "beach" / "水下" / "underwater" / "ocean" | L44 |
| photo + "魔法" / "magic" / "fantasy" / "wizard" / "魔法学院" | L45 |
| photo + "OOTD" / "Plog" / "网感" / "street style" / "站姐" | L46 |
| photo + "三宫格" / "grid" / "triptych" / "宫格" | L48 |
| pet photo + styling keywords | L50 |
| baby photo + "漫画" / "comic" / "grid" | L51 |
| pet photo + "杂志" / "magazine" / "VOGUE" | L52 |
| pet photo + "入狱" / "mugshot" / "打工" / "costume" / "变装" | L53 |
| pet photo + "拟人" / "humanize" / "as human" | L54 |
| photo + "换装" / "换衣服" / "try on" / "outfit" | L60 |
| photo + "发型" / "hairstyle" / "hair" | L61 |
| photo + "背景" / "background" | L62 |
| photo + "扩图" / "outpaint" / "expand" / "extend canvas" | L63 |
| photo + "消除" / "remove" / "erase" / "擦除" / "删除物体" | L64 |
| photo + "变清晰" / "enhance" / "sharpen" / "upscale" / "超分辨率" | L65 |
| text about social media / quotes / cards | M01 |
| text about events / posters / flyers | M02 |
| text about stories / panels / storyboard | M03 |
| text about 手抄报 / bulletin | M04 |
| text about illustration / artwork / scene | M05 |
| text about YouTube / thumbnail / 缩略图 / video cover | M06 |
| text about educational / infographic / 教育 / diagram | M07 |
| text about picture book / 绘本 / storybook / 童话 | M08 |
| product + "电商" / "e-commerce" / "product shot" | P01 |
| photo + "贴纸集" / "sticker set" | P02 |
| room photo + "设计" / "design" / "装修" | P03 |
| text about logo / brand / identity | P04 |
| photo/text + "手办" / "钥匙扣" / "figure" | P05 |
| text about coloring / 涂色 / line art | P06 |
| text about game / 游戏 / character design / concept art | P07 |
| text/product about marketing / 营销 / ad / campaign / 广告 | P08 |

### Step 3: Ambiguity resolution

If multiple templates could match:
1. Prefer the MORE SPECIFIC template (e.g., "Q版卡通" → L01, not generic L03)
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
