import os
import subprocess
from pydub import AudioSegment
from pathlib import Path
import shutil
import demucs.separate

import logging

logger = logging.getLogger(__name__)

# TODO: Update demucs version once updated separate.py is released
# NOTE: This is a hacky way to get the updated separate.py
# demucs latest release does not have the updated separate.py
# https://github.com/facebookresearch/demucs/pull/474
# jankily replace the main function with local copy of updated main
from .demucs_separate_updated import main
demucs.separate.main = main

def isolate_voice(input_fpath: Path, output_directory: Path, bitrate="320k", file_format="mp3") -> Path:
    processing_dir = Path('tmp_demucs')
    os.makedirs(processing_dir, exist_ok=True)

    # https://github.com/facebookresearch/demucs
    DEMUCS_MODEL = 'htdemucs' # Default model
    # TODO: Voice isolation seems to work, but
    # sometimes seems to speed up the cloned voice
    # Should investigate if there's a way to improve thi
    demucs.separate.main(["-n", DEMUCS_MODEL, "-d", "cpu", "--two-stems=vocals", "--overlap", ".01", "-o", processing_dir.as_posix(), input_fpath.as_posix()])
    processed_audio_dir = Path(os.path.join(processing_dir.as_posix(), DEMUCS_MODEL, input_fpath.stem))
    # Find the separated vocal track
    output_voice_file = None
    if "vocals.wav" not in os.listdir(processed_audio_dir):
        shutil.rmtree(processing_dir)
        raise FileNotFoundError("Vocals file not found in the processed audio directory")
    else:
        output_voice_file = Path(os.path.join(output_directory, f"{input_fpath.stem}_voice_isolated.mp3"))
        # audio = AudioSegment.from_mp3(output_voice_file)
        audio = AudioSegment.from_wav(processed_audio_dir / "vocals.wav")
        audio.export(output_voice_file, format=file_format, bitrate=bitrate)
        shutil.rmtree(processing_dir)
    return output_voice_file