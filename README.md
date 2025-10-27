# ⚡ Swedish Electricity Spot Price & Power Monitoring Dashboard

A real-time web dashboard for monitoring Swedish electricity spot prices and household power consumption. Built with [NiceGUI](https://nicegui.io/) - a Python-based web framework that's easy to use and deploy.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![NiceGUI](https://img.shields.io/badge/NiceGUI-1.4+-purple)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **Real-Time Spot Prices**: Live electricity spot prices for all Swedish regions (SE1-SE4)
- **Power Consumption Monitoring**: Real-time power usage via MQTT integration
- **Solar Production Monitoring**: Real-time solar panel production via SolarEdge API
- **Auto-Updating Interface**: UI refreshes every 3 seconds with latest data
- **Multi-Client Support**: Clean handling of multiple browser connections without memory leaks
- **Region Selection**: Easy switching between Swedish electricity regions
- **Minimal Dependencies**: Simple Python-based architecture

## 📊 Data Sources

### 1. Electricity Spot Prices

**Provider**: [elprisetjustnu.se](https://www.elprisetjustnu.se/)

**API Endpoint**: `https://www.elprisetjustnu.se/api/v1/prices/{year}/{month-day}_{region}.json`

**Regions Supported**:
- **SE1**: Northern Sweden (Luleå area)
- **SE2**: Central Sweden (Sundsvall area)
- **SE3**: Southern Sweden (Stockholm area)
- **SE4**: Southern Sweden (Malmö area)

**Data Format**: 
- Price in SEK/kWh (öre/kWh)
- Updated every 15 minutes by Nord Pool
- Historical and current 15-minute interval data
- No API key required

**Example Response**:
```json
[
  {
    "SEK_per_kWh": 0.85,
    "EUR_per_kWh": 0.078,
    "EXR": 10.89,
    "time_start": "2025-10-27T00:00:00+02:00",
    "time_end": "2025-10-27T00:15:00+02:00"
  },
  {
    "SEK_per_kWh": 0.87,
    "EUR_per_kWh": 0.080,
    "EXR": 10.89,
    "time_start": "2025-10-27T00:15:00+02:00",
    "time_end": "2025-10-27T00:30:00+02:00"
  }
]
```

### 2. Real-Time Power Consumption

**Protocol**: MQTT (Message Queuing Telemetry Transport)

**Compatible Sources**:
- Home Assistant energy monitoring
- Zigbee2MQTT power outlets/meters
- Shelly energy monitors
- Tibber Pulse
- Any MQTT-enabled power meter

**Message Format**:
```json
{
  "power": 1580.5
}
```
or simply:
```
1580.5
```

**Configuration**: Via environment variables (`.env` file)
```bash
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
MQTT_TOPIC=home/power/consumption
```

### 3. Solar Production Data

**Provider**: SolarEdge Monitoring API

**API Endpoint**: `https://monitoringapi.solaredge.com`

**Features**:
- Real-time power production (Watts)
- Daily, monthly, yearly energy totals
- Power flow (PV → Grid, Battery, Load)
- Battery status and charge level
- System status and alerts

**Authentication**: API Key required

**Configuration**: Via environment variables (`.env` file)
```bash
SOLAREDGE_API_KEY=your_api_key_here
SOLAREDGE_SITE_ID=your_site_id_here
```

**Data Retrieved**:
- Current power production (W)
- Energy produced today/month/year/lifetime (Wh)
- Power flow between PV, grid, battery, and load
- Battery charge level and status
- Site information and installation details

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- MQTT broker (optional, for power monitoring)
- Internet connection (for spot price data)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd spot
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MQTT & SolarEdge** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your MQTT broker details and SolarEdge API credentials
   ```

5. **Run the application**:
   ```bash
   python run_nicegui.py
   ```

6. **Open in browser**:
   ```
   http://localhost:8080
   ```

## 🖥️ UI Functionality

### Main Dashboard

The dashboard is divided into three main sections:

#### 1. **Spot Price Section**
- **Current Price Display**: Large, bold display of current electricity price in SEK/kWh
- **Region Selector**: Dropdown menu to switch between SE1, SE2, SE3, SE4
- **Last Updated Timestamp**: Shows when the price was last fetched
- **Auto-Fetch**: Automatically loads price on page load
- **Visual Feedback**: Loading spinner during data fetch
- **Error Handling**: Clear error messages if API is unavailable

#### 2. **Power Consumption Section**
- **Real-Time Display**: Current household power consumption in Watts (W)
- **Connection Status**: 
  - 🟢 Green indicator when MQTT is connected
  - Visual feedback while connecting
  - Error messages if connection fails
- **Auto-Updates**: Refreshes every 3 seconds with new data
- **Last Updated Timestamp**: Shows when the last power reading was received
- **Reconnection**: Automatic retry on connection loss

#### 3. **Information Section**
- **About**: Description of the service and data source
- **Region Guide**: Explains which region corresponds to which area in Sweden
- **Helpful Tips**: Usage information and context

### Technical UI Features

#### Real-Time Updates
- **Per-Client Generators**: Each browser connection gets its own update stream
- **3-Second Refresh Rate**: Configurable update frequency
- **No Polling Overhead**: Efficient websocket-based updates
- **State Synchronization**: All connected clients see the same data

#### Connection Management
- **Automatic Cleanup**: Disconnected clients are immediately removed
- **No Memory Leaks**: Proper generator lifecycle management
- **Multi-Tab Support**: Open multiple browser tabs without conflicts
- **Graceful Disconnection**: Clean shutdown when browser closes

#### Responsive Design
- **Modern UI**: Clean, card-based layout
- **Centered Layout**: Professional appearance on all screen sizes
- **Color-Coded Status**: Visual indicators for connection states
- **Icon Integration**: Emoji icons for visual appeal (⚡, 🏠, 🟢)

## 📁 Project Structure

```
spot/
├── src/
│   ├── backend/                # Backend modules
│   │   ├── spotprice.py       # Spot price API client
│   │   ├── mqtt_client.py     # MQTT power monitoring
│   │   ├── solar_edge.py      # SolarEdge solar production API
│   │   └── README.md          # Module documentation
│   └── frontend/              # Frontend web application
│       ├── nicegui_app.py     # Main application file
│       └── README.md          # Frontend-specific docs
├── examples/
│   └── solar_edge_example.py  # SolarEdge usage example
├── run_nicegui.py             # Launcher script
├── requirements.txt           # Python dependencies
├── .env.example               # Configuration template
└── README.md                  # This file
```

## 🔧 Configuration

### MQTT Configuration

Edit `.env` file to configure your MQTT broker:

```bash
# Local Mosquitto broker
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_TOPIC=home/power/consumption

# Home Assistant
MQTT_BROKER_HOST=homeassistant.local
MQTT_USERNAME=ha_user
MQTT_PASSWORD=your_password
MQTT_TOPIC=sensor/power_meter/state

# Cloud MQTT (HiveMQ, CloudMQTT, etc.)
MQTT_BROKER_HOST=your-broker.hivemq.cloud
MQTT_BROKER_PORT=8883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
MQTT_TOPIC=home/power
```

### SolarEdge Configuration

To get your SolarEdge API credentials:

1. **Log into SolarEdge Monitoring Portal**:
   ```
   https://monitoring.solaredge.com
   ```

2. **Generate API Key**:
   - Go to **Admin** → **API Access**
   - Read and accept the terms and conditions
   - Click **Generate API Key**
   - Copy the generated key

3. **Find Site ID**:
   - In your SolarEdge portal, the Site ID is visible in the URL
   - Or go to **Site Admin** → **Site Details**
   - Copy the Site ID number

4. **Add to .env file**:
   ```bash
   SOLAREDGE_API_KEY=L4QLVQ1LOKCQX2193VSEICXW61NP6B1O
   SOLAREDGE_SITE_ID=123456
   ```

5. **Test the integration**:
   ```bash
   python examples/solar_edge_example.py
   ```

To change the UI update frequency, modify the sleep duration in `src/frontend/nicegui_app.py`:

```python
async def _update_loop(self):
    while True:
        await asyncio.sleep(3)  # Change this value (in seconds)
        # ... rest of code
```

## 🏗️ Architecture

### Data Flow

```
┌─────────────────────┐
│   Spot Price API    │
│ (elprisetjustnu.se) │
└──────────┬──────────┘
           │ HTTP GET
           ↓
┌─────────────────────┐      ┌──────────────────┐
│   SpotPriceClient   │      │  MQTT Broker     │
│  (src/backend)      │      │                  │
└──────────┬──────────┘      └────────┬─────────┘
           │                          │ Subscribe
           │                          ↓
           │                 ┌──────────────────┐
           │                 │  MQTTPowerClient │
           │                 │  (src/backend)   │
           │                 └────────┬─────────┘
           │                          │
           ↓                          ↓
┌─────────────────────────────────────────────┐
│          Global Shared State                │
│  (_latest_power_data, spot price cache)    │
└──────────────────┬──────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────┐
│         Background Update Task              │
│      (asyncio.create_task)                  │
└──────────────────┬──────────────────────────┘
                   │ Every 3 seconds
                   ↓
┌─────────────────────────────────────────────┐
│         NiceGUI UI Components               │
│     (Direct label/text updates)             │
└──────────────────┬──────────────────────────┘
                   │ HTTP/WebSocket
                   ↓
┌─────────────────────────────────────────────┐
│         Browser Clients                     │
│        (NiceGUI frontend)                   │
└─────────────────────────────────────────────┘
```

### Key Components

1. **SpotPriceClient** (`src/backend/spotprice.py`):
   - Fetches 15-minute interval spot prices from Swedish API
   - Returns current interval's price as float
   - Handles date formatting and region selection

2. **MQTTPowerClient** (`src/backend/mqtt_client.py`):
   - Connects to MQTT broker
   - Subscribes to power consumption topic
   - Updates global shared state on each message via callback

3. **NiceGUI Dashboard** (`src/frontend/nicegui_app.py`):
   - Single dashboard instance with UI components
   - Background asyncio task for periodic updates
   - Direct UI manipulation (no state management layer)
   - Simple and straightforward architecture

4. **Update Pattern**:
   - Background task runs continuously
   - Polls global state every 3 seconds
   - Directly updates UI labels and text elements
   - Thread-safe access with locks

## 🐛 Troubleshooting

### MQTT Connection Issues

**Problem**: "Failed to connect to MQTT broker"

**Solutions**:
- Check broker is running: `mosquitto -v` (if using Mosquitto)
- Verify credentials in `.env` file
- Test connection: `mosquitto_sub -h localhost -t '#' -v`
- Check firewall settings

### Spot Price Not Updating

**Problem**: Old or no spot price displayed

**Solutions**:
- Check internet connection
- Verify API is accessible: `curl https://www.elprisetjustnu.se/api/v1/prices/2025/10-27_SE4.json`
- Try different region
- Check browser console for errors

### High CPU Usage

**Problem**: Application uses excessive CPU

**Solutions**:
- Increase sleep duration in update loop (from 3 to 5+ seconds)
- Close unused browser tabs
- Check system resource usage

### Port Already in Use

**Problem**: "Port 8080 already in use"

**Solutions**:
- Kill existing process: `lsof -ti:8080 | xargs kill -9`
- Change port in `nicegui_app.py`: `ui.run(port=8081)`
- Find and stop other services using port 8080

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **elprisetjustnu.se** - For providing free Swedish electricity spot price API
- **NiceGUI Team** - For the simple and elegant Python web framework
- **Nord Pool** - Source of spot price data
- **Python Community** - For excellent libraries and tools

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review NiceGUI documentation at [nicegui.io](https://nicegui.io/)

---

**Built with ❤️ in Sweden** 🇸🇪
