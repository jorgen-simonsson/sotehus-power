#!/usr/bin/env python3
"""
Swedish Electricity Spot Price & Power Monitoring Dashboard
NiceGUI Version

Real-time web dashboard for monitoring Swedish electricity spot prices 
and household power consumption.
"""

from nicegui import ui
from datetime import datetime
from typing import Optional, Dict, Any
import asyncio
import threading
from src.backend.spotprice import SpotPriceClient
from src.backend.mqtt_client import MQTTPowerClient


# Global variable to store MQTT client instance
_mqtt_client_instance: Optional[MQTTPowerClient] = None

# Global variable to store latest power data (shared across all clients)
_latest_power_data: Optional[Dict[str, Any]] = None
_power_data_lock = threading.Lock()


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
        
        # Initialize
        self.setup_mqtt()
        self.fetch_spot_price()
        
        # Start background update task
        self.update_task = None
    
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
                'timestamp': datetime.now()
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
                self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.error_message = ""
            else:
                self.error_message = "Could not fetch current spot price"
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
        finally:
            self.loading = False
            self.update_price_ui()
    
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
            if self.current_price is not None:
                self.price_info_label.text = f"Current spot price for {self.region}"
                self.price_info_label.visible = True
            else:
                self.price_info_label.text = "Click 'Refresh Price' to get current spot price"
                self.price_info_label.visible = not self.loading
        
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
            self.power_last_updated = latest_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
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
    
    async def background_update_loop(self):
        """Background task to update power data every 3 seconds"""
        while True:
            await asyncio.sleep(3)
            self.update_power_ui()
    
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
                    ui.label('🏠 Current Power Consumption').classes('text-2xl font-semibold mb-4')
                    
                    # Connecting state
                    with ui.column().classes('items-center gap-2') as self.power_connecting_container:
                        ui.label('Connecting to power monitoring...')
                        ui.spinner(size='md')
                    
                    # Connected state
                    with ui.column().classes('items-center gap-1') as self.power_data_container:
                        self.power_label = ui.label().classes('text-3xl font-bold text-orange-600')
                        ui.label('Current power consumption')
                    
                    # Status labels
                    self.power_status_label = ui.label('🟢 MQTT Connected').classes('text-sm text-green-600')
                    self.power_error_label = ui.label().classes('text-sm text-red-600')
                    self.power_updated_label = ui.label().classes('text-sm text-gray-600')
        
        # Initial UI update
        self.update_price_ui()
        self.update_power_ui()
        
        # Start background update task
        if self.update_task is None:
            self.update_task = asyncio.create_task(self.background_update_loop())


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
