#!/usr/bin/env python3
"""
Swedish Electricity Spot Price & Power Monitoring Dashboard
NiceGUI Version

Real-time web dashboard for monitoring Swedish electricity spot prices 
and household power consumption.
"""

from nicegui import ui
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import asyncio
import threading
from src.backend.spotprice import SpotPriceClient
from src.backend.mqtt_client import MQTTPowerClient
from src.backend.solar_edge import SolarEdgeClient


# Global variable to store MQTT client instance
_mqtt_client_instance: Optional[MQTTPowerClient] = None

# Global variable to store latest power data (shared across all clients)
_latest_power_data: Optional[Dict[str, Any]] = None
_power_data_lock = threading.Lock()


def get_current_time() -> datetime:
    """Get current time with proper timezone handling (local time)"""
    return datetime.now().astimezone()


def format_timestamp(dt: datetime) -> str:
    """Format datetime to string with timezone awareness"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class SpotPriceDashboard:
    """Main dashboard class for managing spot price and power monitoring"""
    
    def __init__(self):
        # Spot price state
        self.current_price: Optional[float] = None
        self.loading: bool = False
        self.error_message: str = ""
        self.last_updated: str = ""
        self.region: str = "SE4"  # Always use SE4
        
        # MQTT Power consumption state
        self.current_power: Optional[float] = None
        self.mqtt_connected: bool = False
        self.mqtt_error: str = ""
        self.power_last_updated: str = ""
        
        # Solar power state
        self.current_solar_power: Optional[float] = None
        self.solar_error: str = ""
        self.solar_last_updated: str = ""
        self.solar_available: bool = False
        
        # UI elements (will be set when building UI)
        self.price_label: Optional[ui.label] = None
        self.price_info_label: Optional[ui.label] = None
        self.price_error_label: Optional[ui.label] = None
        self.price_updated_label: Optional[ui.label] = None
        self.price_spinner: Optional[ui.spinner] = None
        
        self.power_label: Optional[ui.label] = None
        self.power_status_label: Optional[ui.label] = None
        self.power_error_label: Optional[ui.label] = None
        self.power_updated_label: Optional[ui.label] = None
        self.power_connecting_container: Optional[ui.element] = None
        self.power_data_container: Optional[ui.element] = None
        
        self.solar_label: Optional[ui.label] = None
        self.solar_status_label: Optional[ui.label] = None
        self.solar_error_label: Optional[ui.label] = None
        self.solar_updated_label: Optional[ui.label] = None
        self.solar_data_container: Optional[ui.element] = None
        
        # Initialize
        self.setup_mqtt()
        self.fetch_spot_price()
        self.check_solar_availability()
    
    @classmethod
    def get_mqtt_client(cls) -> Optional[MQTTPowerClient]:
        """Get or create the MQTT client instance."""
        global _mqtt_client_instance
        
        if _mqtt_client_instance is None:
            try:
                _mqtt_client_instance = MQTTPowerClient()
                # Set the callback to update global data
                def callback(power: float):
                    cls.power_update_callback_static(power)
                _mqtt_client_instance.set_power_callback(callback)
            except Exception as e:
                print(f"MQTT config error: {str(e)}")
                return None
        
        return _mqtt_client_instance
    
    @classmethod
    def power_update_callback_static(cls, power: float) -> None:
        """Static callback for MQTT power updates."""
        global _latest_power_data, _power_data_lock
        
        # Update the global shared power data
        with _power_data_lock:
            _latest_power_data = {
                'power': round(power, 2),
                'timestamp': get_current_time()
            }
        print(f"MQTT received: {power}W, updated global data")
    
    def setup_mqtt(self):
        """Initialize MQTT connection"""
        try:
            client = self.get_mqtt_client()
            if client and client.connect():
                self.mqtt_connected = True
                self.mqtt_error = ""
                print("MQTT connected successfully")
            else:
                self.mqtt_connected = False
                self.mqtt_error = "Failed to connect to MQTT broker"
                print(f"MQTT connection failed: {self.mqtt_error}")
        except Exception as e:
            self.mqtt_connected = False
            self.mqtt_error = f"MQTT connection error: {str(e)}"
            print(f"MQTT exception: {e}")
    
    def check_solar_availability(self):
        """Check if SolarEdge configuration is available"""
        try:
            client = SolarEdgeClient()
            self.solar_available = True
            self.solar_error = ""
            print("SolarEdge configuration found")
            # Try to fetch initial data
            self.fetch_solar_power()
        except ValueError as e:
            self.solar_available = False
            self.solar_error = "SolarEdge not configured"
            print(f"SolarEdge not available: {e}")
        except Exception as e:
            self.solar_available = False
            self.solar_error = f"SolarEdge error: {str(e)}"
            print(f"SolarEdge exception: {e}")
    
    def fetch_solar_power(self):
        """Fetch the current solar power production"""
        if not self.solar_available:
            return
        
        try:
            client = SolarEdgeClient()
            power = client.get_current_power_production()
            if power is not None:
                self.current_solar_power = round(power, 2)
                self.solar_last_updated = format_timestamp(get_current_time())
                self.solar_error = ""
                print(f"Solar power updated: {power}W")
            else:
                self.solar_error = "No solar data available"
        except Exception as e:
            self.solar_error = f"Solar error: {str(e)}"
            print(f"Solar fetch error: {e}")
        
        self.update_solar_ui()
    
    def fetch_spot_price(self):
        """Fetch the current spot price"""
        self.loading = True
        self.error_message = ""
        self.update_price_ui()
        
        try:
            client = SpotPriceClient()
            price = client.get_current_price(self.region)
            if price is not None:
                self.current_price = round(price, 2)
                self.last_updated = format_timestamp(get_current_time())
                self.error_message = ""
            else:
                self.error_message = "Could not fetch current spot price"
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
        finally:
            self.loading = False
            self.update_price_ui()
    
    def check_and_refresh_spot_price(self):
        """Check if we've crossed a 15-minute boundary and refresh spot price if needed"""
        now = get_current_time()
        current_minute = now.minute
        
        # Check if we're at a 15-minute boundary (0, 15, 30, 45)
        if current_minute % 15 == 0:
            # Only refresh if we haven't updated in the last minute
            if self.last_updated:
                last_update_time = datetime.strptime(self.last_updated, "%Y-%m-%d %H:%M:%S").astimezone()
                time_since_update = (now - last_update_time).total_seconds()
                
                # Refresh if it's been more than 60 seconds
                if time_since_update > 60:
                    print(f"15-minute boundary detected, refreshing spot price")
                    self.fetch_spot_price()
            else:
                # No previous update, fetch now
                self.fetch_spot_price()
    
    def set_region(self, new_region: str):
        """Set the region and fetch new price"""
        self.region = new_region
        self.fetch_spot_price()
    
    def update_price_ui(self):
        """Update the spot price UI elements"""
        if self.price_spinner:
            self.price_spinner.visible = self.loading
        
        if self.price_label:
            if self.current_price is not None:
                self.price_label.text = f"{self.current_price:.2f} SEK/kWh"
                self.price_label.visible = True
            else:
                self.price_label.visible = False
        
        if self.price_info_label:
            # Hide the info label to save space on mobile
            self.price_info_label.visible = False
        
        if self.price_error_label:
            self.price_error_label.text = self.error_message
            self.price_error_label.visible = bool(self.error_message)
        
        if self.price_updated_label:
            self.price_updated_label.text = f"Last updated: {self.last_updated}" if self.last_updated else ""
            self.price_updated_label.visible = bool(self.last_updated)
    
    def update_power_ui(self):
        """Update the power consumption UI elements"""
        global _latest_power_data, _power_data_lock
        
        # Read latest data from global variable
        with _power_data_lock:
            latest_data = _latest_power_data
        
        if latest_data:
            self.current_power = latest_data['power']
            self.power_last_updated = format_timestamp(latest_data['timestamp'])
            self.mqtt_error = ""
        
        # Update UI elements
        if self.power_connecting_container:
            self.power_connecting_container.visible = not self.mqtt_connected
        
        if self.power_data_container:
            self.power_data_container.visible = self.mqtt_connected
        
        if self.power_label and self.current_power is not None:
            self.power_label.text = f"{self.current_power:.0f} W"
        
        if self.power_status_label:
            self.power_status_label.visible = self.mqtt_connected
        
        if self.power_error_label:
            self.power_error_label.text = f"⚠️ {self.mqtt_error}" if self.mqtt_error else ""
            self.power_error_label.visible = bool(self.mqtt_error)
        
        if self.power_updated_label:
            self.power_updated_label.text = f"Last updated: {self.power_last_updated}" if self.power_last_updated else ""
            self.power_updated_label.visible = bool(self.power_last_updated)
    
    def update_solar_ui(self):
        """Update the solar power UI elements"""
        if not self.solar_available:
            if self.solar_data_container:
                self.solar_data_container.visible = False
            return
        
        if self.solar_data_container:
            self.solar_data_container.visible = True
        
        if self.solar_label and self.current_solar_power is not None:
            # Display in W if less than 1000W, otherwise in kW
            if self.current_solar_power < 1000:
                self.solar_label.text = f"{self.current_solar_power:.1f} W"
                print(f"DEBUG: Updated solar UI label to {self.current_solar_power:.1f} W")
            else:
                power_kw = self.current_solar_power / 1000
                self.solar_label.text = f"{power_kw:.2f} kW"
                print(f"DEBUG: Updated solar UI label to {power_kw:.2f} kW")
        elif self.solar_label is None:
            print("DEBUG: solar_label is None")
        elif self.current_solar_power is None:
            print(f"DEBUG: current_solar_power is None")
        
        if self.solar_status_label:
            if self.current_solar_power is not None:
                if self.current_solar_power > 0:
                    self.solar_status_label.text = "☀️ Producing power"
                else:
                    self.solar_status_label.text = "🌙 No production"
            else:
                self.solar_status_label.text = "❓ Status unknown"
        
        if self.solar_error_label:
            self.solar_error_label.text = f"⚠️ {self.solar_error}" if self.solar_error else ""
            self.solar_error_label.visible = bool(self.solar_error)
        
        if self.solar_updated_label:
            self.solar_updated_label.text = f"Last updated: {self.solar_last_updated}" if self.solar_last_updated else ""
            self.solar_updated_label.visible = bool(self.solar_last_updated)
    
    def start_background_updates(self):
        """Start background updates using UI timers"""
        # Timer for power consumption updates every 3 seconds
        ui.timer(3.0, self.update_power_ui)
        
        # Timer for spot price UI updates every 3 seconds (updates timestamp)
        ui.timer(3.0, self.update_price_ui)
        
        # Timer for solar power updates every 60 seconds
        if self.solar_available:
            ui.timer(60.0, self.fetch_solar_power)
            # Timer to update solar UI every 3 seconds (to keep UI responsive)
            ui.timer(3.0, self.update_solar_ui)
        
        # Timer to check for 15-minute boundary and refresh spot price
        ui.timer(30.0, self.check_and_refresh_spot_price)

    async def background_update_loop(self):
        """Background task to update power data every 3 seconds and solar data every minute"""
        # This method is kept for compatibility but timers are used instead
        pass
    
    def build_ui(self):
        """Build the user interface"""
        with ui.column().classes('w-full items-center p-8 gap-4'):
            # Header
            ui.label('Sotehus').classes('text-6xl font-bold')
            
            # Spot Price Section
            with ui.card().classes('w-full max-w-lg p-6'):
                with ui.column().classes('items-center gap-4'):
                    self.price_spinner = ui.spinner(size='lg')
                    self.price_spinner.visible = self.loading
                    
                    with ui.column().classes('items-center gap-1'):
                        self.price_label = ui.label().classes('text-4xl font-bold')
                        self.price_info_label = ui.label().classes('text-base')
                    
                    self.price_error_label = ui.label().classes('text-red-600')
                    self.price_updated_label = ui.label().classes('text-sm text-gray-600')
            
            # Power Consumption Section
            with ui.card().classes('w-full max-w-lg p-6 mt-4'):
                with ui.column().classes('items-center gap-3'):
                    ui.label('🏠 Grid Power Consumption').classes('text-2xl font-semibold mb-4')
                    
                    # Connecting state
                    with ui.column().classes('items-center gap-2') as self.power_connecting_container:
                        ui.label('Connecting to power monitoring...')
                        ui.spinner(size='md')
                    
                    # Connected state
                    with ui.column().classes('items-center gap-1') as self.power_data_container:
                        self.power_label = ui.label().classes('text-3xl font-bold text-orange-600')
                    
                    # Status labels
                    self.power_status_label = ui.label('🟢 MQTT Connected').classes('text-sm text-green-600')
                    self.power_error_label = ui.label().classes('text-sm text-red-600')
                    self.power_updated_label = ui.label().classes('text-sm text-gray-600')
            
            # Solar Power Section
            with ui.card().classes('w-full max-w-lg p-6 mt-4'):
                with ui.column().classes('items-center gap-3'):
                    ui.label('☀️ Solar Power Production').classes('text-2xl font-semibold mb-4')
                    
                    # Solar data display
                    with ui.column().classes('items-center gap-1') as self.solar_data_container:
                        self.solar_label = ui.label().classes('text-3xl font-bold text-yellow-600')
                    
                    # Status labels
                    self.solar_status_label = ui.label().classes('text-sm text-gray-600')
                    self.solar_error_label = ui.label().classes('text-sm text-red-600')
                    self.solar_updated_label = ui.label().classes('text-sm text-gray-600')
        
        # Initial UI update
        self.update_price_ui()
        self.update_power_ui()
        self.update_solar_ui()
        
        # Start background updates using timers
        self.start_background_updates()


# Create the dashboard instance
dashboard = SpotPriceDashboard()

@ui.page('/')
def index():
    """Main page"""
    dashboard.build_ui()

if __name__ in {"__main__", "__mp_main__"}:
    # Run the NiceGUI app
    ui.run(
        title='Sotehus',
        reload=False,
        host='0.0.0.0',
        port=8080
    )
