#!/usr/bin/env python3
"""
List the last 50 records from InfluxDB

This utility queries the InfluxDB database and displays the most recent
50 records from the power_monitoring measurement, showing timestamp and
all data fields (grid_power, spot_price, solar_production).

Usage:
    python src/util/listinflux.py
    
    # Or with custom record count:
    python src/util/listinflux.py --count 100
    
Environment variables required:
    INFLUXDB2_HOST - InfluxDB host (default: localhost)
    INFLUXDB2_PORT - InfluxDB port (default: 8086)
    INFLUXDB2_USER - Username for authentication
    INFLUXDB2_PASSWORD - Password for authentication
    INFLUXDB2_TOKEN - API token (optional, uses user/pass if not set)
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def list_influx_records(count: int = 50) -> None:
    """
    Query and display the last N records from InfluxDB
    
    Args:
        count: Number of records to retrieve (default: 50)
    """
    try:
        from influxdb_client import InfluxDBClient
    except ImportError:
        print("Error: influxdb-client not installed")
        print("Install it with: pip install influxdb-client")
        sys.exit(1)
    
    # Get configuration from environment
    host = os.getenv('INFLUXDB2_HOST', 'localhost')
    port = os.getenv('INFLUXDB2_PORT', '8086')
    user = os.getenv('INFLUXDB2_USER')
    password = os.getenv('INFLUXDB2_PASSWORD')
    token = os.getenv('INFLUXDB2_TOKEN')
    org = os.getenv('INFLUXDB2_ORG', 'sotehus')
    bucket = os.getenv('INFLUXDB2_BUCKET', 'sotehus_bucket')
    
    # Validate required configuration
    if not host:
        print("Error: INFLUXDB2_HOST not set in environment")
        sys.exit(1)
    
    if not token and not (user and password):
        print("Error: Either INFLUXDB2_TOKEN or both INFLUXDB2_USER and INFLUXDB2_PASSWORD must be set")
        sys.exit(1)
    
    # Build connection URL
    url = f"http://{host}:{port}"
    
    print(f"Connecting to InfluxDB at {url}...")
    print(f"Organization: {org}")
    print(f"Bucket: {bucket}")
    print(f"Retrieving last {count} records...\n")
    
    # Create client
    try:
        if token:
            client = InfluxDBClient(url=url, token=token, org=org)
        else:
            client = InfluxDBClient(
                url=url,
                username=user,
                password=password,
                org=org
            )
        
        # Test connection
        health = client.health()
        if health.status != "pass":
            print(f"Error: InfluxDB health check failed: {health.message}")
            sys.exit(1)
        
        print("✓ Connected to InfluxDB successfully\n")
        
    except Exception as e:
        print(f"Error connecting to InfluxDB: {e}")
        sys.exit(1)
    
    # Query last N records
    query_api = client.query_api()
    
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -30d)
        |> filter(fn: (r) => r._measurement == "power_monitoring")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["_time"], desc: true)
        |> limit(n: {count})
    '''
    
    try:
        tables = query_api.query(query, org=org)
        
        if not tables:
            print("No records found in the database.")
            print("\nTip: Make sure data is being written to InfluxDB.")
            client.close()
            return
        
        # Count total records
        record_count = 0
        for table in tables:
            record_count += len(table.records)
        
        if record_count == 0:
            print("No records found in the database.")
            print("\nTip: Make sure data is being written to InfluxDB.")
            client.close()
            return
        
        print(f"{'Timestamp':<28} {'Grid Power (W)':<15} {'Spot Price (SEK/kWh)':<23} {'Solar Production (W)':<20}")
        print("=" * 110)
        
        # Display records (already sorted by time descending)
        for table in tables:
            for record in table.records:
                timestamp = record.values.get('_time')
                grid_power = record.values.get('grid_power')
                spot_price = record.values.get('spot_price')
                solar_production = record.values.get('solar_production')
                
                # Format timestamp
                if timestamp:
                    if isinstance(timestamp, datetime):
                        ts_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        ts_str = str(timestamp)
                else:
                    ts_str = "N/A"
                
                # Format values with proper handling of None
                grid_str = f"{grid_power:>12.1f}" if grid_power is not None else "         N/A"
                spot_str = f"{spot_price:>20.4f}" if spot_price is not None else "                  N/A"
                solar_str = f"{solar_production:>17.1f}" if solar_production is not None else "                 N/A"
                
                print(f"{ts_str:<28} {grid_str:<15} {spot_str:<23} {solar_str:<20}")
        
        print("=" * 110)
        print(f"\nTotal records displayed: {record_count}")
        
        # Show summary statistics
        print("\n--- Summary Statistics ---")
        all_grid_power = []
        all_spot_price = []
        all_solar_production = []
        
        for table in tables:
            for record in table.records:
                if record.values.get('grid_power') is not None:
                    all_grid_power.append(record.values['grid_power'])
                if record.values.get('spot_price') is not None:
                    all_spot_price.append(record.values['spot_price'])
                if record.values.get('solar_production') is not None:
                    all_solar_production.append(record.values['solar_production'])
        
        if all_grid_power:
            print(f"Grid Power:        avg={sum(all_grid_power)/len(all_grid_power):>8.1f} W, "
                  f"min={min(all_grid_power):>8.1f} W, max={max(all_grid_power):>8.1f} W")
        
        if all_spot_price:
            print(f"Spot Price:        avg={sum(all_spot_price)/len(all_spot_price):>8.4f} SEK/kWh, "
                  f"min={min(all_spot_price):>8.4f} SEK/kWh, max={max(all_spot_price):>8.4f} SEK/kWh")
        
        if all_solar_production:
            print(f"Solar Production:  avg={sum(all_solar_production)/len(all_solar_production):>8.1f} W, "
                  f"min={min(all_solar_production):>8.1f} W, max={max(all_solar_production):>8.1f} W")
        
    except Exception as e:
        print(f"Error querying InfluxDB: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        client.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='List the last N records from InfluxDB power_monitoring measurement',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # List last 50 records (default)
  python src/util/listinflux.py
  
  # List last 100 records
  python src/util/listinflux.py --count 100
  
  # List last 10 records
  python src/util/listinflux.py -c 10

Environment variables:
  INFLUXDB2_HOST        InfluxDB host (default: localhost)
  INFLUXDB2_PORT        InfluxDB port (default: 8086)
  INFLUXDB2_USER        Username for authentication
  INFLUXDB2_PASSWORD    Password for authentication
  INFLUXDB2_TOKEN       API token (alternative to user/password)
  INFLUXDB2_ORG         Organization name (default: sotehus)
  INFLUXDB2_BUCKET      Bucket name (default: sotehus_bucket)
        '''
    )
    
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=50,
        help='Number of records to retrieve (default: 50)'
    )
    
    args = parser.parse_args()
    
    if args.count < 1:
        print("Error: count must be a positive number")
        sys.exit(1)
    
    list_influx_records(args.count)


if __name__ == '__main__':
    main()
