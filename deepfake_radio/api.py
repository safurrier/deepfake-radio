import requests
import os
from dotenv import load_dotenv
from .utils import yaml_to_dataclass
from pathlib import Path
from typing import Dict
from itertools import islice
import logging

logger = logging.getLogger(__name__)
load_dotenv()

def fetch_voices(max_voices: int=25) -> Dict[str, str]:
    """
    Fetch the available voices for the bot on startup.

    Raises:
        ValueError: Raised if no API key is provided in the .env file.
    """
    api_key = os.environ.get('ELEVEN_API_KEY')

    if not api_key:
        raise ValueError("ERROR: No API key provided! Please provide an API key in the .env file.")

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        'accept': 'application/json',
        'xi-api-key': api_key
    }
    response = requests.get(url, headers=headers)

    cloned_voices = [voice for voice in response.json()['voices'] if voice['category'] == 'cloned']
    voices = {voice['name']: voice['voice_id'] for voice in cloned_voices}

    if len(voices) > max_voices:
        warning_msg = f"More than {max_voices} custom voices detected items, some items will be excluded."
        logger.warning(warning_msg)
        voices = dict(islice(voices.items(), max_voices))

    return voices


def split_file(file, size_limit=10 * 1024 * 1024):
    with open(file, "rb") as f:
        voice = f.read()

    chunks = []
    chunk_filenames = []
    bytes_read = 0
    while bytes_read < len(voice):
        chunk = voice[bytes_read:bytes_read + size_limit]
        bytes_read += len(chunk)
        file_name = f"{file.stem}chunk{len(chunks) + 1}{file.suffix}"
        chunks.append({'filename': file_name, 'content': chunk})

    return chunks

def extract_audio_files(upload_dir: Path):
    files = []
    for file in upload_dir.glob("*.mp3"):
        with open(file, "rb") as f:
            voice = f.read()
            fsize = len(voice) / (1024 * 1024)  # Convert bytes to MB

            if fsize > 20:
                # Split the file into chunks
                file_chunks = split_file(file)
                for chunk in file_chunks:
                    files.append(chunk)
            else:
                files.append({'filename': file.name, 'content': voice})
    return files
def upload_voice(voice_dir: Path):
    voice = yaml_to_dataclass(voice_dir / "config.yaml")
    upload_dir = voice_dir / "upload"

    current_voices = fetch_voices(max_voices=999999)
    if voice.name in current_voices:
        logger.info(f"Voice {voice.name} already exists. Skipping upload.")
        return

    # Load in the upload files as byte string
    files = extract_audio_files(upload_dir)
    max_samples = 25
    if len(files) > max_samples:
        warning_msg = f"More than {max_samples} custom voices samples detected items, some items will be excluded. If using clips, try increasing the clip size or deleting some clips."
        logger.warning(warning_msg)
        print(warning_msg)
        files = files[:max_samples]

    api_key = os.environ.get("ELEVEN_API_KEY")

    # Upload the voice via POST
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        'Accept': 'application/json',
        'xi-api-key': api_key
    }

    data = {
        'name': voice.name,
        # 'labels': '{"accent": "American"}', # TODO: Add support for labels
        'description': voice.description
    }

    multipart_form_data = [
        ('files', (file_info['filename'], file_info['content'], 'audio/mpeg'))
        for file_info in files
    ]

    response = requests.post(url, headers=headers, data=data, files=multipart_form_data)

    # Check response status
    if response.status_code == 200:
        logger.info(f"All files uploaded successfully!.[voice_name: {voice.name}, n_samples: {len(files)}]")
    else:
        raise Exception(f"Failed to upload files. Response: {response.text}")
