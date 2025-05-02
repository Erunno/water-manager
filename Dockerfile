FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY backend /app/backend
COPY frontend /app/frontend

# Create directory for the database file
RUN mkdir -p /data

# Environment variable for the database file
ENV CSV_FILE=/data/water-jugs.csv

# Expose both HTTP and HTTPS ports
EXPOSE 80 5000

# Install curl for healthcheck and debugging
RUN apt-get update && \
    apt-get install -y openssl curl && \
    apt-get clean && \
    openssl req -x509 -newkey rsa:4096 -nodes -out /app/server.cert -keyout /app/server.key -days 365 -subj "/CN=localhost"

# Make sure we're binding to all interfaces
ENV FLASK_RUN_HOST=0.0.0.0

# Add a health check to verify the application is running correctly
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f https://localhost:5000/ --insecure || exit 1

# Command to run the app - using an absolute path and printing more debugging info
CMD ["sh", "-c", "python -u /app/backend/app.py /data/water-jugs.csv"]
