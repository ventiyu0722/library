import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dbPath = path.join(__dirname, '..', 'data', 'counties.db');

let db = null;

export function getDb() {
  if (!db) {
    db = new Database(dbPath);
    db.pragma('journal_mode = WAL');
  }
  return db;
}

export function initSchema() {
  const database = getDb();
  database.exec(`
    CREATE TABLE IF NOT EXISTS counties (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      food TEXT NOT NULL,
      hotel TEXT NOT NULL,
      price INTEGER NOT NULL,
      food_image TEXT,
      food_name_en TEXT,
      hotel_image TEXT,
      hotel_name_en TEXT,
      province TEXT,
      gdp_rank INTEGER,
      lat REAL,
      lng REAL
    );
    CREATE INDEX IF NOT EXISTS idx_counties_name ON counties(name);
  `);
  migrateAddColumns(database);
}

function migrateAddColumns(db) {
  const cols = ['food_image', 'food_name_en', 'hotel_image', 'hotel_name_en', 'province', 'gdp_rank', 'lat', 'lng'];
  const info = db.pragma('table_info(counties)');
  const existing = new Set(info.map((c) => c.name));
  for (const col of cols) {
    if (!existing.has(col)) {
      const type = (col === 'gdp_rank' ? 'INTEGER' : col === 'lat' || col === 'lng' ? 'REAL' : 'TEXT');
      db.exec(`ALTER TABLE counties ADD COLUMN ${col} ${type}`);
    }
  }
}
