# 推送到 GitHub 并供线上访问

按下面 **1 → 2 → 3** 顺序做即可。

---

## 第一步：在 GitHub 新建一个空仓库

1. 打开：**https://github.com/new**
2. **Repository name** 填：`county-random`（或任意英文名）
3. 选 **Public**
4. **不要**勾选 “Add a README file”
5. 点 **Create repository**
6. 记下页面上的仓库地址，例如：`https://github.com/你的用户名/county-random.git`

---

## 第二步：在终端推送代码

在终端里**依次**执行（把 `你的用户名/county-random` 换成你上一步的仓库地址）：

```bash
cd /Users/yufei/github_video_agent/test
git init
git add .
git commit -m "init: 中国城市探索者"
git branch -M main
git remote add origin https://github.com/你的用户名/county-random.git
git push -u origin main
```

- 第一次 `git push` 会要求登录 GitHub（浏览器弹窗或输入用户名/密码）。
- 若提示没有权限，可先在 GitHub 用 **Token** 代替密码，或使用 **GitHub Desktop** 做推送。

---

## 第三步：用 Railway 发布到公网

1. 打开：**https://railway.app**
2. 点 **Login** → **Login with GitHub**，用你的 GitHub 账号登录
3. 点 **New Project** → **Deploy from GitHub repo**
4. 选中你刚推送的仓库（如 `county-random`）→ 点 **Deploy Now**
5. 等构建完成（约 1～2 分钟）
6. 点进这个项目 → 点 **Settings** → 找到 **Deploy**：
   - **Start Command** 已有默认值即可（本项目用 `railway.toml`，会自动先执行 `npm run seed` 再 `npm start`）
7. 点 **Settings** → **Networking** → **Generate Domain**
8. 会生成一个链接，例如：`https://county-random-production-xxxx.up.railway.app`

把这个链接发给别人，即可在线上访问。

---

## 若推送时提示 “Support for password authentication was removed”

GitHub 已不支持用密码推送，需要改用 **Personal Access Token**：

1. 打开：**https://github.com/settings/tokens**
2. **Generate new token (classic)** → 勾选 **repo** → 生成
3. 复制生成的 token（只显示一次）
4. 在终端执行 `git push` 时，**密码**处粘贴这个 token

或使用 **GitHub Desktop** 登录账号后，在终端执行 `git push` 也会用已登录账号。

---

## 小结

| 步骤 | 做什么 |
|------|--------|
| 1 | GitHub 新建空仓库，记下地址 |
| 2 | 终端在项目目录执行 `git init` → `add` → `commit` → `remote add` → `push` |
| 3 | Railway 用 GitHub 登录 → Deploy from GitHub → 选仓库 → Generate Domain，得到公网链接 |

完成以上三步后，项目就在 GitHub 上，并且可以通过 Railway 的链接供其他人访问。
