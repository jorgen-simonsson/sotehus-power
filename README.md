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

**Rate Limits**:
- 300 API calls per day per API key
- Dashboard updates every 60 seconds to stay within limits

**Configuration**: Via environment variables (`.env` file)
```bash
SOLAREDGE_API_KEY=your_api_key_here
SOLAREDGE_SITE_ID=your_site_id_here
```

**Data Retrieved**:
- **Current Power Production**: Live power output in Watts (W) or kilowatts (kW)
- **Production Status**: Visual indicators for production state (producing/idle)
- **Energy Totals**: Daily, monthly, yearly, and lifetime energy production
- **Power Flow**: Real-time flow between PV panels, grid, battery, and household load
- **Battery Information**: Charge level, charging/discharging status
- **System Status**: Inverter status, alerts, and system health

**API Endpoints Used**:
```
GET /site/{siteId}/currentPowerFlow.json
GET /site/{siteId}/overview.json
GET /site/{siteId}/details.json
```

**Response Example** (Current Power Flow):
```json
{
  "siteCurrentPowerFlow": {
    "PV": {
      "currentPower": 2847.0,
      "status": "Active"
    },
    "LOAD": {
      "currentPower": 1580.5,
      "status": "Active"
    },
    "GRID": {
      "currentPower": -1266.5,
      "status": "Active"
    },
    "STORAGE": {
      "currentPower": 0,
      "chargeLevel": 85,
      "status": "Idle"
    }
  }
}
```

**Display Format**:
- Power < 1000W: Displayed as "XXX.X W"
- Power ≥ 1000W: Displayed as "X.XX kW"
- Status Icons:
  - ☀️ Producing power (> 0W)
  - 🌙 No production (0W)
  - ❓ Status unknown (no data)

**Auto-Configuration**:
- If SolarEdge credentials are not provided, the solar panel section is automatically hidden
- No errors shown if SolarEdge is not configured (optional feature)
- Graceful degradation - app works fine without solar monitoring

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

#### 3. **Solar Production Section** (Optional)
- **Real-Time Display**: Current solar power production in Watts (W) or kilowatts (kW)
- **Production Status**:
  - ☀️ Producing power (when panels are generating electricity)
  - 🌙 No production (nighttime or cloudy conditions)
  - ❓ Status unknown (if data unavailable)
- **Auto-Updates**: Refreshes every 60 seconds (respects API rate limits)
- **Last Updated Timestamp**: Shows when the last solar reading was received
- **Auto-Hide**: Section is hidden if SolarEdge is not configured
- **Smart Display**:
  - Shows power in W for values < 1000W
  - Shows power in kW for values ≥ 1000W

#### 4. **Information Section**
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

To enable solar production monitoring, you'll need SolarEdge API credentials:

#### Step 1: Log into SolarEdge Monitoring Portal

Visit the SolarEdge monitoring website:
```
https://monitoring.solaredge.com
```

Log in with your SolarEdge account credentials.

#### Step 2: Generate API Key

1. Navigate to **Admin** → **Site Access** → **API Access**
2. Read and accept the API Terms and Conditions
3. Click **Generate API Key**
4. **Important**: Copy the API key immediately - you won't be able to see it again!

**Example API Key format**: `L4QLVQ1LOKCQX2193VSEICXW61NP6B1O`

#### Step 3: Find Your Site ID

Your Site ID can be found in multiple ways:

**Method 1 - From URL**:
- When logged into the SolarEdge portal, check the URL bar
- The URL will look like: `https://monitoring.solaredge.com/solaredge-web/p/site/123456`
- The number at the end is your Site ID

**Method 2 - From Site Details**:
- Go to **Admin** → **Site Details**
- The Site ID is displayed at the top of the page

**Example Site ID**: `123456` (numeric value)

#### Step 4: Add Credentials to .env File

Create or edit the `.env` file in the project root:

```bash
# SolarEdge API Configuration
SOLAREDGE_API_KEY=L4QLVQ1LOKCQX2193VSEICXW61NP6B1O
SOLAREDGE_SITE_ID=123456
```

#### Step 5: Test the Integration

Run the example script to verify your credentials work:

```bash
python examples/solar_edge_example.py
```

Expected output:
```
SolarEdge Site: My House
Current Power: 2847.0 W
Status: Active
Last Update: 2025-10-29 14:30:00
```

#### Step 6: Start the Dashboard

```bash
python run_nicegui.py
```

The solar production section will now appear on the dashboard with live data!

### Understanding SolarEdge API Limits

**Rate Limit**: 300 API calls per day per API key

**Dashboard Behavior**:
- Solar data updates every **60 seconds** (1 call per minute)
- This equals 1,440 calls per day
- To stay within limits, the dashboard makes calls only when needed
- Power consumption and spot price updates are independent (no API calls)

**Best Practices**:
- Don't run multiple instances with the same API key
- Avoid running test scripts continuously
- Monitor your API usage in the SolarEdge portal

### SolarEdge API Troubleshooting

#### Problem: "SolarEdge not configured"

**Solution**:
- This is normal if you haven't added credentials to `.env`
- The solar section will be hidden, and the app works fine without it
- Add credentials following the steps above to enable solar monitoring

#### Problem: "Solar error: API authentication failed"

**Solutions**:
- Verify API key is correct (check for typos, extra spaces)
- Ensure Site ID is a number (no quotes needed in .env)
- Regenerate API key if expired or compromised
- Check that your SolarEdge account has API access enabled

#### Problem: "No solar data available"

**Solutions**:
- Verify your solar system is online in the SolarEdge portal
- Check that inverter is communicating (may take 15-20 minutes after sunset/sunrise)
- Ensure Site ID matches your installation
- Try running the example script to test API access directly

#### Problem: Solar power shows 0W during daytime

**Solutions**:
- Check inverter status in SolarEdge portal
- Inverter may be in standby mode (normal in very low light)
- Verify panels are not shaded or covered
- Check for system alerts in SolarEdge portal
- Wait 5-10 minutes - data may be delayed

### Optional: Disable SolarEdge

If you don't have solar panels or don't want solar monitoring:

**Simply don't add the SolarEdge variables to your `.env` file.**

The dashboard will automatically:
- Hide the solar production section
- Continue working normally with spot prices and power consumption
- Show no errors related to solar monitoring

### SolarEdge Data Privacy

**What data is accessed**:
- Only your solar site's production data
- No personal information
- No account credentials (only API key)

**Data security**:
- API key stored locally in `.env` file
- Never transmitted except to SolarEdge servers
- Keep your `.env` file private (already in `.gitignore`)

### Advanced: Multiple Sites

If you have multiple SolarEdge installations:

**Option 1**: Create separate `.env` files and run multiple instances:
```bash
# Site 1
SOLAREDGE_API_KEY=key1
SOLAREDGE_SITE_ID=123456

# Site 2  
SOLAREDGE_API_KEY=key2
SOLAREDGE_SITE_ID=789012
```

**Option 2**: Modify `solar_edge.py` to support multiple sites (requires code changes)

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
