import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';
import { getDb, initSchema } from './db.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

initSchema();

const CHINA_MAP_PNG_URL = 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/China_blank_map.svg/400px-China_blank_map.svg.png';
const CHINA_MAP_SVG_URL = 'https://upload.wikimedia.org/wikipedia/commons/9/92/China_blank_map.svg';

app.get('/assets/china-map.png', async (req, res) => {
  const file = path.join(__dirname, '..', 'assets', 'china-map.png');
  if (existsSync(file)) return res.sendFile(file);
  try {
    const r = await fetch(CHINA_MAP_PNG_URL, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    if (!r.ok) throw new Error(r.status);
    res.set('Content-Type', r.headers.get('content-type') || 'image/png');
    res.send(Buffer.from(await r.arrayBuffer()));
  } catch (e) {
    res.redirect(302, CHINA_MAP_PNG_URL);
  }
});

app.get('/assets/china-map.svg', async (req, res) => {
  const file = path.join(__dirname, '..', 'assets', 'china-map.svg');
  if (existsSync(file)) return res.sendFile(file);
  try {
    const r = await fetch(CHINA_MAP_SVG_URL, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    if (!r.ok) throw new Error(r.status);
    res.set('Content-Type', r.headers.get('content-type') || 'image/svg+xml');
    res.send(Buffer.from(await r.arrayBuffer()));
  } catch (e) {
    res.redirect(302, CHINA_MAP_SVG_URL);
  }
});

app.use(express.static(path.join(__dirname, '..')));

app.get('/api/random', (req, res) => {
  try {
    const db = getDb();
    const row = db.prepare(
      `SELECT name, food, hotel, price, food_image, food_name_en, hotel_image, hotel_name_en, province, gdp_rank, lat, lng FROM counties ORDER BY RANDOM() LIMIT 1`
    ).get();
    if (!row) {
      return res.status(404).json({ error: '暂无数据，请先执行 npm run seed' });
    }
    res.json(row);
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: '服务器错误' });
  }
});

app.listen(PORT, () => {
  console.log('Server at http://localhost:' + PORT);
});
