# 发布到线上

本项目是 Node.js + Express + SQLite 应用，可按下面几种方式部署。

---

## 一、自己的服务器 / VPS（推荐）

适用：阿里云、腾讯云、DigitalOcean 等有公网 IP 的 Linux 机器。

### 1. 安装 Node.js

```bash
# 以 Ubuntu 为例
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. 上传代码并运行

```bash
# 克隆或上传项目后
cd /path/to/test
npm install --production
npm run seed
npm start
```

服务会在 3000 端口启动。如需对外访问，用 **Nginx 反代** 并配域名：

```nginx
# /etc/nginx/sites-available/your-site
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 用 PM2 常驻进程（可选）

```bash
npm install -g pm2
pm2 start server/index.js --name county-random
pm2 save
pm2 startup
```

---

## 二、Railway

1. 打开 [railway.app](https://railway.app)，用 GitHub 登录。
2. **New Project** → **Deploy from GitHub repo**，选本仓库。
3. 在项目 **Settings** 里：
   - **Build Command**：留空或 `npm install`
   - **Start Command**：`npm run seed && npm start`（首次部署会先建库再启动；若已有 DB 可只填 `npm start`）
   - **Root Directory**：仓库根目录
4. 部署完成后，在 **Settings → Networking** 里生成 **Public URL** 即可访问。

注意：Railway 重启后本地文件可能被清空，`data/counties.db` 和 `assets/` 若需保留，可：
- 把 `data/counties.db`、`assets/`、`data/counties.json`、`data/crawled-images.json` 提交到 Git，部署时一起带上；或
- 使用 Railway 的 Volume 挂载持久化目录（需在面板里配置）。

---

## 三、Render

1. 打开 [render.com](https://render.com)，用 GitHub 登录。
2. **New** → **Web Service**，连到本仓库。
3. 配置：
   - **Build Command**：`npm install`
   - **Start Command**：`npm run seed && npm start`
   - **Instance Type**：Free 或付费
4. 创建后等构建完成，用给出的 **URL** 访问。

说明：Free 实例会休眠，冷启动较慢；且重启后磁盘不持久，需把 `data/counties.db` 和 `assets/` 一并提交到仓库，或改用外部数据库/对象存储。

---

## 四、线上「出不来结果」和图片爬虫的关系

- **点击「开始随机」后完全没有结果**（没有城市名、没有卡片）：  
  一般是**数据库在线上没有生成或没被保留**，和「有没有自动爬取图片」无关。  
  解决：确保 **Start Command** 为 `npm run seed && npm start`，让每次启动都先写入数据库再开服务（见上节 Railway/Render 配置）。

- **有结果但美食/酒店/地图没有图**：  
  因为部署时**不会自动跑** `npm run crawl-images`（Puppeteer 重、耗时长、在云环境容易失败）。  
  可选做法：  
  1. 本地执行 `npm run crawl-images`，把生成的 `assets/`、`data/crawled-images.json` 提交到 Git，部署时一起带上；  
  2. 不提交图片：线上会显示 🍜🛏️ 等占位，功能正常，只是没有真实图片。

---

## 五、部署前检查

| 项目 | 说明 |
|------|------|
| 数据库 | 线上需有 `data/counties.db`。未提交到 Git 时，部署后执行一次 `npm run seed` 生成。 |
| 图片 | 若已跑过 `npm run crawl-images`，把 `assets/`、`data/crawled-images.json` 一并提交，线上无需再爬。 |
| 端口 | 多数平台用环境变量 `PORT`，本应用已支持：`const PORT = process.env.PORT \|\| 3000`。 |
| Node 版本 | 建议 Node 18+。 |

---

## 六、简要流程（以 VPS 为例）

```bash
# 服务器上
git clone <你的仓库地址> app && cd app
npm install --production
npm run seed
PORT=3000 npm start
# 或用 pm2: pm2 start server/index.js --name county-random
```

然后在 Nginx 里把域名反代到 `127.0.0.1:3000`，即可通过域名访问。
