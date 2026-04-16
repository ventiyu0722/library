---
name: daily-avatar
description: >-
  Generates personalized daily avatars based on user's reference photo combined with
  real-time context (weather, lunar calendar, fortune, mood). Supports two modes:
  daily random avatar with fortune, and mood-based emotional avatar. Use when the user
  asks to generate a daily avatar, personalized avatar, fortune avatar, mood avatar,
  today's avatar, or 每日头像/运势头像/心情头像.
argument-hint: "[reference_image_path] or ask me to search for one"
---

# Daily Avatar Generator

基于用户头像 + 当日环境（天气/农历/运势/心情）生成个性化每日头像。

## When to Use

用户要求生成：每日头像、今日头像、运势头像、心情头像、个性化头像、daily avatar。
或用户说：帮我生成今天的头像、今天适合什么头像、给我做个头像。

## Tools

| Script | 调用方式 | 作用 |
|--------|----------|------|
| `get_context.py` | `python3 <SKILL_DIR>/get_context.py [--city <city>] [--user-id <uid>]` | 获取天气/农历/运势/节日，输出 JSON |
| `generate_avatar.py` | `python3 <SKILL_DIR>/generate_avatar.py "<prompt>" <ref_img> [--output-dir <dir>] [--user-id <uid>]` | 调用 Gemini 3.1 Flash Image 生成头像 |
| `search_images.py` | `python3 <SKILL_DIR>/search_images.py "<query>" [--count 5]` | [P1] 联网搜索头像候选图 |

`<SKILL_DIR>` = `~/.claude/skills/daily-avatar`

### Config

`~/.claude/skills/daily-avatar/config.json` 存储用户配置：
- `compass_api.client_token`: Compass API token（或设置环境变量 `COMPASS_CLIENT_TOKEN`）
- `user.city`: 用户所在城市（留空则自动 IP 定位）
- `user.reference_avatar`: 用户原始头像路径（首次设定后持久化）
- `search_api.api_key`: Serper API key（P1 图片搜索用，或设置 `SERPER_API_KEY`）

## Workflow

按以下步骤严格执行。总 Gemini API 调用 = **1 次**（仅图像生成），文案由你自己生成。

### Step 0 — 参考图确认

读取 config.json 的 `user.reference_avatar`：

- **有值且文件存在** → 简要告知用户"将基于已保存的头像生成"，继续 Step 1
- **无值 + 用户消息中附带了图片** → 保存路径到 config.json `user.reference_avatar`，继续 Step 1
- **无值 + 用户给了搜索 query** → 调用 `search_images.py "<query>" --count 5`
  - 展示候选图给用户（列出 index + 缩略描述）
  - 用户选择后，将 `local_path` 写入 config.json `user.reference_avatar`
  - 继续 Step 1
- **无值 + 什么都没给** → 问用户：
  - "请提供一张头像作为参考图（直接发图片，或告诉我想搜什么风格的头像）"
  - 等待用户响应后重新进入 Step 0

### Step 1 — 模式判断

根据用户意图判断模式：

| 用户意图信号 | 模式 |
|-------------|------|
| "每日头像" "今日运势" "随机头像" "帮我生成头像"（无心情描述）| **模式1: 每日随机** |
| "心情头像" "我今天心情..." 提及情绪词 "不开心" "开心" "累" | **模式2: 今日心情** |
| 不确定 | 问用户："想生成每日运势头像，还是基于你现在的心情来定制？" |

### Step 2 — 环境数据采集

```bash
python3 <SKILL_DIR>/get_context.py [--city <city>] [--user-id <uid>]
```

解析返回的 JSON，提取所有字段备用。这是 **唯一的数据采集调用**。

### Step 3 — [仅模式2] 心情采集

以资深心理咨询师的视角，用温和友好的语气进行结构化问询。

问题设计原则：
- 总共 3-5 题，不要太多造成压力
- 选择题为主 + 最后可选自由输入
- Q4/Q5 仅在 Q1 回答偏负面时触发
- 每题之间给予简短温暖回应

**问题列表**（输出为结构化格式，前端可渲染为选择组件）：

**Q1**: 今天整体感觉怎么样？
- A. 心情不错 😊
- B. 还算平静 😌
- C. 有点累了 😮‍💨
- D. 不太好 😔

**Q2**: 现在最想做什么？
- A. 出去走走 🚶
- B. 窝在家里 🏠
- C. 找人聊聊 💬
- D. 独处放空 🌙

**Q3**: 如果用天气来形容现在的内心，你觉得是？
- A. 晴空万里 ☀️
- B. 多云微风 ⛅
- C. 绵绵细雨 🌧️
- D. 电闪雷鸣 ⛈️

**Q4** (仅当 Q1 = C 或 D)：这种感觉大概什么时候开始的？
- A. 就今天
- B. 最近几天
- C. 已经有一阵子了

**Q5** (仅当 Q1 = C 或 D，可选)：如果愿意说，主要是因为什么呢？
- 自由输入（提示：工作/生活/关系/身体... 不想说也完全没关系）

收集完答案后，综合分析出：
- `mood_keyword`: 核心情绪词（如 "疲惫但平静"、"开心且充满活力"）
- `mood_analysis`: 一句话情绪分析（供 prompt 使用）
- `empathy_tone`: 文案共情程度（happy→多幽默, calm→平衡, tired/down→多温暖）

### Step 4 — Prompt 构建

根据模式和上下文数据，按以下模板构建 prompt。

**重要原则**（来自 Google 官方 Gemini Prompt Guide）：
- 叙述式描述，不要堆砌关键词
- 先描述主体，再描述风格，最后写约束
- 身份保留指令要明确具体
- 1:1 方形输出适合头像使用

#### 模式1: 每日随机头像 Prompt 模板

```
Transform this portrait photo into a stylized personalized avatar while completely
preserving the subject's facial identity — face shape, features, skin tone, and
expression must remain immediately recognizable.

Today's context: Fortune level is「{fortune.display}」. Weather in {city}: {weather.desc},
{weather.temp_c}°C (feels like {weather.feels_like_c}°C). Date: {date_str},
{lunar.date_display}.
{如有 solar_festival 或 lunar.lunar_festival: "Special occasion: {festival}. Weave thematic elements into the composition."}
{如有 lunar.jieqi: "Solar term: {jieqi}. Reflect this seasonal energy in the atmosphere."}
Auspicious today: {取 lunar.yi 前3个}. Avoid: {取 lunar.ji 前2个}.

Visual style direction — apply the style matching fortune「{fortune.style_hint}」:
- zen_retreat: Warm monochrome ink-wash illustration style, like a Japanese manga
  or Chinese ink painting with gentle cross-hatching. Muted grayscale palette with
  subtle warm undertones. Subject sits peacefully in a cozy indoor setting — tatami
  mat, a warm cup of tea in hand, bonsai nearby, soft light through paper screen
  window. Deeply calm and contemplative. The vibe is: "today is not the day to fight
  the world — just sip tea and exist peacefully." Slice-of-life manga aesthetic.
- warm_cozy: Warm golden-hour tones. Soft bokeh background of {season} scenery.
  Subject wrapped in cozy atmosphere — gentle sunlight, floating dust motes.
  Like a cherished film photograph on Kodak Gold 200.
- golden_celebration: Radiant golden glow emanating from behind the subject.
  Auspicious cloud motifs, scattered cherry blossoms or confetti.
  Rich amber and champagne color palette. Celebratory but elegant.
- lavish_festival: Full festival aesthetic — fireworks blooming overhead,
  traditional red and gold palette, ornate decorative borders.
  Subject wearing a subtle festive accessory. Luxurious and joyful.
- ultra_royal: Ultra-premium royal portrait. Ornate golden crown, deep purple
  velvet backdrop with gold filigree. Divine light rays from above.
  Subject radiates sovereign confidence. Museum-quality oil painting meets digital art.

Background should subtly reflect {city}'s {weather.desc} weather and {season} season.
The avatar must feel premium, modern, and perfect for social media profile use.
Square 1:1 aspect ratio. Polished illustration style with clean lines and rich detail.
No text, no watermark, no UI elements, no extra characters.
```

#### 模式2: 今日心情头像 Prompt 模板

```
Transform this portrait photo into an emotionally expressive personalized avatar
that deeply captures the feeling of「{mood_keyword}」, while completely preserving
the subject's facial identity.

Emotional context: {mood_analysis}
Environment: {city}, {weather.desc}, {weather.temp_c}°C. {lunar.date_display}.
{如有 festival: "Atmosphere hint: {festival}."}

Color palette and emotional direction — choose based on mood:
- Happy/Excited: Vibrant warm tones — amber, coral, sunflower yellow. Dynamic
  composition with upward energy. Sparkles or light bokeh. Subject's expression
  enhanced with a subtle extra warmth in the eyes.
- Calm/Peaceful: Soft pastels — sage green, lavender, powder blue. Zen
  composition with generous breathing space. Gentle side-lighting.
  Like a quiet moment in a Studio Ghibli film.
- Tired/Drained: Muted earth tones as base, but with ONE warm accent light
  source (a candle glow, sunset through window, warm lamp). Cozy protective
  atmosphere — think blanket, warm drink, rain on window. The warmth says
  "it's okay to rest."
- Anxious/Stressed: Cool tones transitioning to warm — like a storm clearing.
  Composition suggests movement from chaos toward calm. A small reassuring
  element (a hand holding a warm cup, a patch of blue sky breaking through clouds).

The avatar should feel like a gentle emotional mirror — the viewer recognizes
their own feeling in it and feels understood.
Background elements should reflect {weather.desc} weather, blending with the emotional tone.
Therapeutic suggestion woven in: today is good for {取 lunar.yi 第1个}.
Square 1:1 portrait. Polished illustration style. No text, no watermark.
```

### Step 5 — 图像生成

```bash
python3 <SKILL_DIR>/generate_avatar.py "<constructed_prompt>" <reference_avatar_path> [--output-dir <dir>]
```

解析返回的 JSON。如果 `success: false`，告知用户错误并建议重试。

### Step 6 — 文案生成

基于 context + 生成结果，你自己生成配套文案（不要额外调用模型）。

#### 模式1 文案风格：抽象搞笑打工牛马风

- 人设：打工人视角，自嘲但乐观，带点互联网黑话
- 格式：`{天气描述}，{农历宜忌}，运势{等级}——{搞笑建议}`
- 例子：
  - "深圳28°C多云，农历二月廿八宜祈福，运势吉——老天都说今天适合跪求甲方不要改需求 🍀"
  - "上海15°C小雨，农历三月初十宜出行，运势大吉——适合带着简历出门，说不定在路上偶遇贵人（或者偶遇地铁故障）✨"
  - "北京-2°C大雪，农历腊月十五诸事不宜，运势小凶——今天建议装死，活儿明天再干 💀"
  - "成都22°C晴朗，运势吉吉吉吉国王驾到！——今天你就是办公室里最靓的崽，建议直接跟老板提涨薪 👑"

#### 模式2 文案风格：走心共情 + 轻微幽默

- 人设：理解你的朋友
- 幽默比例：心情好→60%幽默, 平静→40%幽默, 累/不好→20%幽默+80%温暖
- 格式：`{共情开头}。{天气+宜忌建议}。{温暖收尾}`
- 例子：
  - 开心时："心情好就是生产力！深圳28°C晴朗，农历廿八宜出行——下班后去海边吹吹风呗，打工人也值得拥有夕阳"
  - 平静时："保持平静本身就是一种力量。今天多云微风，宜修身——适合泡杯好茶，做个安静的美男子/女子"
  - 疲惫时："有点累了对吧，这很正常。今天26°C微风正好，宜休息——就算不想出门，打开窗户让风吹吹也好。你已经很棒了。"
  - 低落时："嗯，今天不太好也没关系。阴天22°C，农历廿八宜祈福——不用逼自己开心，给自己泡杯热的吧。低谷是弯道，不是终点。"

### Step 7 — 结构化输出

组装最终结果并展示给用户。同时输出结构化 JSON 供前端渲染：

```json
{
  "type": "daily_avatar_result",
  "mode": "daily|mood",
  "avatar": {
    "image_path": "...",
    "image_size_kb": 245.3
  },
  "context": { ... },
  "fortune": { ... },
  "mood": { ... },
  "caption": "今日文案...",
  "generated_at": "..."
}
```

展示时：
1. 先展示生成的头像图片
2. 展示文案
3. 展示运势/心情标签
4. 简要说明："如果想调整风格，可以告诉我具体想改什么"

## Refinement

如果用户对结果不满意：
- **风格不对** → 在 prompt 中增加/修改风格描述，重新调用 generate_avatar.py
- **保留度不够** → 在 prompt 开头强化："The subject's face must be EXACTLY preserved — this is the highest priority"
- **氛围不对** → 调整色调/光照描述
- 每次精修只改一个方面，最多重试 2 次

## Output for Frontend

所有工具输出均为结构化 JSON，可直接用于前端组件：

| 数据 | 对应前端组件 |
|------|-------------|
| 心情问卷 (Q1-Q5) | 选择题按钮组 / 自由输入框 |
| 头像候选图 (search_images) | 图片网格选择器 |
| 生成结果 (avatar + caption) | 头像卡片 + 文案气泡 |
| 运势信息 (fortune) | 运势标签/徽章 |
| 环境信息 (weather + lunar) | 信息摘要条 |
