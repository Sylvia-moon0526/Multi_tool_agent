from langchain_core.tools import tool
import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10

_CITY_ALIAS = {
    "北京": "beijing", "上海": "shanghai", "广州": "guangzhou", "深圳": "shenzhen",
    "成都": "chengdu", "重庆": "chongqing", "天津": "tianjin", "武汉": "wuhan",
    "西安": "xi'an", "杭州": "hangzhou", "南京": "nanjing", "苏州": "suzhou",
    "长沙": "changsha", "郑州": "zhengzhou", "青岛": "qingdao", "大连": "dalian",
    "厦门": "xiamen", "福州": "fuzhou", "昆明": "kunming", "哈尔滨": "harbin",
}

_WMO_ZH = {
    0: "晴", 1: "基本晴朗", 2: "局部多云", 3: "阴",
    45: "有雾", 48: "雾凇雾",
    51: "小毛毛雨", 53: "毛毛雨", 55: "密集毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨", 81: "强阵雨", 82: "强雷阵雨",
    95: "雷阵雨", 96: "雷阵雨伴小冰雹", 99: "雷阵雨伴大冰雹",
}


def _city_key(city: str) -> str:
    city = city.strip()
    return _CITY_ALIAS.get(city, city.replace(" ", "+").strip())


def _weathercode_zh(code: int) -> str:
    return _WMO_ZH.get(code, f"(天气编码 {code})")


@tool
def get_weather(city: str) -> str:
    """获取指定城市的当前天气信息。输入城市名称（中文或英文均可），返回温度和天气情况。"""
    if not city or not city.strip():
        return "请提供城市名称，例如：北京 / beijing"

    query = _city_key(city)

    try:
        geo_resp = requests.get(GEO_URL, params={"name": query, "count": 1, "language": "zh"}, timeout=TIMEOUT)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            return f"找不到城市 '{city}'，请检查城市名称是否正确。"

        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        display_name = loc.get("name", city)

        f_resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat, "longitude": lon,
                "current_weather": "true",
                "timezone": "auto",
            },
            timeout=TIMEOUT,
        )
        f_resp.raise_for_status()
        f = f_resp.json()["current_weather"]

        temp = f["temperature"]
        wind = f.get("windspeed", "?")
        code = f.get("weathercode", 0)
        desc = _weathercode_zh(code)

        return (
            f"📍 {display_name} 天气信息\n"
            f"🌡️ 温度: {temp}°C (体感约 {temp}°C)\n"
            f"🌤️ 天气: {desc}\n"
            f"💨 风速: {wind} km/h"
        )

    except requests.exceptions.Timeout:
        return f"获取 {city} 天气超时，请稍后重试。"
    except Exception as e:
        return f"获取天气失败: {str(e)}"