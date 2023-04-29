from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)


def time_str_to_ms(time_str):

    h, m, s = time_str.split(':')
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000

def trim_mp3(input_filepath, output_filepath, start_time=None, end_time=None):
    # Load the MP3 file
    audio = AudioSegment.from_mp3(input_filepath)

    # Convert input HH:MM:SS format to milliseconds and validate the values
    start_time = time_str_to_ms(start_time) if start_time else 0
    end_time = time_str_to_ms(end_time) if end_time else len(audio)
    # Trim the audio and export the result
    trimmed_audio = audio[start_time:end_time]
    trimmed_audio.export(output_filepath, format="mp3")