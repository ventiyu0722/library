# 中国 GDP Top 200 县级市 · 随机抽取

前端点击「开始随机！」从后端 SQLite 中随机抽一个县级市，展示城市名、特色美食、最低价四星级酒店及价格。

## 结构

- **前端**：`index.html`，请求 `/api/random` 获取随机一条
- **后端**：`server/index.js`（Express），SQLite 数据库文件 `data/counties.db`
- **数据**：`data/counties.json` 为原始数据；`npm run seed` 将其写入数据库

## 使用

```bash
npm install
npm run seed    # 首次或更新数据后执行，生成 data/counties.db
npm start       # 启动服务，访问 http://localhost:3000
```

## 真实图片（预下载存储，访问时不爬取）

- **美食图、酒店图、中国地图均为预下载到本地**：仅在开发/部署时执行一次 `npm run crawl-images`，脚本会从 Bing 图片搜索下载每个城市的特色美食、最低四星级酒店图片，以及中国地图，保存到 `assets/food/`、`assets/hotel/`、`assets/china-map.png`。
- **用户打开页面时不会进行任何爬取**：前端只请求 `/api/random` 和静态资源；接口返回的 `food_image`、`hotel_image` 为本地路径（如 `/assets/food/xxx.jpg`），浏览器直接加载已存储的图片，无实时爬虫。
- 爬取结果写入 `data/crawled-images.json`；执行 `npm run seed` 后，数据库会使用这些本地路径。若某张图已存在，再次运行 `npm run crawl-images` 会跳过该图、直接使用已存储文件。
- 测试可加条数限制：`LIMIT=5 npm run crawl-images` 只处理前 5 个城市。
- **有失败时**：每个图片会自动重试最多 3 次，且**重试时会换源**（Bing ↔ DuckDuckGo）；可再执行 **`RETRY_FAILED=1 npm run crawl-images`** 只补爬失败/缺失项（此时首轮用 DuckDuckGo）。中国地图会依次尝试 Wikipedia 400px → 800px → SVG 多个源。可选：`RETRIES=5`、`DELAY=3000`。

## 数据库

- 库文件：`data/counties.db`（SQLite）
- 表：`counties(id, name, food, hotel, price)`
- 修改数据：编辑 `data/counties.json` 后重新执行 `npm run seed`

## 发布到线上

详见 **[DEPLOY.md](./DEPLOY.md)**，包含：自己的服务器/VPS（Nginx + PM2）、Railway、Render 等部署方式。
