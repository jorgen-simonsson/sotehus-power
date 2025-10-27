# Quick Start Guide

## Installation

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Configure MQTT (optional)
cp .env.example .env
# Edit .env with your MQTT broker settings
```

## Running the Application

```bash
# From project root:
python run_nicegui.py
```

Open: http://localhost:8080

## Features

- ⚡ Real-time Swedish electricity spot prices (SE1-SE4)
- 🏠 Live power consumption monitoring via MQTT
- 🔄 Auto-updates every 3 seconds
- 🌍 Works with Home Assistant, Zigbee2MQTT, and more

## Troubleshooting

**Import errors?**
- Make sure you're running from project root using `python run_nicegui.py`
- Check virtual environment is activated

**MQTT not connecting?**
- Verify broker settings in `.env`
- Check broker is running: `mosquitto -v`
- Test with: `mosquitto_sub -h localhost -t '#' -v`

**Port conflict?**
- NiceGUI uses port 8080 by default
- Change port in `spot_nicegui/nicegui_app.py`: `ui.run(port=8081)`
- Kill existing process: `lsof -ti:8080 | xargs kill -9`

## Project Structure

```
spot/
├── src/
│   ├── backend/          # Backend modules (API & MQTT)
│   └── frontend/         # Frontend web application
└── run_nicegui.py        # Launcher script
```

For detailed documentation, see [README.md](README.md)
