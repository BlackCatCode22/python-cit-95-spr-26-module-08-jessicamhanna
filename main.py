from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Existing NWS Fetcher (for Fresno and NYC)
def fetch_nws_summary(lat, lon, city_name):
    headers = {"User-Agent": "FCC-Student-App"}
    try:
        res = requests.get(f"https://api.weather.gov/points/{lat},{lon}", headers=headers)
        forecast_url = res.json()["properties"]["forecast"]
        forecast_res = requests.get(forecast_url, headers=headers)
        today = forecast_res.json()["properties"]["periods"][0]

        return {
            "city": city_name,
            "temp": today["temperature"],
            "unit": today["temperatureUnit"],
            "condition": today["shortForecast"],
            "icon": today["icon"],
            "detailed": today["detailedForecast"]
        }
    except Exception:
        return {"city": city_name, "temp": "N/A", "condition": "Error fetching NWS data"}


# New Open-Meteo Fetcher (for London)
def fetch_open_meteo(lat, lon, city_name):
    try:
        # Open-Meteo parameters: current_weather=true and imperial units to match NWS
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=fahrenheit"
        res = requests.get(url)
        data = res.json()["current_weather"]

        return {
            "city": city_name,
            "temp": int(data["temperature"]),
            "unit": "F",
            "condition": "Current Conditions",  # Open-Meteo uses codes, showing text for now
            "icon": "https://api.weather.gov/icons/land/day/few?size=medium",  # Placeholder icon
            "detailed": f"Current windspeed is {data['windspeed']} km/h."
        }
    except Exception:
        return {"city": city_name, "temp": "N/A", "condition": "Error fetching Open-Meteo data"}


@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    fresno = fetch_nws_summary(36.7378, -119.7871, "Fresno")
    nyc = fetch_nws_summary(40.7128, -74.0060, "New York")
    # London, UK Coordinates
    london = fetch_open_meteo(51.5074, -0.1278, "London")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "locations": [fresno, nyc, london]
    })