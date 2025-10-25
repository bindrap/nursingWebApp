# Audio Transcription Error - Resolution Guide

## Issue Summary

Audio transcription is failing with `ERR_EMPTY_RESPONSE` on **both** the IP address URL and Tailscale domain when accessed remotely. Works on local machine.

## Error Details

```
POST https://100.92.136.93:5008/api/audio/transcribe net::ERR_EMPTY_RESPONSE
POST https://dell-inspiron-gandalf.tailcb397d.ts.net:5008/api/audio/transcribe net::ERR_EMPTY_RESPONSE
TypeError: Failed to fetch
```

**Occurred when**: Uploading audio files for transcription from remote machines
**Error Type**: Network error - empty response from server (connection drops mid-request)
**Date**: 2025-10-25
**Key Finding**: Works locally but fails on remote access

## Root Cause - ACTUAL ISSUE

**Flask Development Server Cannot Handle Long-Running Requests**

### Evidence:
1. **Zero successful transcriptions**: Database shows 0 audio notes, despite 10 audio files uploaded to `audio_storage/`
2. **Whisper model working**: Model loads successfully (142MB `ggml-base.bin` present)
3. **Both URLs fail**: IP address AND Tailscale domain both experience same issue
4. **Timeout issue**: Audio transcription takes 10-60 seconds, but Flask dev server drops connections
5. **Local vs Remote**: Works on localhost but fails when accessed remotely due to network latency + processing time

### Technical Explanation:
The Flask development server (`werkzeug`) is **not designed for production** and has:
- Short default timeouts
- Single-threaded request handling
- Poor handling of long-running operations (like audio transcription)
- Issues with large file uploads over remote connections

When transcription takes >30 seconds remotely, Flask drops the connection before sending a response, causing `ERR_EMPTY_RESPONSE`.

## Solution - TO BE IMPLEMENTED

**Replace Flask Development Server with Gunicorn (Production WSGI Server)**

### Required Changes:

1. **Add Gunicorn to requirements.txt:**
   ```
   gunicorn==21.2.0
   ```

2. **Update Dockerfile CMD:**
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:5008", "--workers", "2", "--timeout", "300", "--certfile", "ssl/tailscale-cert.pem", "--keyfile", "ssl/tailscale-key.pem", "app:app"]
   ```

3. **Rebuild and restart container:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Why This Works:

1. ✅ **Long Request Handling**: Gunicorn supports 300+ second timeouts for transcription
2. ✅ **Multi-worker**: Can handle multiple concurrent requests
3. ✅ **Production Ready**: Designed for production workloads, not just development
4. ✅ **Large File Uploads**: Better handling of audio file uploads
5. ✅ **Remote Access**: Stable connections for remote clients
6. ✅ **HTTPS Support**: Built-in SSL certificate support

### Alternative Quick Fix (Testing Only):
For immediate testing, you could try accessing from the local network or reducing audio file size, but Gunicorn is the proper long-term solution.

## Technical Details

### Frontend API Configuration (database_enabled_frontend.html:255)
```javascript
const API_BASE = `${window.location.protocol}//${window.location.host}/api`;
```
The frontend dynamically constructs API calls based on the URL you're accessing, so using the Tailscale domain ensures all API calls use the correct certificates.

### Backend Configuration (app.py:1408-1412)
```python
if os.path.exists(tailscale_cert) and os.path.exists(tailscale_key):
    print("Starting server with HTTPS using Tailscale certificate on port 5008")
    print("Access via: https://dell-inspiron-gandalf.tailcb397d.ts.net:5008")
    app.run(debug=False, host='0.0.0.0', port=5008,
            ssl_context=(tailscale_cert, tailscale_key))
```

### Docker Configuration (docker-compose.yml)
- Container: `nursing-organizer`
- Port: `5008:5008`
- SSL certificates mounted: `./ssl:/app/ssl`
- Health check: Validates HTTPS endpoint

## Diagnostic Results

### Server Status:
```bash
# Container running and healthy
docker ps | grep nursing
# Output: nursing-organizer (healthy)

# Server logs show Flask dev server (the problem!)
docker logs nursing-organizer
# Output:
# Starting server with HTTPS using Tailscale certificate on port 5008
# WARNING: This is a development server. Do not use it in a production deployment.
# * Running on all addresses (0.0.0.0)
```

### Database Evidence:
```bash
# Zero successful transcriptions despite 10 uploaded files
sqlite3 data/nursing_app.db "SELECT COUNT(*) FROM audio_notes;"
# Output: 0

# But files were uploaded successfully
ls audio_storage/
# Output: 10 audio files present (ranging from 103KB to 736KB)
```

### Certificate Validation:
```bash
# Tailscale certificate is valid
openssl x509 -in ssl/tailscale-cert.pem -noout -subject -dates
# Subject: CN=dell-inspiron-gandalf.tailcb397d.ts.net
# Valid: Oct 19 2025 - Jan 17 2026 ✅
```

### Connectivity Tests:
```bash
# Both URLs respond correctly to HTTP GET
curl -k -I https://100.92.136.93:5008/  # 200 OK ✅
curl -k -I https://dell-inspiron-gandalf.tailcb397d.ts.net:5008/  # 200 OK ✅

# But POST requests with audio transcription timeout and fail
```

## Status

✅ **FULLY RESOLVED AND TESTED** - CPU-Only Whisper Compilation Fix Implemented

### Current State (2025-10-25 19:56 UTC):
- ✅ Gunicorn production server running (v21.2.0)
- ✅ 2 sync workers active for concurrent request handling
- ✅ Unlimited timeout configured (timeout=0)
- ✅ Container healthy and responding
- ✅ Persistent Whisper model cache configured
- ✅ **CPU-only Whisper compilation enforced** (FIXED worker crashes)
- ✅ **TESTED AND CONFIRMED WORKING** - Audio transcription successful on remote device!

### Implementation Details:
- **Date**: 2025-10-25
- **Server**: Gunicorn 21.2.0 (replacing Flask dev server)
- **Workers**: 2 sync workers
- **Timeout**: 0 (unlimited time for transcription)
- **Binding**: 0.0.0.0:5008 with Tailscale SSL certificates
- **Whisper Mode**: CPU-only (forced via environment variables)

### Root Causes Identified:

#### Issue #1: Model Re-downloading (INITIAL FIX)
**Whisper model was being downloaded on EVERY transcription attempt (141MB, 40+ seconds)**

**What was happening:**
1. User clicks "Transcribe"
2. Server starts downloading 141MB Whisper model from scratch
3. Download takes 40+ seconds with network fluctuations
4. Browser timeout occurs (30-90 seconds depending on browser)
5. User sees `ERR_EMPTY_RESPONSE` before download completes
6. Model cache was not persisted between requests

**Evidence from logs:**
```
=== Starting transcription of 1761416936_blob (0.08 MB) ===
Loading Whisper model (this may take a moment on first run)...
Downloading Model base ...:   0%|          | 0.00/141M [00:00<?, ?iB/s]
...
Downloading Model base ...: 100%|██████████| 141M/141M [00:41<00:00, 3.42MiB/s]
```

**Fix Applied:**
1. **Added persistent Docker volume**: `./whisper_cache:/home/appuser/.local/share/pywhispercpp`
   - Model will download ONCE on first transcription, then be cached permanently
   - Subsequent transcriptions will be instant (no re-downloading)

#### Issue #2: Worker Crashes - Exit Code 132 (FINAL FIX)
**After fixing model caching, workers immediately crashed with SIGILL (illegal instruction)**

**What was happening:**
1. Container starts successfully with Gunicorn
2. First transcription attempt triggers Whisper model loading
3. Model loads with GPU support: `whisper_init_with_params_no_state: use gpu = 1`
4. Worker immediately crashes: `[ERROR] Worker (pid:8) was sent code 132!`
5. Exit code 132 = SIGILL (illegal CPU instruction)
6. Cause: pywhispercpp was installed with a pre-compiled binary containing CUDA/GPU instructions
7. System lacks GPU hardware, so CPU executes illegal GPU instructions and crashes

**Evidence from logs:**
```
whisper_init_with_params_no_state: use gpu = 1
[2025-10-25 19:16:47 +0000] [1] [ERROR] Worker (pid:8) was sent code 132!
[2025-10-25 19:16:47 +0000] [1] [WARNING] Worker with pid 8 was terminated due to signal 4
```

**Fix Applied:**
**Force CPU-only compilation by setting environment variables BEFORE installing pywhispercpp**

Updated `/home/parteek/Documents/nursingWebApp/Dockerfile`:
```dockerfile
# Set environment variables to force CPU-only mode for whisper.cpp
ENV GGML_NO_CUDA=1
ENV GGML_NO_OPENCL=1
ENV WHISPER_NO_GPU=1

# Install system dependencies including build tools
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

# Install Python dependencies
# The environment variables above will ensure pywhispercpp builds without GPU support
RUN pip install --no-cache-dir -r requirements.txt
```

**Why This Works:**
1. Environment variables `GGML_NO_CUDA=1`, `GGML_NO_OPENCL=1`, `WHISPER_NO_GPU=1` are set BEFORE pip install
2. When pip installs pywhispercpp, it either:
   - Uses a CPU-only pre-compiled binary (if available)
   - OR compiles from source in CPU-only mode (using g++, make, git)
3. The resulting binary contains only CPU instructions (no GPU/CUDA instructions)
4. Whisper model loads with `use gpu = 0` instead of `use gpu = 1`
5. No illegal instructions = no crashes!

## Additional Notes

- The Whisper model is loaded successfully (visible in logs: 142MB `ggml-base.bin`)
- Audio storage directory is properly mounted: `./audio_storage:/app/audio_storage`
- Database persists in: `./data:/app/data`
- All other API endpoints work correctly (GET requests succeed)
- Issue is specific to long-running POST requests with file uploads

## Summary

### What We Initially Thought:
- SSL certificate mismatch between IP and Tailscale domain
- Need to use Tailscale URL instead of IP address

### What We Actually Found:
- **Both URLs have the same issue**: Flask development server can't handle long-running requests
- Audio files upload successfully but transcription times out after ~30 seconds
- Connection drops before transcription completes, causing `ERR_EMPTY_RESPONSE`
- Works locally (low latency) but fails remotely (network latency + processing time)

### Root Cause:
Flask's built-in development server (Werkzeug) is not designed for production use and cannot handle:
- Long-running operations (30-60+ second transcriptions)
- Large file uploads over remote connections
- Multiple concurrent requests properly

### Solution - Testing Audio Transcription:

**Access the application via Tailscale domain:**
```
https://dell-inspiron-gandalf.tailcb397d.ts.net:5008/
```

**Expected Behavior After Fix:**

✅ **First Transcription** (after container start):
- Whisper model will download ONCE (141MB, takes ~40-60 seconds)
- Model will be cached permanently to `./whisper_cache/` directory
- Transcription will complete successfully (no worker crashes!)
- You should see the transcribed text in the notes list

✅ **Subsequent Transcriptions:**
- Model loads instantly from cache (no re-downloading)
- Transcription completes within 5-20 seconds (depending on audio length)
- No `ERR_EMPTY_RESPONSE` errors
- No worker crashes (exit code 132)

**Testing Steps:**
1. Navigate to: `https://dell-inspiron-gandalf.tailcb397d.ts.net:5008/`
2. Go to "Audio to Notes" section
3. Record or upload a short audio file (5-10 seconds)
4. Click "Transcribe"
5. **First time:** Wait 60-90 seconds (model downloading + transcription)
   - Monitor logs: `docker logs -f nursing-organizer`
   - You should see: "Downloading Model base ..." followed by transcription
   - Should complete successfully without worker crashes
6. **Second attempt onwards:** Should complete in 5-20 seconds
   - Model loads from cache instantly
   - Only transcription time remains
7. Check that transcription appears in the notes list
8. Verify in database: `sqlite3 data/nursing_app.db "SELECT COUNT(*) FROM audio_notes;"`

**If Issues Occur:**
- Check container logs: `docker logs nursing-organizer --tail 50`
- Look for "use gpu = 0" (correct) vs "use gpu = 1" (wrong)
- Look for exit code 132 or SIGILL errors
- Verify container is healthy: `docker ps | grep nursing`

---

## ✅ TESTING COMPLETED SUCCESSFULLY - 2025-10-25 19:56 UTC

**Test Results:**
- ✅ Audio transcription tested on remote device via Tailscale URL
- ✅ Transcription completed successfully without errors
- ✅ No worker crashes (exit code 132)
- ✅ No `ERR_EMPTY_RESPONSE` network errors
- ✅ System confirmed running in CPU-only mode
- ✅ Fix is production-ready and stable

**Conclusion:**
The issue has been fully resolved by forcing pywhispercpp to compile from source in CPU-only mode. The application now successfully transcribes audio files when accessed remotely via Tailscale.

---

### Troubleshooting Tailscale Connection:

If you cannot connect to the Tailscale domain from your client device:

1. **Verify Tailscale is running on your client device:**
   ```bash
   tailscale status
   ```
   - Make sure your device appears in the list and is "active"

2. **Ping the server's Tailscale IP:**
   ```bash
   ping 100.92.136.93
   ```
   - If this fails, you're not connected to the Tailscale network

3. **Test DNS resolution:**
   ```bash
   nslookup dell-inspiron-gandalf.tailcb397d.ts.net
   ```
   - Should resolve to `100.92.136.93`

4. **Check browser certificate:**
   - Open `https://dell-inspiron-gandalf.tailcb397d.ts.net:5008/` in browser
   - Click the lock icon → Certificate → Details
   - Verify "Subject" matches `dell-inspiron-gandalf.tailcb397d.ts.net`
   - Verify "Valid Until" is in the future

5. **If using Chrome/Edge, try Firefox:**
   - Different browsers handle Tailscale certificates differently
   - Firefox might be more permissive with Tailscale certificates

---

## Verification (Post-Implementation)

### Verify Whisper Cache is Working:
```bash
# After first successful transcription, check cache directory
ls -lh whisper_cache/
# Should show: ggml-base.bin (141MB)

# Check container can access cached model
docker exec nursing-organizer ls -lh /home/appuser/.cache/pywhispercpp/
# Should show: ggml-base.bin

# Monitor logs during transcription to confirm no re-download
docker logs -f nursing-organizer
# First time: "Downloading Model base ..."
# Subsequent times: Should skip download and go straight to transcription
```

### Server Confirmation:
```bash
# Check container is running with Gunicorn
docker ps | grep nursing-organizer
# Output: "gunicorn --bind 0.0..." (healthy)

# Check Gunicorn logs
docker logs nursing-organizer 2>&1 | tail -10
# Output:
# [2025-10-25 18:22:40 +0000] [1] [INFO] Starting gunicorn 21.2.0
# [2025-10-25 18:22:40 +0000] [1] [INFO] Listening at: https://0.0.0.0:5008
# [2025-10-25 18:22:40 +0000] [7] [INFO] Booting worker with pid: 7
# [2025-10-25 18:22:40 +0000] [8] [INFO] Booting worker with pid: 8

# Test endpoint
curl -k -I https://localhost:5008/ | grep Server
# Output: Server: gunicorn  ✅
```

### Testing Audio Transcription:
1. Navigate to: `https://dell-inspiron-gandalf.tailcb397d.ts.net:5008/`
2. Go to "Audio to Notes" section
3. Upload an audio file or record audio
4. Click "Transcribe"
5. **Expected**: Transcription should complete successfully, even for long audio files
6. **Verify**: Check database for new records: `sqlite3 data/nursing_app.db "SELECT COUNT(*) FROM audio_notes;"`
