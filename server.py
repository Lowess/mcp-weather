from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with documentation enabled
mcp = FastMCP(
    "weather",
    title="Weather MCP Server",
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

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get active weather alerts for a US state.

    Retrieves current weather alerts, warnings, and watches from the National Weather Service
    for the specified state. Returns formatted information including event type, affected areas,
    severity levels, descriptions, and any special instructions.

    Args:
        state: Two-letter US state code (e.g., "CA" for California, "NY" for New York, "TX" for Texas)

    Returns:
        str: Formatted string containing all active alerts for the state, or a message if no alerts are found

    Examples:
        >>> await get_alerts("CA")
        "Event: Winter Storm Warning\\nArea: Northern California Mountains..."

        >>> await get_alerts("FL")
        "No active alerts for this state."
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get detailed weather forecast for a specific location.

    Retrieves the current weather forecast from the National Weather Service for the given
    coordinates. Returns a detailed forecast for the next several periods including temperature,
    wind conditions, and detailed weather descriptions.

    Args:
        latitude: Latitude coordinate of the location (decimal degrees, e.g., 37.7749 for San Francisco)
        longitude: Longitude coordinate of the location (decimal degrees, e.g., -122.4194 for San Francisco)

    Returns:
        str: Formatted forecast information for the next 5 periods, including temperature, wind, and detailed conditions

    Examples:
        >>> await get_forecast(37.7749, -122.4194)  # San Francisco
        "Today: Temperature: 65°F Wind: 10 mph W Forecast: Partly cloudy..."

        >>> await get_forecast(40.7128, -74.0060)  # New York City
        "Tonight: Temperature: 42°F Wind: 5 mph NE Forecast: Clear skies..."
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

def main():
    """Main entry point for the weather MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
