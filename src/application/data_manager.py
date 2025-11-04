"""
Data Manager - Centralized state management for the application

This module provides a singleton DataManager class that consolidates all global state
and provides thread-safe access to shared data across the application.
"""

import threading
from typing import Optional, Dict, Any
from datetime import datetime
from src.backend.mqtt_client import MQTTPowerClient


class DataManager:
    """
    Singleton class to manage shared application state.
    
    Consolidates:
    - MQTT client instance
    - Latest power data from MQTT
    - Connected clients counter
    
    Provides thread-safe access to all shared data.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if self._initialized:
            return
            
        # MQTT client management
        self._mqtt_client: Optional[MQTTPowerClient] = None
        self._mqtt_lock = threading.Lock()
        
        # Power data management
        self._latest_power_data: Optional[Dict[str, Any]] = None
        self._power_data_lock = threading.Lock()
        
        # Client connection tracking
        self._connected_clients: int = 0
        self._clients_lock = threading.Lock()
        
        self._initialized = True
    
    # MQTT Client Management
    
    def get_mqtt_client(self) -> Optional[MQTTPowerClient]:
        """Get the singleton MQTT client instance."""
        with self._mqtt_lock:
            return self._mqtt_client
    
    def set_mqtt_client(self, client: MQTTPowerClient) -> None:
        """Set the MQTT client instance."""
        with self._mqtt_lock:
            self._mqtt_client = client
    
    def create_mqtt_client(self) -> Optional[MQTTPowerClient]:
        """Create and store the MQTT client instance if it doesn't exist."""
        with self._mqtt_lock:
            if self._mqtt_client is None:
                try:
                    self._mqtt_client = MQTTPowerClient()
                    return self._mqtt_client
                except Exception as e:
                    print(f"MQTT client creation error: {str(e)}")
                    return None
            return self._mqtt_client
    
    # Power Data Management
    
    def get_latest_power_data(self) -> Optional[Dict[str, Any]]:
        """Get the latest power data from MQTT."""
        with self._power_data_lock:
            return self._latest_power_data.copy() if self._latest_power_data else None
    
    def update_power_data(self, power: float, timestamp: datetime) -> None:
        """Update the latest power data."""
        with self._power_data_lock:
            self._latest_power_data = {
                'power': round(power, 2),
                'timestamp': timestamp
            }
        print(f"MQTT received: {power}W, updated global data")
    
    # Client Connection Management
    
    def increment_clients(self) -> int:
        """Increment the connected clients counter and return new count."""
        with self._clients_lock:
            self._connected_clients += 1
            count = self._connected_clients
        print(f"Client connected. Total clients: {count}")
        return count
    
    def decrement_clients(self) -> int:
        """Decrement the connected clients counter and return new count."""
        with self._clients_lock:
            self._connected_clients = max(0, self._connected_clients - 1)
            count = self._connected_clients
        print(f"Client disconnected. Total clients: {count}")
        return count
    
    def get_client_count(self) -> int:
        """Get the current number of connected clients."""
        with self._clients_lock:
            return self._connected_clients
    
    def has_connected_clients(self) -> bool:
        """Check if there are any connected clients."""
        with self._clients_lock:
            return self._connected_clients > 0
