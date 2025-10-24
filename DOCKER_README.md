# Nursing WebApp - Docker Setup

This setup allows you to run the Nursing WebApp in a Docker container for easy deployment and consistency across environments.

## Prerequisites

- Docker Desktop installed on Windows
- Docker Compose (included with Docker Desktop)
- `.env` file with your Ollama API credentials (for AI features)

## Environment Setup

Create a `.env` file in the project root with your Ollama Cloud credentials:

```env
OLLAMA_HOST=https://ollama.com
OLLAMA_API_KEY=your_api_key_here
OLLAMA_MODEL=gpt-oss:120b-cloud
```

This enables:
- AI-powered test generation
- Audio transcription enhancement
- Smart study schedule generation

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

The following directories are mounted as volumes for data persistence:

- **`./data`** - SQLite database (all your assignments, grades, goals, etc.)
- **`./audio_storage`** - Recorded and uploaded audio files
- **`./favicon_io`** - Static assets (favicons)

Your data will persist between container restarts and updates. The audio recordings and database are stored outside the container, so they won't be lost when you rebuild.

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

### Audio Recording Issues
**Microphone not accessible:**
- Audio recording requires HTTPS or localhost
- If using Docker, access via `http://localhost:5008` (not container IP)
- Check browser permissions for microphone access

**Audio files not persisting:**
- Verify `./audio_storage` directory exists on host
- Check volume mount in `docker-compose.yml`
- Ensure proper permissions: `chmod 755 ./audio_storage`

**Transcription taking too long:**
- First transcription downloads Whisper model (~140MB)
- Subsequent transcriptions are faster
- Check container logs: `docker-compose logs -f nursing-webapp`

### Missing AI Features
If test generation or audio enhancement isn't working:
```bash
# Verify environment variables are set
docker-compose exec nursing-webapp env | grep OLLAMA

# Check .env file exists and has correct values
cat .env

# Restart container to reload environment
docker-compose restart
```

## Production Deployment

For production deployment, consider:
1. Using environment variables for configuration
2. Setting up proper logging
3. Using a reverse proxy (nginx)
4. Implementing SSL/TLS

## Features Included

✅ **Audio-to-Notes** - Record lectures, upload audio, AI transcription with Whisper.cpp
✅ **AI Test Generation** - Generate practice tests from PDFs, DOCX, PPTX files
✅ **Test Modes** - Practice mode with instant feedback, Exam mode with timer
✅ **Dark/Light Mode Toggle**
✅ **Drag & Drop Calendar**
✅ **Quick Add Widget** (Floating Action Button)
✅ **AI Study Schedule Generator**
✅ **Achievement Badges System**
✅ **Motivational Quotes Rotation**
✅ **Stress Level Tracker**
✅ **Mobile-Friendly Responsive Design**

All features are fully functional in the containerized version!

## What's Included in the Container

The Docker image includes:
- Python 3.11 with all dependencies
- **FFmpeg** for audio processing
- **Whisper.cpp** for speech-to-text transcription
- **Flask** web server
- **SQLite** database
- **Ollama API client** for AI features
- Health checks and automatic restart