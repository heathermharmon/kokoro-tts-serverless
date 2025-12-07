"""
Kokoro TTS RunPod Serverless Handler with R2 Upload
Generates audio and uploads directly to Cloudflare R2, returns URL
"""

import runpod
import torch
import soundfile as sf
import io
import os
import boto3
from botocore.config import Config
import uuid
import time

# Initialize Kokoro TTS model (loaded once, reused for all requests)
kokoro_model = None
kokoro_voicepacks = {}

def load_kokoro():
    """Load Kokoro TTS model and voicepacks"""
    global kokoro_model, kokoro_voicepacks

    if kokoro_model is not None:
        return kokoro_model, kokoro_voicepacks

    from kokoro import KPipeline

    # Load model
    kokoro_model = KPipeline(lang_code='a')  # 'a' for American English

    # Pre-load common voicepacks
    voices = ['af_heart', 'af_alloy', 'af_nova', 'af_bella', 'am_michael', 'af_sarah']
    for voice in voices:
        try:
            kokoro_voicepacks[voice] = kokoro_model.load_voice(voice)
        except Exception as e:
            print(f"Warning: Could not load voice {voice}: {e}")

    return kokoro_model, kokoro_voicepacks


def get_r2_client():
    """Create R2 client using environment variables"""
    return boto3.client(
        's3',
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
        config=Config(signature_version='s3v4'),
        region_name='auto'
    )


def upload_to_r2(audio_data, filename):
    """Upload audio bytes to R2 and return public URL"""
    try:
        client = get_r2_client()
        bucket = os.environ.get('R2_BUCKET_NAME', 'audio-studio')
        public_url = os.environ.get('R2_PUBLIC_URL', '')

        # Upload to R2
        client.put_object(
            Bucket=bucket,
            Key=filename,
            Body=audio_data,
            ContentType='audio/wav'
        )

        # Return public URL
        return f"{public_url}/{filename}"
    except Exception as e:
        raise Exception(f"R2 upload failed: {str(e)}")


def generate_tts(text, voice='af_heart', speed=1.0):
    """Generate TTS audio using Kokoro"""
    model, voicepacks = load_kokoro()

    # Get voicepack (load if not cached)
    if voice not in voicepacks:
        try:
            voicepacks[voice] = model.load_voice(voice)
        except:
            # Fallback to heart voice
            voice = 'af_heart'
            if voice not in voicepacks:
                voicepacks[voice] = model.load_voice(voice)

    voicepack = voicepacks[voice]

    # Generate audio
    generator = model(text, voice=voicepack, speed=speed)

    # Collect all audio chunks
    audio_chunks = []
    for _, _, audio_chunk in generator:
        audio_chunks.append(audio_chunk)

    # Concatenate all chunks
    import numpy as np
    full_audio = np.concatenate(audio_chunks)

    return full_audio, 24000  # Kokoro outputs at 24kHz


def handler(job):
    """RunPod serverless handler"""
    job_input = job.get('input', {})

    # Get parameters
    text = job_input.get('text', '')
    voice = job_input.get('voice', 'af_heart')
    speed = job_input.get('speed', 1.0)
    user_id = job_input.get('user_id', '0')
    project_id = job_input.get('project_id', '')
    chapter_id = job_input.get('chapter_id', '')

    if not text:
        return {"error": "No text provided"}

    try:
        start_time = time.time()

        # Generate audio
        audio_data, sample_rate = generate_tts(text, voice, speed)
        generation_time = time.time() - start_time

        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        wav_bytes = buffer.getvalue()

        # Generate filename
        if project_id and chapter_id:
            filename = f"kokoro_audio/{user_id}/project_{project_id}_chapter_{chapter_id}.wav"
        else:
            filename = f"kokoro_audio/{user_id}/audio_{uuid.uuid4().hex[:8]}.wav"

        # Upload to R2
        upload_start = time.time()
        audio_url = upload_to_r2(wav_bytes, filename)
        upload_time = time.time() - upload_start

        # Calculate duration
        duration = len(audio_data) / sample_rate

        return {
            "success": True,
            "audio_url": audio_url,
            "duration": round(duration, 2),
            "voice": voice,
            "text_length": len(text),
            "generation_time": round(generation_time, 2),
            "upload_time": round(upload_time, 2),
            "format": "wav",
            "sample_rate": sample_rate
        }

    except Exception as e:
        return {"error": str(e)}


# Start the serverless handler
runpod.serverless.start({"handler": handler})
