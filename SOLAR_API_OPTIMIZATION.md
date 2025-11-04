# SolarEdge API Call Optimization

## Overview
This document describes the optimizations implemented to minimize SolarEdge API calls while maintaining useful data updates.

## Optimization Strategies

### 1. Sun Position Awareness
**Implementation**: Only fetch solar data when the sun is up.

- Uses the `astral` library to calculate sunrise and sunset times for Stockholm (SE4 region)
- API calls are completely stopped during nighttime hours
- Fallback to 6 AM - 8 PM if sun calculation fails
- **Benefit**: Saves ~50% of potential API calls (no calls during nighttime)

### 2. Client Connection Tracking
**Implementation**: Only fetch solar data when clients are viewing the dashboard.

- Tracks the number of connected web clients using NiceGUI's connection events
- Solar updates pause when no clients are connected
- Resumes automatically when a client connects
- **Benefit**: Saves API calls when nobody is actively monitoring the dashboard

### 3. Adaptive Update Interval
**Implementation**: Dynamically calculates optimal update interval based on:
- Available API quota (default: 300 calls/day)
- Target usage (default: 90% of available calls)
- Actual daylight duration for the current date

**Calculation**:
```
allowed_calls = max_daily_calls * 0.90  # Use 90% of quota
daylight_hours = sunset - sunrise
interval_minutes = (daylight_hours / allowed_calls)
interval_minutes = max(5, interval_minutes)  # Minimum 5 minutes safety
```

**Example** (Stockholm in summer):
- Daylight: ~18 hours (1080 minutes)
- Allowed calls: 270 (90% of 300)
- Interval: ~4 minutes → Adjusted to 5 minutes (safety minimum)
- Total calls: ~216 per day

**Example** (Stockholm in winter):
- Daylight: ~6 hours (360 minutes)
- Allowed calls: 270 (90% of 300)
- Interval: ~1.3 minutes → Adjusted to 5 minutes (safety minimum)
- Total calls: ~72 per day

### 4. Daily Recalibration
**Implementation**: Update interval is recalculated daily at midnight.

- Adapts to seasonal changes in daylight duration
- Ensures optimal API usage throughout the year
- **Benefit**: Automatic adjustment without manual intervention

## Configuration

### Default Settings
```python
max_daily_calls = 300      # SolarEdge API limit
usage_percent = 0.9        # Use 90% of available quota
min_interval_minutes = 5   # Safety minimum
```

### Customization
To adjust the API usage, modify the call to `calculate_solar_update_interval()` in `nicegui_app.py`:

```python
# Use 80% of quota instead of 90%
self.solar_update_interval = calculate_solar_update_interval(
    max_daily_calls=300, 
    usage_percent=0.8
)

# If you have a higher API limit
self.solar_update_interval = calculate_solar_update_interval(
    max_daily_calls=500, 
    usage_percent=0.9
)
```

## Expected API Usage

### Summer (Long Days)
- Daylight: ~18 hours
- Update interval: ~5 minutes
- API calls per day: ~216
- Quota usage: ~72%

### Winter (Short Days)
- Daylight: ~6 hours
- Update interval: ~5 minutes (minimum)
- API calls per day: ~72
- Quota usage: ~24%

### With No Connected Clients
- API calls per day: **0**
- The system will fetch fresh data immediately when a client connects

## Benefits Summary

1. **Reduced API Costs**: Stay well within API limits
2. **Efficient Resource Usage**: No calls when not needed (night, no clients)
3. **Adaptive**: Automatically adjusts to seasonal daylight changes
4. **Safe**: 90% quota usage leaves 10% buffer for manual checks or errors
5. **Responsive**: Immediate update on first client connection during daytime

## Monitoring

The application logs provide information about:
- Calculated update intervals
- Client connections/disconnections
- Solar API call attempts
- Sun up/down status checks

Example log output:
```
Solar update interval calculated: 5.0 minutes (270 calls over 18.0 hours of daylight)
Client connected. Total clients: 1
Solar power updated: 680.0W
Client disconnected. Total clients: 0
```

## Dependencies

- `astral>=3.2`: Sun position calculations
- Existing dependencies remain unchanged

Install with:
```bash
pip install -r requirements.txt
```
