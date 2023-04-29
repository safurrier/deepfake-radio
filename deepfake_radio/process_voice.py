from pathlib import Path
import shutil
import os
import logging


from .data_models import VoiceClip
from .process.download_yt import download_youtube_video
from .process.trim_audio import trim_mp3
from .process.isolate_vocals import isolate_voice
from .process.clip_audio import split_audio_clips

logger = logging.getLogger(__name__)

def process_voice_clip(voice_clip:VoiceClip, voice_dir:Path):
    # Create directories to hold audio files
    for dir in ['input', 'interim', 'upload']:
        os.makedirs(voice_dir / dir, exist_ok=True)
    # Remove any spaces from fname
    voice_name_fpath_compatible = voice_clip.name.replace(" ", "_")
    fname = Path(f"{voice_clip.idx}_{voice_name_fpath_compatible}.mp3")
    interim_output_dir = voice_dir / "interim"
    output_dir = voice_dir / "upload"

    # Track which files will ultimately be uploaded
    output_files = []
    # Download the voice
    if voice_clip.source.type == "youtube":
        # Download the voice
        interim_output_path = (interim_output_dir / fname)
        ydl_output_fpath = (interim_output_path.parent / interim_output_path.stem).as_posix()
        if not os.path.exists(ydl_output_fpath + ".mp3"):
          logger.info(f"Youtube clip not found, downloading.[clip_path={ydl_output_fpath}]]")
          download_youtube_video(voice_clip.source.location, ydl_output_fpath)

    elif voice_clip.source.type == "file":
        # Copy the voice to /interim
        if not os.path.exists(interim_output_dir / fname):
          shutil.copy(voice_dir /voice_clip.source.location, interim_output_dir / fname)
    output_files = [interim_output_dir / fname]
    # Trim to start and end time
    if voice_clip.source.start_time or voice_clip.source.end_time:
        logger.info(f"Trimming clip.[clip_start={voice_clip.source.start_time}, clip_end={voice_clip.source.end_time}, clip_path={interim_output_dir / fname}]]")
        trim_mp3(interim_output_dir / fname, interim_output_dir / fname, voice_clip.source.start_time, voice_clip.source.end_time)
    # Isolate the voice
    if voice_clip.isolate:
        logger.info(f"Isolating voice.[clip_path={interim_output_dir / fname}]]")
        isolated_voice_fname = Path(fname.stem + "_voice_isolated.mp3")
        if not os.path.exists(interim_output_dir / isolated_voice_fname):
          logger.info(f"Voice isolated clip not found, Processing.[clip_path={interim_output_dir / fname}]]")
          isolate_voice(interim_output_dir / fname, interim_output_dir)
        fname = Path(fname.stem + "_voice_isolated.mp3")
        output_files = [interim_output_dir / fname]
    # Clip the voice
    if voice_clip.clip_size:
        logger.info(f"Clipping voice.[clip_size={voice_clip.clip_size}, clip_path={interim_output_dir / fname}]]")
        output_files = split_audio_clips(interim_output_dir / fname, interim_output_dir, voice_clip.clip_size)
    # Move the voice to upload dir
    logger.info(f"Moving voice to upload dir.[output_dir={output_dir}]]")
    logger.info(f"Files to upload.[output_files={[f.stem for f in output_files]}]]")
    for file in output_files:
        shutil.copy(file, output_dir / file.name)
