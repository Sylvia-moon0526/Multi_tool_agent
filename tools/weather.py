from langchain_core.tools import tool
import requests
import os

@tool
def get_weather(city:str)->str:
    """获取指定城市的当前天气信息。输入城市名称（英文），返回温度和天气情况。"""
    api_key = os.environ.get("OPENWEATHER_API_KEY","your_api_here")

    if not api_key:
        return "未配置 OPENWEATHER_API_KEY 环境变量。请先注册OpenWeatherMap获取API Key."

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=zh_cn"
    try:
        resp = requests.get(url,timeout=10)
        resp.raise_for_status()
        data = resp.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]

        return(
            f"📍 {city} 天气信息\n"
            f"🌡️ 温度: {temp}°C (体感 {feels_like}°C)\n"
            f"🌤️ 天气: {description}\n"
            f"💧 湿度: {humidity}%\n"
            f"💨 风速: {wind_speed} m/s" 
        )

    except requests.exceptions.HTTPError as e:
        if resp.status_code == 404:
            return f"找不到城市 '{city}'，请检查城市名称是否正确（建议使用英文名）"
        return f"获取天气失败: HTTP {resp.status_code}"
    except Exception as e:
        return f"获取天气失败: {str(e)}"