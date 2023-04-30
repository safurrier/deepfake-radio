import os
import hikari
import logging
from pathlib import Path
from deepfake_radio.utils import yaml_to_dataclass, init_logger
from deepfake_radio.process_voice import process_voice_clip
from deepfake_radio.api import upload_voice
from deepfake_radio.bot import bot
import modal
import lightbulb
stub = modal.Stub("deepfake_radio")


init_logger()
logger = logging.getLogger(__name__)

bot_image = modal.Image.debian_slim(python_version="3.10.8").apt_install('ffmpeg').pip_install(
"demucs==4.0.0",
"requests==2.28.1",
"hikari==2.0.0.dev115",
"pydub==0.25.1",
"hikari-lightbulb==2.3.1",
"hikari-miru==2.0.4",
"pyyaml==6.0",
"python_dotenv==1.0.0",
"yt_dlp==2023.03.04",
)
@stub.function(image=bot_image)
def process_voice(voice_dir: Path):
    voice = yaml_to_dataclass(voice_dir / "config.yaml")
    for clip in voice.clips:
      process_voice_clip(clip, voice_dir)

@stub.function(image=bot_image)
def process_and_upload_all_voices(voices_dir: Path):
    for voice_dir in voices_dir.glob("*"):
      process_voice(voice_dir)
      upload_voice(voice_dir)

@stub.function(image=bot_image)
def run_bot(bot: lightbulb.BotApp):
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


@stub.local_entrypoint()
def main():
    if not os.environ.get('BOT_TOKEN'):
        raise ValueError("No bot token provided! Please provide a bot token in the .env file under BOT_TOKEN.")
    if not os.environ.get('ELEVEN_API_KEY'):
        raise ValueError("No API key provided! Please provide an API key in the .env file under ELEVEN_API_KEY.")
    if os.environ.get('PROCESS_AND_UPLOAD_VOICES_ON_STARTUP'):
        logger.warning(f"PROCESS_AND_UPLOAD_VOICES_ON_STARTUP is set to {os.environ.get('PROCESS_AND_UPLOAD_VOICES_ON_STARTUP')}. Processing and uploading all voices.")
        logger.warning("This may take some time, especially if voice isolation is enabled and you have many voices.")

        process_and_upload_all_voices(Path("voices"))

    run_bot(bot)
