# Kokoro TTS RunPod Serverless Worker with R2 Upload
# GPU-enabled using NVIDIA CUDA slim base
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.10 /usr/bin/python

# Install PyTorch with CUDA support (cu118 for CUDA 11.8)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
RUN pip install --no-cache-dir \
    runpod \
    boto3 \
    soundfile \
    kokoro>=0.9.2

# Copy handler
COPY handler.py /app/handler.py

# Start handler
CMD ["python", "-u", "handler.py"]
