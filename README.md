# Weather MCP Server 🌤️

A Model Context Protocol (MCP) server that provides weather alerts and forecasts using the National Weather Service API.

## Features

- 🚨 **Weather Alerts**: Get active weather alerts for any US state
- 🌡️ **Weather Forecasts**: Get detailed forecasts for specific coordinates
- 📖 **Interactive Documentation**: Swagger UI and ReDoc endpoints
- 🚀 **Streamable HTTP**: Fast HTTP transport for MCP communication

## Quick Start with uvx

The easiest way to run the server is using `uvx`:

```bash
# Run directly from the current directory
uvx --from . weather-server

# Or run the main module directly
uvx --python 3.10 --from . --spec weather main:main
```

## Alternative Running Methods

### Using Python directly
```bash
python main.py
```

### Using uv (if you have uv installed)
```bash
uv run python main.py
```

## API Documentation

Once the server is running, you can access:

- **MCP Endpoint**: http://localhost:8080/mcp
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI Schema**: http://localhost:8080/openapi.json

## Available Tools

### get_alerts(state: str)
Get active weather alerts for a US state.

**Parameters:**
- `state`: Two-letter US state code (e.g., "CA", "NY", "TX")

**Example:**
```python
await get_alerts("CA")  # Get alerts for California
```

### get_forecast(latitude: float, longitude: float)
Get detailed weather forecast for specific coordinates.

**Parameters:**
- `latitude`: Latitude in decimal degrees (e.g., 37.7749)
- `longitude`: Longitude in decimal degrees (e.g., -122.4194)

**Example:**
```python
await get_forecast(37.7749, -122.4194)  # San Francisco forecast
```

## Development

### Install Dependencies
```bash
uv sync
```

### Run in Development Mode
```bash
uv run python main.py
```

## Requirements

- Python 3.10+
- httpx
- mcp[cli]
- fastmcp

All dependencies are managed via `pyproject.toml` and can be installed automatically with `uv` or `uvx`.
