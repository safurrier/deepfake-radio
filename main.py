import os
import hikari
import logging
import json
from pathlib import Path
from deepfake_radio.utils import yaml_to_dataclass, init_logger
from deepfake_radio.process_voice import process_voice_clip
from deepfake_radio.api import upload_voice, fetch_voices
from deepfake_radio.bot import bot

init_logger()
logger = logging.getLogger(__name__)

def process_voice(voice_dir: Path):
    voice = yaml_to_dataclass(voice_dir / "config.yaml")
    for clip in voice.clips:
      process_voice_clip(clip, voice_dir)


def process_and_upload_all_voices(voices_dir: Path):
    for voice_dir in voices_dir.glob("*"):
      process_voice(voice_dir)
      upload_voice(voice_dir)



if __name__ == "__main__":
    if not os.environ.get('BOT_TOKEN'):
        raise ValueError("No bot token provided! Please provide a bot token in the .env file under BOT_TOKEN.")
    if not os.environ.get('ELEVEN_API_KEY'):
        raise ValueError("No API key provided! Please provide an API key in the .env file under ELEVEN_API_KEY.")
    if os.environ.get('PROCESS_VOICES'):
        logger.warning(f"PROCESS_VOICES is set to {os.environ.get('PROCESS_AND_UPLOAD_VOICES_ON_STARTUP')}. Processing all voices.")
        logger.warning("This may take some time, especially if voice isolation is enabled and you have many voices.")
        for voice_dir in Path("voices").glob("*"):
            process_voice(voice_dir)

    if os.environ.get('UPLOAD_VOICES'):
        for voice_dir in Path("voices").glob("*"):
            upload_voice(voice_dir)

    # Get available voices and save them to a JSON file
    with open("voices.json", "w") as json_file:
        json.dump(fetch_voices(), json_file)


    bot.run(
        activity=hikari.Activity(
            name="Deepfake Radio",
            type=hikari.ActivityType.LISTENING
        ),
        ignore_session_start_limit=True,
        check_for_updates=False,
        status=hikari.Status.ONLINE,
        coroutine_tracking_depth=20,
        propagate_interrupts=True
    )