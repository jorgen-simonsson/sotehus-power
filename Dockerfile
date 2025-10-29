# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    TZ=Europe/Stockholm

# Install system dependencies (including tzdata for timezone support)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port NiceGUI runs on
EXPOSE 8080

# Run the application
CMD ["python", "run_nicegui.py"]
