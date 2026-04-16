# Daily Avatar Generator

基于用户头像 + 当日环境（天气/农历/运势/心情）生成个性化每日头像。

## 功能

- **模式1 — 每日随机头像**：抽运势 + 天气/农历宜忌 → 风格化头像 + 打工牛马文案
- **模式2 — 心情头像**：结构化心情采集 → 共情风格头像 + 走心文案
- **[P1] 参考图搜索**：联网搜索头像候选图，多样性筛选

## 运势风格

| 运势 | 概率 | 风格 |
|------|------|------|
| 小凶 | 5% | 禅意水墨风 — 喝杯茶歇一歇 🍵 |
| 吉 | 85% | 暖色日常 — 金色阳光温馨感 🍀 |
| 大吉 | 7.5% | 金光庆典 — 璀璨祥云 ✨ |
| 大大吉 | 2.4% | 华丽节庆 — 烟花红金 🎆 |
| 国王驾到 | 0.1% | 极致皇家 — 皇冠紫金 👑 |

## 技术栈

- **图像生成**: Gemini 3.1 Flash Image (via Compass LLM Proxy)
- **天气**: wttr.in (免费，无需 API key)
- **农历/宜忌**: cnlunar (《钦定协纪辨方书》数据)
- **LBS**: ipinfo.io (IP 定位) + 手动配置
- **图片搜索**: Serper API

## 安装

```bash
pip3 install -r requirements.txt
cp config.json.example config.json
# 编辑 config.json，填入 compass_api.client_token
```

## 使用

### 作为 Claude Code / Cursor Skill

将目录放到 `~/.claude/skills/daily-avatar/`，在对话中说"帮我生成今日头像"即可触发。

### 命令行工具

```bash
# 获取今日环境上下文
python3 get_context.py --city Shenzhen

# 生成头像（需要参考图）
python3 generate_avatar.py "<prompt>" <reference_image> --output-dir ./output

# 搜索参考图（需要 Serper API key）
python3 search_images.py "赛博朋克风格头像" --count 5
```

## 输出格式

所有脚本输出结构化 JSON，支持前端组件渲染和后端 API 化。详见 [SKILL.md](SKILL.md)。

## 数据模型

```
AvatarGeneration {
  id, user_id, mode, reference_avatar,
  context { city, weather, lunar, fortune },
  mood?, prompt, generated_image, caption,
  created_at
}
```

面向千/万级用户扩展：`user_id` 贯穿全链路，历史记录 schema 兼容数据库迁移。
