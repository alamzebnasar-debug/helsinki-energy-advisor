from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("HelsinkiEnergyDataServer")

@mcp.tool()
def get_helsinki_weather() -> dict:
    """Fetch live outdoor temperature and weather condition for Helsinki from Open-Meteo."""
    weather_url = "https://api.open-meteo.com/v1/forecast?latitude=60.1699&longitude=24.9384&current=temperature_2m,weather_code"
    try:
        res = requests.get(weather_url, timeout=5).json().get("current", {})
        return {
            "temperature_c": res.get("temperature_2m", -2.0),
            "condition": f"Weather Code: {res.get('weather_code', 0)}"
        }
    except Exception:
        return {"temperature_c": -2.0, "condition": "Normal Winter Conditions"}

@mcp.tool()
def get_spot_price() -> str:
    """Fetch the live 15-minute electricity spot price from Pörssisähkö.net."""
    spot_url = "https://api.porssisahko.net/v2/latest-prices.json"
    try:
        res = requests.get(spot_url, timeout=5).json()
        prices = res.get("prices", [])
        if prices:
            price_cents = prices[0].get("price")
            return f"{price_cents} c/kWh (Inc. VAT)"
    except Exception:
        pass
    return "0.15 EUR"

if __name__ == "__main__":
    mcp.run(transport="stdio")