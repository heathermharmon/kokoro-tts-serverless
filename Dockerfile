# Kokoro TTS RunPod Serverless Worker with R2 Upload
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    runpod \
    boto3 \
    soundfile \
    numpy \
    scipy \
    torch \
    torchaudio

# Install Kokoro TTS
RUN pip install --no-cache-dir kokoro>=0.9.2

# Download Kokoro model and voicepacks at build time for faster cold starts
RUN python -c "from kokoro import KPipeline; p = KPipeline(lang_code='a'); p.load_voice('af_heart')"

# Copy handler
COPY handler.py /app/handler.py

# Set environment variables (these will be overridden by RunPod secrets)
ENV R2_ACCOUNT_ID=""
ENV R2_ACCESS_KEY_ID=""
ENV R2_SECRET_ACCESS_KEY=""
ENV R2_BUCKET_NAME="audio-studio"
ENV R2_PUBLIC_URL=""

# Start handler
CMD ["python", "-u", "handler.py"]
