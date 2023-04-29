import os
import hikari
import logging
from pathlib import Path
from deepfake_radio.utils import yaml_to_dataclass, init_logger
from deepfake_radio.process_voice import process_voice_clip
from deepfake_radio.api import upload_voice
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
    if os.environ.get('PROCESS_AND_UPLOAD_VOICES_ON_STARTUP'):
        logger.warning(f"PROCESS_AND_UPLOAD_VOICES_ON_STARTUP is set to {os.environ.get('PROCESS_AND_UPLOAD_VOICES_ON_STARTUP')}. Processing and uploading all voices.")
        logger.warning("This may take some time, especially if voice isolation is enabled and you have many voices.")

        process_and_upload_all_voices(Path("voices"))

    bot.run(
        activity=hikari.Activity(
            name="AI voices.",
            type=hikari.ActivityType.LISTENING
        ),
        ignore_session_start_limit=True,
        check_for_updates=False,
        status=hikari.Status.ONLINE,
        coroutine_tracking_depth=20,
        propagate_interrupts=True
    )