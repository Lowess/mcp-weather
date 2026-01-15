import json
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with documentation enabled
mcp = FastMCP(
    "Weather MCP Server",
    description="A Model Context Protocol server providing weather alerts and forecasts using the National Weather Service API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None



@mcp.tool()
async def get_alerts(state: str) -> dict[str, Any]:
    """Get active weather alerts for a US state.

    Retrieves current weather alerts, warnings, and watches from the National Weather Service
    for the specified state. Returns formatted information including event type, affected areas,
    severity levels, descriptions, and any special instructions.

    Args:
        state: Two-letter US state code (e.g., "CA" for California, "NY" for New York, "TX" for Texas)

    Returns:
        dict[str, Any]: Structured data containing all active alerts for the state, or a message if no alerts are found

    Examples:
        >>> await get_alerts("CA")
        {"state": "CA", "alerts": [{"event": "Winter Storm Warning", "area": "Northern California Mountains", ...}], "alert_count": 1}

        >>> await get_alerts("FL")
        {"state": "FL", "alerts": [], "message": "No active alerts for this state."}
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return {"error": "Unable to fetch alerts or no alerts found."}

    if not data["features"]:
        return {
            "state": state.upper(),
            "alerts": [],
            "message": "No active alerts for this state."
        }

    alerts = []
    for feature in data["features"]:
        props = feature["properties"]
        alert = {
            "event": props.get('event', 'Unknown'),
            "area": props.get('areaDesc', 'Unknown'),
            "severity": props.get('severity', 'Unknown'),
            "description": props.get('description', 'No description available'),
            "instructions": props.get('instruction', 'No specific instructions provided')
        }
        alerts.append(alert)

    return {
        "state": state.upper(),
        "alerts": alerts,
        "alert_count": len(alerts),
        "message": f"Found {len(alerts)} active alert(s) for {state.upper()}"
    }

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> dict[str, Any]:
    """Get detailed weather forecast for a specific location.

    Retrieves the current weather forecast from the National Weather Service for the given
    coordinates. Returns a detailed forecast for the next several periods including temperature,
    wind conditions, and detailed weather descriptions.

    Args:
        latitude: Latitude coordinate of the location (decimal degrees, e.g., 37.7749 for San Francisco)
        longitude: Longitude coordinate of the location (decimal degrees, e.g., -122.4194 for San Francisco)

    Returns:
        dict[str, Any]: Structured forecast information for the next 5 periods, including temperature, wind, and detailed conditions

    Examples:
        >>> await get_forecast(37.7749, -122.4194)  # San Francisco
        {"location": {"latitude": 37.7749, "longitude": -122.4194}, "forecast_periods": [{"name": "Today", "temperature": 65, ...}]}

        >>> await get_forecast(40.7128, -74.0060)  # New York City
        {"location": {"latitude": 40.7128, "longitude": -74.0060}, "forecast_periods": [{"name": "Tonight", "temperature": 42, ...}]}
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return {"error": "Unable to fetch forecast data for this location."}

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return {"error": "Unable to fetch detailed forecast."}

    # Format the periods into a structured forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast_period = {
            "name": period['name'],
            "temperature": period['temperature'],
            "temperature_unit": period['temperatureUnit'],
            "wind_speed": period['windSpeed'],
            "wind_direction": period['windDirection'],
            "detailed_forecast": period['detailedForecast']
        }
        forecasts.append(forecast_period)

    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "forecast_periods": forecasts,
        "summary": f"5-day forecast for coordinates {latitude}, {longitude}"
    }

def main():
    """Main entry point for the weather MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
