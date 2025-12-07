# Kokoro TTS RunPod Serverless Worker with R2 Upload
# Using RunPod's base image for faster builds
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    runpod \
    boto3 \
    soundfile \
    kokoro>=0.9.2

# Copy handler
COPY handler.py /app/handler.py

# Start handler
CMD ["python", "-u", "handler.py"]
