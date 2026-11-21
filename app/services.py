import requests
from typing import Dict, Any

def fetch_fmi_weather() -> Dict[str, Any]:
    """Fetches live Helsinki weather and spot prices, printing raw responses for debugging."""
    weather_url = "https://api.open-meteo.com/v1/forecast?latitude=60.1699&longitude=24.9384&current=temperature_2m,weather_code"
    spot_url = "https://api.porssisahko.net/v2/latest-prices.json"
    
    default_data = {
        "temperature_c": -2.0,
        "condition": "Normal Winter Conditions",
        "spot_price_kwh": "0.15 EUR"
    }

    temperature = None
    weather_code = None
    spot_price_cents = None

    # 1. Fetch Live Weather
    try:
        w_response = requests.get(weather_url, timeout=5)
        if w_response.status_code == 200:
            w_data = w_response.json().get("current", {})
            temperature = w_data.get("temperature_2m")
            weather_code = w_data.get("weather_code")
    except Exception as e:
        print(f"--> [Warning] Weather fetch failed: {e}")

    # 2. Fetch Live Spot Price & Print Raw Response
    try:
        s_response = requests.get(spot_url, timeout=5)
        print(f"[Spot API] Status Code: {s_response.status_code}")
        print(f"[Spot API] Raw Text: {s_response.text[:200]}...") # Print first 200 chars of response
        
        if s_response.status_code == 200:
            s_data = s_response.json()
            prices_list = s_data.get("prices", [])
            if prices_list:
                # Grab the latest available price entry
                spot_price_cents = prices_list[0].get("price")
    except Exception as e:
        print(f"--> [Warning] Spot price fetch failed: {e}")

    final_temp = temperature if temperature is not None else default_data["temperature_c"]
    final_price = f"{spot_price_cents} c/kWh (Inc. VAT)" if spot_price_cents is not None else default_data["spot_price_kwh"]
    final_condition = f"Weather Code: {weather_code}" if weather_code is not None else default_data["condition"]

    print(f"[Live Data] Temp: {final_temp}°C | Spot Price: {final_price}")

    return {
        "temperature_c": final_temp,
        "condition": final_condition,
        "spot_price_kwh": final_price
    }