# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set environment variables to force CPU-only mode for whisper.cpp
ENV GGML_NO_CUDA=1
ENV GGML_NO_OPENCL=1
ENV WHISPER_NO_GPU=1

# Install system dependencies including FFmpeg for audio processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (excluding pywhispercpp first)
RUN grep -v "pywhispercpp" requirements.txt > /tmp/requirements_no_whisper.txt && \
    pip install --no-cache-dir -r /tmp/requirements_no_whisper.txt

# Force build pywhispercpp from source (not pre-compiled binary) with CPU-only support
RUN pip install --no-cache-dir --no-binary=pywhispercpp pywhispercpp==1.3.3

# Copy application code
COPY . .

# Create directories for SQLite database and audio storage
RUN mkdir -p /app/data /app/audio_storage

# Expose port
EXPOSE 5008

# Create a non-root user and set permissions
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/data /app/audio_storage
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5008/ || exit 1

# Run the application with Gunicorn (production WSGI server)
# --timeout 0 means no timeout limit (allows long-running transcriptions)
CMD ["gunicorn", "--bind", "0.0.0.0:5008", "--workers", "2", "--timeout", "0", "--certfile", "ssl/tailscale-cert.pem", "--keyfile", "ssl/tailscale-key.pem", "app:app"]