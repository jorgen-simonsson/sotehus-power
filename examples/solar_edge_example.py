#!/usr/bin/env python3
"""
Simple example usage of the SolarEdge API client

This example demonstrates how to get current solar power production
for integration into a power monitoring dashboard.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.solar_edge import SolarEdgeClient


def display_solar_power():
    """
    Simple function showing how to retrieve current solar power production
    """
    try:
        # Initialize the client (reads from .env file)
        client = SolarEdgeClient()
        
        print("=" * 50)
        print("🌞 SOLAR POWER MONITORING")
        print("=" * 50)
        
        # Get current power production
        current_power = client.get_current_power_production()
        if current_power is not None:
            print(f"⚡ Current Production: {current_power:,.0f} W ({current_power/1000:.2f} kW)")
            
            if current_power > 0:
                print("☀️  Solar panels are producing power")
            else:
                print("� Solar panels are not producing power (nighttime or low light)")
        else:
            print("❌ Could not retrieve current power production")
        
        print("\n" + "=" * 50)
        print(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease ensure you have set the following in your .env file:")
        print("SOLAREDGE_API_KEY=your_actual_api_key")
        print("SOLAREDGE_SITE_ID=your_actual_site_id")
        print("\nTo get these values:")
        print("1. Log into your SolarEdge monitoring portal")
        print("2. Go to Admin → API Access")
        print("3. Generate an API key")
        print("4. Find your Site ID in the site details")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


def get_simple_power_reading():
    """
    Simple example for getting just the current power production
    """
    try:
        client = SolarEdgeClient()
        current_power = client.get_current_power_production()
        
        if current_power is not None:
            print(f"Current solar power production: {current_power:.2f} W")
            return current_power
        else:
            print("No power data available")
            return 0
            
    except Exception as e:
        print(f"Error getting solar power: {e}")
        return 0


if __name__ == "__main__":
    # Display simple power monitoring
    display_solar_power()
    
    print("\n" + "=" * 50)
    print("Simple power reading example:")
    get_simple_power_reading()