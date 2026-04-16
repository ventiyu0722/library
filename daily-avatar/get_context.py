#!/usr/bin/env python3
"""Daily context provider — weather, LBS, lunar calendar, fortune, festivals.

Usage:
    python3 get_context.py [--city <city>] [--user-id <uid>]

Outputs structured JSON to stdout for downstream consumption by agent or frontend.
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATHS = [
    os.path.join(SCRIPT_DIR, "config.json"),
    os.path.expanduser("~/.claude/skills/daily-avatar/config.json"),
]

FORTUNE_LEVELS = [
    {"level": "小凶", "level_index": 0, "emoji": "🍵", "style_hint": "zen_retreat"},
    {"level": "吉", "level_index": 1, "emoji": "🍀", "style_hint": "warm_cozy"},
    {"level": "大吉", "level_index": 2, "emoji": "✨", "style_hint": "golden_celebration"},
    {"level": "大大吉", "level_index": 3, "emoji": "🎆", "style_hint": "lavish_festival"},
    {"level": "吉吉吉吉国王驾到！", "level_index": 4, "emoji": "👑", "style_hint": "ultra_royal"},
]
FORTUNE_WEIGHTS = [5.0, 85.0, 7.5, 2.4, 0.1]

SOLAR_FESTIVALS = {
    (1, 1): "元旦",
    (2, 14): "情人节",
    (3, 8): "妇女节",
    (3, 12): "植树节",
    (4, 1): "愚人节",
    (5, 1): "劳动节",
    (5, 4): "青年节",
    (6, 1): "儿童节",
    (7, 1): "建党节",
    (8, 1): "建军节",
    (9, 10): "教师节",
    (10, 1): "国庆节",
    (10, 31): "万圣节",
    (11, 11): "双十一",
    (12, 24): "平安夜",
    (12, 25): "圣诞节",
    (12, 31): "跨年夜",
}

SEASON_MAP = {
    1: "winter", 2: "winter", 3: "spring", 4: "spring",
    5: "spring", 6: "summer", 7: "summer", 8: "summer",
    9: "autumn", 10: "autumn", 11: "autumn", 12: "winter",
}

WEATHER_DESC_CN = {
    "Sunny": "晴朗", "Clear": "晴朗", "Partly cloudy": "多云",
    "Cloudy": "阴天", "Overcast": "阴天", "Mist": "薄雾",
    "Fog": "大雾", "Patchy rain possible": "可能有零星小雨",
    "Light rain": "小雨", "Moderate rain": "中雨", "Heavy rain": "大雨",
    "Light snow": "小雪", "Moderate snow": "中雪", "Heavy snow": "大雪",
    "Thundery outbreaks possible": "可能有雷阵雨",
    "Patchy light rain with thunder": "雷阵雨",
    "Light drizzle": "毛毛雨", "Patchy light drizzle": "零星毛毛雨",
    "Moderate or heavy rain shower": "阵雨",
    "Light rain shower": "小阵雨",
}


def _load_config() -> dict:
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                continue
    return {}


def _get_city_from_ip() -> str:
    """Detect city via IP geolocation (ipinfo.io, free tier)."""
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=5)
        data = resp.json()
        return data.get("city", "")
    except Exception:
        return ""


def _get_weather(city: str) -> dict:
    """Fetch current weather from wttr.in."""
    if not city:
        return {"temp_c": 0, "feels_like_c": 0, "desc": "未知", "humidity": 0, "wind_kmph": 0}
    try:
        resp = requests.get(
            f"https://wttr.in/{city}?format=j1",
            headers={"Accept-Language": "zh-CN"},
            timeout=8,
        )
        data = resp.json()
        cc = data.get("current_condition", [{}])[0]
        desc_en = cc.get("weatherDesc", [{}])[0].get("value", "")
        desc_cn = WEATHER_DESC_CN.get(desc_en, desc_en)
        return {
            "temp_c": int(cc.get("temp_C", 0)),
            "feels_like_c": int(cc.get("FeelsLikeC", 0)),
            "desc": desc_cn,
            "desc_en": desc_en,
            "humidity": int(cc.get("humidity", 0)),
            "wind_kmph": int(cc.get("windspeedKmph", 0)),
        }
    except Exception as e:
        print(f"[WARN] Weather fetch failed: {e}", file=sys.stderr)
        return {"temp_c": 0, "feels_like_c": 0, "desc": "未知", "humidity": 0, "wind_kmph": 0}


def _get_lunar(now: datetime.datetime) -> dict:
    """Get lunar calendar data via cnlunar."""
    try:
        import cnlunar
        lunar = cnlunar.Lunar(now, godType="8char")

        yi_list = []
        ji_list = []
        try:
            good = lunar.goodThing
            if good and isinstance(good, (list, tuple)):
                yi_list = [str(x) for x in good[:8]]
            elif good and isinstance(good, str):
                yi_list = [x.strip() for x in good.split(" ") if x.strip()][:8]
        except Exception:
            pass
        try:
            bad = lunar.badThing
            if bad and isinstance(bad, (list, tuple)):
                ji_list = [str(x) for x in bad[:8]]
            elif bad and isinstance(bad, str):
                ji_list = [x.strip() for x in bad.split(" ") if x.strip()][:8]
        except Exception:
            pass

        jieqi = ""
        try:
            st = lunar.todaySolarTerms
            if st and st != "无":
                jieqi = str(st)
        except Exception:
            pass

        lunar_festival = ""
        try:
            lf = lunar.get_otherLunarHolidays()
            if lf:
                lunar_festival = str(lf)
            lh = lunar.get_legalHolidays()
            if lh:
                lunar_festival = str(lh) if not lunar_festival else f"{lunar_festival} {lh}"
        except Exception:
            pass

        zodiac = ""
        try:
            zodiac = str(lunar.chineseYearZodiac)
        except Exception:
            pass

        eight_char = ""
        try:
            eight_char = f"{lunar.year8Char}年 {lunar.month8Char}月 {lunar.day8Char}日"
        except Exception:
            pass

        return {
            "year_cn": str(lunar.lunarYearCn),
            "month_cn": str(lunar.lunarMonthCn),
            "day_cn": str(lunar.lunarDayCn),
            "date_display": f"农历{str(lunar.lunarMonthCn).replace('大', '').replace('小', '')}{lunar.lunarDayCn}",
            "zodiac": zodiac,
            "yi": yi_list,
            "ji": ji_list,
            "jieqi": jieqi,
            "lunar_festival": lunar_festival,
            "eight_char": eight_char,
        }
    except Exception as e:
        print(f"[WARN] Lunar calendar failed: {e}", file=sys.stderr)
        return {
            "year_cn": "", "month_cn": "", "day_cn": "",
            "date_display": "农历未知", "zodiac": "",
            "yi": [], "ji": [], "jieqi": "", "lunar_festival": "", "eight_char": "",
        }


def _draw_fortune(user_id: str, date_str: str) -> dict:
    """Deterministic fortune draw: same user + same date = same result."""
    import random
    seed_str = f"{user_id}:{date_str}:daily-avatar-fortune"
    seed = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    chosen = rng.choices(FORTUNE_LEVELS, weights=FORTUNE_WEIGHTS, k=1)[0]
    return {
        "level": chosen["level"],
        "level_index": chosen["level_index"],
        "display": f"{chosen['level']} {chosen['emoji']}",
        "style_hint": chosen["style_hint"],
    }


def get_daily_context(city: str = "", user_id: str = "local") -> dict:
    """Collect all daily context in one call. Parallelizes network requests."""
    cfg = _load_config()
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    resolved_city = city
    if not resolved_city:
        resolved_city = cfg.get("user", {}).get("city", "")

    weather_result = {}
    ip_city = ""

    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {}
        if not resolved_city:
            futures["ip"] = pool.submit(_get_city_from_ip)
        futures["lunar"] = pool.submit(_get_lunar, now)

        if "ip" in futures:
            try:
                ip_city = futures["ip"].result(timeout=6)
            except Exception:
                ip_city = ""
            if not resolved_city:
                resolved_city = ip_city

        weather_result = _get_weather(resolved_city)

        try:
            lunar_result = futures["lunar"].result(timeout=5)
        except Exception:
            lunar_result = _get_lunar(now)

    solar_festival = SOLAR_FESTIVALS.get((now.month, now.day), "")
    fortune = _draw_fortune(user_id, date_str)
    season = SEASON_MAP.get(now.month, "unknown")

    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekday_names[now.weekday()]

    return {
        "user_id": user_id,
        "city": resolved_city or "未知",
        "weather": weather_result,
        "lunar": lunar_result,
        "solar_festival": solar_festival,
        "fortune": fortune,
        "date_str": f"{now.year}年{now.month}月{now.day}日 {weekday}",
        "season": season,
        "generated_at": now.astimezone().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Daily Avatar Context Provider")
    parser.add_argument("--city", default="", help="City name for weather (auto-detect if empty)")
    parser.add_argument("--user-id", default="local", help="User ID for deterministic fortune")
    args = parser.parse_args()

    result = get_daily_context(city=args.city, user_id=args.user_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
