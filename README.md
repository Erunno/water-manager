# Water Jug Manager

A simple web application to track the filling and emptying of water jugs using QR codes.

## Features

- QR code scanning to identify water jugs
- Track when jugs are filled and emptied
- View a list of currently filled jugs
- Czech language interface
- Support for special characters in jug names

## Docker Setup

The application can be easily run using Docker.

### Requirements

- Docker
- Docker Compose (optional, but recommended)

### Quick Start

1. Clone the repository:
   ```
   git clone [repository-url]
   cd water-manager
   ```

2. Build and run with Docker Compose:
   ```
   docker-compose up -d
   ```

3. Access the application:
   ```
   https://localhost:5000
   ```

### Port Configuration

The application supports both HTTP and HTTPS access:

- **Port 80**: HTTP access
- **Port 5000**: HTTPS access with self-signed certificate

You can choose which port to expose or map to a different external port:

```yaml
# Map HTTP to port 8080 and HTTPS to port 8443
ports:
  - "8080:80"    # HTTP
  - "8443:5000"  # HTTPS
```

For QR code scanning on mobile devices, HTTPS is recommended.

### Using HTTP Only

If you prefer to use only HTTP:

### Manual Docker Build

If you prefer not to use Docker Compose:

1. Build the Docker image:
   ```
   docker build -t water-manager .
   ```

2. Run the container:
   ```
   docker run -d -p 5000:5000 -v $(pwd)/data:/data water-manager
   ```

## Database Configuration

The application uses a simple CSV file as its database. By default, this file is stored at `/data/water-jugs.csv` inside the container.

### Using Your Own Database File

To use a custom database file, mount a volume to the `/data` directory.

## Troubleshooting

### Cannot access the application

If you can't access the application at https://localhost:5000, try these steps:

1. **Run the connectivity test script**:
   ```
   test-container.bat  # On Windows
   ```

2. **Check browser HTTPS handling**:
   - Try different browsers (Firefox, Chrome, Edge)
   - Try typing "thisisunsafe" in Chrome when on the warning page
   - Try adding a security exception for the self-signed certificate

3. **Try alternative access methods**:
   - Try the plain HTTP test endpoint: http://localhost:80
   - Try using your machine's IP instead of localhost
   - Try 127.0.0.1 instead of localhost: https://127.0.0.1:5000

4. **Check Docker configuration**:
   ```
   docker-compose down
   docker-compose up -d --build
   ```

5. **Windows-specific issues**:
   - Check if Windows Defender Firewall is blocking the connections
   - Try temporarily disabling the firewall
   - Check Docker Desktop settings → Resources → WSL Integration

6. **Last resort - direct port forward**:
   ```
   docker exec -it water-manager /bin/bash
   # Inside container:
   apt-get update && apt-get install -y socat
   socat TCP-LISTEN:8080,fork TCP:localhost:5000
   ```
   Then try accessing https://localhost:8080 in your browser.

### Browser security warnings

Because the application uses a self-signed certificate, your browser will show a security warning. This is normal. To proceed:

- Click "Advanced" or "Details"
- Then click "Proceed to localhost (unsafe)" or similar option

For Chrome, you might need to type "thisisunsafe" while the warning page is active (just type it anywhere on the page).

## Development

### Rebuilding the Docker container

When you make changes to the code, you need to rebuild the Docker container:
```
docker-compose down
docker-compose up -d --build
```

