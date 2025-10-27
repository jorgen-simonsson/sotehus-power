# Backend Modules

This directory contains backend modules for the spot price dashboard.

## Modules

### `spotprice.py`
Spot price API client for fetching Swedish electricity prices from elprisetjustnu.se.

**Key Functions:**
- `get_spot_prices(region)` - Fetch all price data for a region
- `get_current_spot_price(price_data)` - Get current price from data
- `get_current_price(region)` - Convenience method for current price

### `mqtt_client.py`
MQTT client for monitoring real-time power consumption.

**Key Features:**
- Connects to MQTT broker
- Subscribes to power consumption topic
- Callback support for real-time updates
- Automatic reconnection handling

## Usage

Import these modules in the frontend application:

```python
from src.backend.spotprice import SpotPriceClient
from src.backend.mqtt_client import MQTTPowerClient
```

## Testing

Run the application to test all backend modules:

```bash
python run_nicegui.py
```
