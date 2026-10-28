import streamlit as st
import requests

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️")

st.title("🌤️ Weather Dashboard")
st.write("Enter a city to see its current weather.")

city = st.text_input("City", value="San Francisco")

# Open-Meteo uses coordinates, so first look up the city.
def get_coordinates(city_name):
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city_name, "count": 1, "language": "en"},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[0] if results else None


# Convert the weather code from the API into readable text.
def describe_weather(code):
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Light snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        95: "Thunderstorm",
    }
    return descriptions.get(code, "Unknown conditions")


if st.button("Get weather"):
    if not city.strip():
        st.error("Please enter a city name.")
    else:
        try:
            location = get_coordinates(city.strip())

            if not location:
                st.error(f"Could not find “{city}”. Check the spelling and try again.")
            else:
                response = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": location["latitude"],
                        "longitude": location["longitude"],
                        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                        "timezone": "auto",
                    },
                    timeout=10,
                )
                response.raise_for_status()
                current = response.json()["current"]

                st.subheader(f"{location['name']}, {location.get('country', '')}")
                st.write(describe_weather(current["weather_code"]))

                col1, col2, col3 = st.columns(3)
                col1.metric("Temperature", f"{current['temperature_2m']} °C")
                col2.metric("Feels like", f"{current['apparent_temperature']} °C")
                col3.metric("Wind speed", f"{current['wind_speed_10m']} km/h")

                st.caption(
                    f"Humidity: {current['relative_humidity_2m']}% · "
                    f"Updated: {current['time']}"
                )

        except requests.RequestException as error:
            st.error(f"Could not retrieve weather data: {error}")