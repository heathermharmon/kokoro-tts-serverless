# Kokoro TTS RunPod Serverless Worker with R2 Upload
# CPU-only build to avoid disk space issues
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (CPU-only torch)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    runpod \
    boto3 \
    soundfile \
    kokoro>=0.9.2

# Copy handler
COPY handler.py /app/handler.py

# Start handler
CMD ["python", "-u", "handler.py"]
