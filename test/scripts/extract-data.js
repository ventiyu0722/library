/**
 * 从 index.html 中提取 CITIES 数组并写入 data/counties.json（仅运行一次）
 */
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
const match = html.match(/const CITIES = \[([\s\S]*?)\];\s*const btn/);
if (!match) throw new Error('CITIES array not found');
const jsArray = '[' + match[1] + ']';
const data = eval(jsArray);

const outDir = path.join(__dirname, '../data');
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, 'counties.json'), JSON.stringify(data, null, 2), 'utf8');
console.log('Wrote data/counties.json with', data.length, 'entries');
