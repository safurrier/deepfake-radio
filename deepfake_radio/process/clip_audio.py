import os
from pydub import AudioSegment
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def split_audio_clips(input_file, output_directory, max_clip_size=10):
    fname = Path(input_file).stem
    audio = AudioSegment.from_mp3(input_file)

    clip_length = max_clip_size * 1000  # Convert max_clip_size to milliseconds
    num_clips = len(audio) // clip_length

    output_files = []
    for i in range(num_clips):
        start_time = i * clip_length
        end_time = (i + 1) * clip_length
        clip = audio[start_time:end_time]
        output_file = os.path.join(output_directory, f"{fname}_{i}.mp3")
        clip.export(output_file, format="mp3")
        output_files.append(Path(output_file))

    return output_files