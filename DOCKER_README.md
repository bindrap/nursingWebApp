# Nursing WebApp - Docker Setup

This setup allows you to run the Nursing WebApp in a Docker container for easy deployment and consistency across environments.

## Prerequisites

- Docker Desktop installed on Windows
- Docker Compose (included with Docker Desktop)

## Quick Start

1. **Build and start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   Open your browser and go to: `http://localhost:5008`

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Docker Commands

### First Time Setup
```bash
# Build and start in detached mode
docker-compose up --build -d

# View logs
docker-compose logs -f
```

### Daily Usage
```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# Restart the application
docker-compose restart
```

### Development
```bash
# Rebuild after code changes
docker-compose up --build

# View real-time logs
docker-compose logs -f nursing-webapp
```

## Data Persistence

- The SQLite database is stored in the `./data` directory
- Your data will persist between container restarts
- The `favicon_io` directory is also mounted for static assets

## Container Management

### Check container status:
```bash
docker-compose ps
```

### Access container shell:
```bash
docker-compose exec nursing-webapp /bin/bash
```

### View application logs:
```bash
docker-compose logs nursing-webapp
```

## Troubleshooting

### Port Already in Use
If port 5008 is already in use, modify the `docker-compose.yml` file:
```yaml
ports:
  - "5009:5008"  # Use port 5009 instead
```

### Database Issues
If you need to reset the database:
```bash
# Stop the application
docker-compose down

# Remove the database file
rm -rf ./data/nursing_app.db

# Restart the application (will recreate the database)
docker-compose up
```

## Production Deployment

For production deployment, consider:
1. Using environment variables for configuration
2. Setting up proper logging
3. Using a reverse proxy (nginx)
4. Implementing SSL/TLS

## Features Included

✅ Dark/Light Mode Toggle
✅ Drag & Drop Calendar
✅ Quick Add Widget (Floating Action Button)
✅ AI Study Schedule Generator
✅ Achievement Badges System
✅ Motivational Quotes Rotation
✅ Stress Level Tracker
✅ Mobile-Friendly Responsive Design

All features are fully functional in the containerized version!