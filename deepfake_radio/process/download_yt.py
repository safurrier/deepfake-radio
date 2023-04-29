import yt_dlp
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

def download_youtube_video(url, output_file, start_time=None, end_time=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_file,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
    }
    # Handle start time, end time
    post_processor_args = []
    if start_time:
        post_processor_args.append(f'-ss {start_time}')
    if end_time:
        post_processor_args.append(f'-t {end_time}')

    if post_processor_args:
        ydl_opts['ppa'] = ' '.join(post_processor_args)


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logger.info(f"Downloading youtube video.[url={url}]")
        ydl.download([url])


def trim_mp3(input_file, output_file, start_time=None, end_time=None):
    ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_file]

    if start_time:
        ffmpeg_cmd.extend(["-ss", start_time])

    if end_time:
        ffmpeg_cmd.extend(["-to", end_time])

    ffmpeg_cmd.extend(["-codec:a", "libmp3lame", output_file])
    try:

        subprocess.run(ffmpeg_cmd, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg returned an error:\n{e.stderr.decode('utf-8')}")
        raise e

def compress_wav_to_mp3(input_file, output_file, bitrate="128k"):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-codec:a", "libmp3lame",
        "-b:a", bitrate,
        output_file
    ]
    subprocess.run(cmd, check=True)