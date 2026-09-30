import requests
from flask import current_app

def get_weather(lat, lon):
    key = current_app.config.get("WEATHER_API_KEY", "")
    if not key:
        return {"available": False, "reason": "no_key"}
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": key, "units": "metric"},
            timeout=5
        )
        r.raise_for_status()
        d = r.json()
        icon_map = {
            "01": "☀️",  "02": "⛅",  "03": "☁️",  "04": "☁️",
            "09": "🌧️", "10": "🌦️", "11": "⛈️",  "13": "❄️",  "50": "🌫️"
        }
        icon_code = d["weather"][0]["icon"][:2]
        return {
            "available": True,
            "city":      d.get("name", ""),
            "temp":      round(d["main"]["temp"]),
            "feels":     round(d["main"]["feels_like"]),
            "humidity":  d["main"]["humidity"],
            "desc":      d["weather"][0]["description"].capitalize(),
            "emoji":     icon_map.get(icon_code, "🌡️"),
            "wind":      round(d["wind"]["speed"] * 3.6),
        }
    except Exception:
        return {"available": False, "reason": "error"}


def get_news():
    key = current_app.config.get("NEWS_API_KEY", "")
    if not key:
        return {"available": False, "reason": "no_key"}
    try:
        r = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"language": "en", "pageSize": 5, "apiKey": key},
            timeout=5
        )
        r.raise_for_status()
        articles = r.json().get("articles", [])
        return {
            "available": True,
            "articles": [
                {
                    "title":  a["title"],
                    "source": a["source"]["name"],
                    "url":    a["url"],
                }
                for a in articles if a.get("title") and "[Removed]" not in a["title"]
            ]
        }
    except Exception:
        return {"available": False, "reason": "error"}
