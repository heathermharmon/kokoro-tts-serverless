# Kokoro TTS RunPod Serverless Worker

Custom RunPod serverless worker that generates TTS audio and uploads directly to Cloudflare R2.

## Features
- Generates high-quality TTS using Kokoro model
- Uploads audio directly to R2 (avoids RunPod's 20MB response limit)
- Returns public URL for immediate playback
- Supports multiple voices
- Fast cold starts (model pre-loaded in Docker image)

## Build & Deploy

### 1. Build Docker Image
```bash
docker build -t kokoro-tts-r2:latest .
```

### 2. Push to Docker Hub
```bash
docker tag kokoro-tts-r2:latest YOUR_DOCKERHUB/kokoro-tts-r2:latest
docker push YOUR_DOCKERHUB/kokoro-tts-r2:latest
```

### 3. Create RunPod Serverless Endpoint

1. Go to RunPod Console > Serverless
2. Create new endpoint
3. Use Docker image: `YOUR_DOCKERHUB/kokoro-tts-r2:latest`
4. Set environment variables (secrets):
   - `R2_ACCOUNT_ID`: Your Cloudflare account ID
   - `R2_ACCESS_KEY_ID`: R2 access key
   - `R2_SECRET_ACCESS_KEY`: R2 secret key
   - `R2_BUCKET_NAME`: audio-studio
   - `R2_PUBLIC_URL`: https://pub-xxx.r2.dev

### 4. Update wp-config.php
```php
define('RUNPOD_ENDPOINT_ID', 'your-new-endpoint-id');
```

## API Usage

### Request
```json
{
  "input": {
    "text": "Hello, this is a test.",
    "voice": "af_heart",
    "speed": 1.0,
    "user_id": "123",
    "project_id": "proj_abc",
    "chapter_id": "ch_001"
  }
}
```

### Response
```json
{
  "success": true,
  "audio_url": "https://pub-xxx.r2.dev/kokoro_audio/123/project_proj_abc_chapter_ch_001.wav",
  "duration": 2.5,
  "voice": "af_heart",
  "text_length": 25,
  "generation_time": 1.2,
  "upload_time": 0.3,
  "format": "wav",
  "sample_rate": 24000
}
```

## Available Voices
- `af_heart` - Female, warm (default)
- `af_alloy` - Female, neutral
- `af_nova` - Female, bright
- `af_bella` - Female, soft
- `am_michael` - Male, neutral
- `af_sarah` - Female, clear
