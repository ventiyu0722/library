/**
 * 爬取特色美食、四星级酒店真实图片，并下载中国地图
 * 图片源：Bing 与 DuckDuckGo 轮换（重试或 RETRY_FAILED 时优先 DuckDuckGo）
 * 中国地图：多源依次尝试（Wikipedia 400px → 800px → SVG）
 *
 * 环境变量：
 *   LIMIT=5          只处理前 5 个城市（测试用）
 *   RETRY_FAILED=1   只重试失败/缺失项，且首轮用 DuckDuckGo
 *   RETRIES=3        每个图片最多重试次数，默认 3
 *   DELAY=2500       每次请求间隔毫秒，默认 2500
 *
 * 运行: npm run crawl-images
 * 重试失败项（换源）: RETRY_FAILED=1 npm run crawl-images
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.join(__dirname, '..');
const dataPath = path.join(projectRoot, 'data', 'counties.json');
const assetsDir = path.join(projectRoot, 'assets');
const foodDir = path.join(assetsDir, 'food');
const hotelDir = path.join(assetsDir, 'hotel');
const outputJsonPath = path.join(projectRoot, 'data', 'crawled-images.json');

const LIMIT = parseInt(process.env.LIMIT || '0', 10) || 9999; // 0 表示全部
const RETRY_FAILED = process.env.RETRY_FAILED === '1';
const RETRIES = Math.max(1, parseInt(process.env.RETRIES || '3', 10));
const DELAY_MS = Math.max(1000, parseInt(process.env.DELAY || '2500', 10));

function slug(name) {
  return name.replace(/[市县区]/g, '').replace(/\s/g, '') || 'city';
}

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function downloadToFile(url, filePath) {
  const res = await fetch(url, {
    redirect: 'follow',
    headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  writeFileSync(filePath, buf);
}

async function getFirstImageUrlFromBing(page, query) {
  const searchUrl = `https://cn.bing.com/images/search?q=${encodeURIComponent(query)}&first=1`;
  await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 15000 });
  await delay(1000);
  const url = await page.evaluate(() => {
    const imgs = document.querySelectorAll('.iusc');
    for (const div of imgs) {
      const m = div.getAttribute('m');
      if (m) {
        try {
          const data = JSON.parse(m);
          if (data.murl && data.murl.startsWith('http')) return data.murl;
        } catch (_) {}
      }
    }
    const imgs2 = document.querySelectorAll('img.mimg');
    for (const img of imgs2) {
      const s = img.src || img.getAttribute('data-src');
      if (s && s.startsWith('http') && !s.includes('bing.com/th')) return s;
    }
    const grid = document.querySelector('.dg_b, .imgpt, [class*="img"]');
    if (grid) {
      const allImgs = grid.querySelectorAll('img[src]');
      for (const img of allImgs) {
        const s = img.src;
        if (s && s.startsWith('http') && (img.naturalWidth || img.width) > 100) return s;
      }
    }
    const anyImg = document.querySelector('img[src*="http"][src*=".jpg"], img[src*="http"][src*=".png"], img[src*="http"][src*=".jpeg"]');
    if (anyImg && anyImg.src) return anyImg.src;
    return null;
  });
  return url;
}

async function getFirstImageUrlFromDuckDuckGo(page, query) {
  const searchUrl = `https://duckduckgo.com/?q=${encodeURIComponent(query)}&iax=images&ia=images`;
  await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 15000 });
  await delay(1500);
  const url = await page.evaluate(() => {
    const links = document.querySelectorAll('a[data-id]');
    for (const a of links) {
      const img = a.querySelector('img');
      if (img) {
        const s = img.src || img.getAttribute('data-src');
        if (s && s.startsWith('http') && !s.includes('duckduckgo.com')) return s;
      }
    }
    const imgs = document.querySelectorAll('.tile--img__img, img[data-id]');
    for (const img of imgs) {
      const s = img.src || img.getAttribute('data-src');
      if (s && s.startsWith('http') && s.length > 20) return s;
    }
    const any = document.querySelector('img[src^="http"][src*=".jpg"], img[src^="http"][src*=".png"], img[src^="http"][src*=".jpeg"], img[src^="http"][src*=".webp"]');
    if (any && any.src) return any.src;
    return null;
  });
  return url;
}

function getImageSource(attempt, isRetryFailed) {
  if (isRetryFailed && attempt === 1) return 'duckduckgo';
  if (attempt === 1) return 'bing';
  if (attempt % 2 === 0) return 'duckduckgo';
  return 'bing';
}

async function getFirstImageUrl(page, query, source) {
  if (source === 'duckduckgo') return getFirstImageUrlFromDuckDuckGo(page, query);
  return getFirstImageUrlFromBing(page, query);
}

const CHINA_MAP_SOURCES = [
  { name: 'Wikipedia SVG (9/92)', url: 'https://upload.wikimedia.org/wikipedia/commons/9/92/China_blank_map.svg', ext: '.svg' },
  { name: 'Wikipedia 400px (9/92)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/China_blank_map.svg/400px-China_blank_map.svg.png', ext: '.png' },
  { name: 'Wikipedia grey SVG', url: 'https://upload.wikimedia.org/wikipedia/commons/2/23/China_blank_map_grey.svg', ext: '.svg' },
  { name: 'Wikipedia 800px (9/92)', url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/China_blank_map.svg/800px-China_blank_map.svg.png', ext: '.png' },
  { name: 'SimpleMaps SVG', url: 'https://simplemaps.com/static/svg/country/cn/admin1/cn.svg', ext: '.svg' },
];

async function downloadChinaMap() {
  mkdirSync(assetsDir, { recursive: true });
  const chinaMapPathPng = path.join(assetsDir, 'china-map.png');
  const chinaMapPathSvg = path.join(assetsDir, 'china-map.svg');
  if (existsSync(chinaMapPathPng) || existsSync(chinaMapPathSvg)) {
    console.log('中国地图已存在，跳过下载');
    return;
  }
  console.log('正在下载中国地图（多源尝试）...');
  for (const src of CHINA_MAP_SOURCES) {
    try {
      const outPath = src.ext === '.svg' ? chinaMapPathSvg : chinaMapPathPng;
      await downloadToFile(src.url, outPath);
      console.log('中国地图已保存:', outPath, '(' + src.name + ')');
      return;
    } catch (e) {
      console.warn('  ', src.name, '失败:', e.message);
    }
  }
  console.warn('中国地图所有源均失败，前端将使用在线兜底 URL');
}

async function main() {
  const counties = JSON.parse(readFileSync(dataPath, 'utf8'));
  let slice = counties.slice(0, LIMIT);

  let existingResults = {};
  if (RETRY_FAILED) {
    try {
      existingResults = JSON.parse(readFileSync(outputJsonPath, 'utf8'));
      const needRetry = slice.filter((row) => {
        const cur = existingResults[row.name];
        return !cur?.food_image || !cur?.hotel_image;
      });
      console.log('仅重试失败/缺失项，共', needRetry.length, '个城市需补爬');
    } catch (_) {
      console.log('未找到已有结果，将全量爬取');
    }
  }

  mkdirSync(foodDir, { recursive: true });
  mkdirSync(hotelDir, { recursive: true });

  let puppeteer;
  try {
    puppeteer = await import('puppeteer');
  } catch {
    console.error('请先安装 puppeteer: npm install puppeteer');
    process.exit(1);
  }

  await downloadChinaMap();

  const results = { ...existingResults };
  const browser = await puppeteer.default.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );
    await page.setViewport({ width: 1280, height: 800 });

    for (let i = 0; i < slice.length; i++) {
      const row = slice[i];
      const name = row.name;
      const foodQuery = row.food;
      const hotelQuery = row.hotel;
      const base = slug(name) + '_' + i;

      if (RETRY_FAILED && existingResults[name]?.food_image && existingResults[name]?.hotel_image) {
        continue;
      }
      results[name] = results[name] || { food_image: '', hotel_image: '' };

      // 美食图：已存在则直接使用，不重复爬取
      const existingFood = ['jpg', 'jpeg', 'png', 'webp'].find((e) =>
        existsSync(path.join(foodDir, base + '.' + e))
      );
      if (existingFood) {
        results[name] = results[name] || {};
        results[name].food_image = '/assets/food/' + base + '.' + existingFood;
        console.log(`[${i + 1}/${slice.length}] ${name} 美食 使用已存储`);
      } else {
        let lastErr;
        for (let attempt = 1; attempt <= RETRIES; attempt++) {
          const source = getImageSource(attempt, RETRY_FAILED);
          try {
            const foodUrl = await getFirstImageUrl(page, foodQuery, source);
            if (foodUrl) {
              let ext = path.extname(new URL(foodUrl).pathname) || '.jpg';
              ext = ext.replace(/[^a-zA-Z0-9.]/g, '') || '.jpg';
              const foodFile = path.join(foodDir, base + ext);
              await downloadToFile(foodUrl, foodFile);
              const safeExt = (ext || '.jpg').replace(/[^a-zA-Z0-9.]/g, '.jpg');
              results[name] = results[name] || {};
              results[name].food_image = '/assets/food/' + base + safeExt;
              console.log(`[${i + 1}/${slice.length}] ${name} 美食 已下载 (${source})`);
              break;
            }
          } catch (e) {
            lastErr = e;
            if (attempt < RETRIES) {
              console.warn(`[${i + 1}/${slice.length}] ${name} 美食 第${attempt}次失败(${source})，${DELAY_MS}ms 后换源重试:`, e.message);
              await delay(DELAY_MS);
            } else {
              console.warn(`[${i + 1}/${slice.length}] ${name} 美食 失败(已重试${RETRIES}次):`, e.message);
            }
          }
        }
        await delay(DELAY_MS);
      }

      // 酒店图：已存在则直接使用，不重复爬取
      const existingHotel = ['jpg', 'jpeg', 'png', 'webp'].find((e) =>
        existsSync(path.join(hotelDir, base + '.' + e))
      );
      if (existingHotel) {
        results[name] = results[name] || {};
        results[name].hotel_image = '/assets/hotel/' + base + '.' + existingHotel;
        console.log(`[${i + 1}/${slice.length}] ${name} 酒店 使用已存储`);
      } else {
        let lastErr;
        for (let attempt = 1; attempt <= RETRIES; attempt++) {
          const source = getImageSource(attempt, RETRY_FAILED);
          try {
            const hotelUrl = await getFirstImageUrl(page, hotelQuery, source);
            if (hotelUrl) {
              let extH = path.extname(new URL(hotelUrl).pathname) || '.jpg';
              extH = extH.replace(/[^a-zA-Z0-9.]/g, '') || '.jpg';
              const hotelFile = path.join(hotelDir, base + extH);
              await downloadToFile(hotelUrl, hotelFile);
              const safeExtH = (extH || '.jpg').replace(/[^a-zA-Z0-9.]/g, '.jpg');
              results[name] = results[name] || {};
              results[name].hotel_image = '/assets/hotel/' + base + safeExtH;
              console.log(`[${i + 1}/${slice.length}] ${name} 酒店 已下载 (${source})`);
              break;
            }
          } catch (e) {
            lastErr = e;
            if (attempt < RETRIES) {
              console.warn(`[${i + 1}/${slice.length}] ${name} 酒店 第${attempt}次失败(${source})，${DELAY_MS}ms 后换源重试:`, e.message);
              await delay(DELAY_MS);
            } else {
              console.warn(`[${i + 1}/${slice.length}] ${name} 酒店 失败(已重试${RETRIES}次):`, e.message);
            }
          }
        }
        await delay(DELAY_MS);
      }
    }
  } finally {
    await browser.close();
  }

  writeFileSync(outputJsonPath, JSON.stringify(results, null, 2), 'utf8');
  console.log('已写入', outputJsonPath);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
