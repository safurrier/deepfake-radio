import asyncio
import datetime
import requests
import random
import os
import json
import logging

import hikari
import lightbulb
import miru

from itertools import islice
from typing import Dict
from dotenv import load_dotenv
from deepfake_radio.api import fetch_voices
from pydub import AudioSegment
import tempfile
import json


logger = logging.getLogger(__name__)
load_dotenv()

bot = lightbulb.BotApp(os.environ.get('BOT_TOKEN'))
miru.install(bot)
@bot.listen(hikari.StartedEvent)
async def on_ready(event):
    print("Ready!")



def read_voices():
    if os.path.exists("voices.json"):
        with open("voices.json", "r") as json_file:
            voices = json.load(json_file)
        return voices
    else:
        return fetch_voices()


@bot.command
@lightbulb.command("update_voices", "Update the voices available to the bot. Defaults to all cloned voices.")
@lightbulb.implements(lightbulb.SlashCommand)
async def update_voices(ctx: lightbulb.context.Context):
   # Get available voices and save them to a JSON file
    with open("voices.json", "w") as json_file:
        json.dump(fetch_voices(), json_file)

    await ctx.respond('🔄 Updated voices!')

@bot.command
@lightbulb.option("text", "Text to use the TTS. Max is 1000.", required=True)
@lightbulb.option("voices", "Voices to utilize", choices=list(read_voices().keys()), required=True)
@lightbulb.option("title", "Voices to utilize", required=False)
@lightbulb.command("speak", "Create an audio file voiced by you know who")
@lightbulb.implements(lightbulb.SlashCommand)
async def speak(ctx: lightbulb.context.Context):
    VOICES = read_voices()
    api_key = os.environ.get('ELEVEN_API_KEY')

    if not api_key:
        await ctx.respond("ERROR: No API key provided! Please provide an API key in the .env file.")
        return

    text = ctx.options.text
    voice_id = VOICES[ctx.options.voices]

    if len(text) > 1000:
        await ctx.respond(f"WARNING: Text is over 1000 characters! Please try a sentence less than 1000 characters.\nTranscript: ||{text}||")
    else:
        await ctx.respond(f"Sending request... ⏰\nTranscript: ||{text}||")
        headers = {
            'accept': 'audio/mpeg',
            'xi-api-key': api_key,
            'Content-Type': 'application/json'
        }
        payload = {"text": text}

        if ctx.options.use_stream:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        else:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 400:
            await ctx.edit_last_response("ERROR: Entered voice ID does not exist! Did you enter the ID correctly?")
        else:
            if ctx.options.title:
                audio_filename = f"audio-{ctx.options.voices}-{ctx.options.title}.mp3"
            else:
              audio_filename = f"audio-{ctx.options.voices}-{random.randint(1, 372855)}.mp3"
            with open(audio_filename, 'wb') as output_file:
                output_file.write(response.content)

            hikari_file = hikari.File(audio_filename)
            await ctx.respond(hikari_file)
            os.remove(audio_filename)

    return

async def generate_audio(text, voice_id, pause_duration=250):
    api_key = os.environ.get('ELEVEN_API_KEY')
    if not api_key:
        raise Exception("ERROR: No API key provided! Please provide an API key in the .env file.")

    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    payload = {"text": text}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 400:
        raise Exception("ERROR: Entered voice ID does not exist! Did you enter the ID correctly?")

    # Save the response content to a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3')
    temp_file.write(response.content)
    temp_file.seek(0)
    # Convert the mp3 file to wav and add the pause duration
    audio_segment = AudioSegment.from_file(temp_file, format='mp3')
    audio_segment += AudioSegment.silent(duration=pause_duration)

    return audio_segment

@bot.command
@lightbulb.option("text", "Text to use the TTS. Max is 1000.", required=True)
@lightbulb.option("delimiter", "Delimiter used to separate voices", required=False, default="---")
@lightbulb.option("pause_length", "Pause time in seconds to put between each speaker", required=False, default=.25)
@lightbulb.option("title", "Voices to utilize", required=False)
@lightbulb.command("conversation", "Use voices in a convo. Use the format 'Voice Name: script ---' (the delimiter) to separate voices.")
@lightbulb.implements(lightbulb.SlashCommand)
async def conversation(ctx: lightbulb.context.Context):
    VOICES = read_voices()
    text = ctx.options.text
    delimiter = ctx.options.delimiter

    if len(text) > 1000:
        await ctx.respond(f"WARNING: Text is over 1000 characters! Please try a sentence less than 1000 characters.\nTranscript: {text}")
        return
    # Defer the response to have more time for processing
    await ctx.respond("Processing your request...")

    # Parse text, call generate_audio for each voice, and combine the resulting AudioSegments
    combined_audio = AudioSegment.empty()

    # Split the text into sections using the delimiter
    sections = text.split(delimiter)
    if not sections[0].strip():  # If the first section is empty, remove it
        sections.pop(0)

    for section in sections:
        colon_index = section.find(':')
        if colon_index != -1:
            voice_key = section[:colon_index].strip()
            voice_text = section[colon_index + 1:].strip()
            if voice_key in VOICES:
                voice_id = VOICES[voice_key]
                try:
                    audio_segment = await generate_audio(voice_text, voice_id, pause_duration=ctx.options.pause_length*1000) # Convert from seconds to milliseconds
                    combined_audio += audio_segment
                except Exception as e:
                    await ctx.respond(str(e))
                    return
            else:
                await ctx.respond(f"ERROR: Invalid voice key '{voice_key}'. Please use a valid voice.")
                return
        else:
            await ctx.respond(f"ERROR: Incorrect formatting of the text. Please use 'voice: text' format and separate speakers with the delimiter '{delimiter}'.")
            return

    # Save the combined audio to an mp3 file
    if ctx.options.title:
        audio_filename = f"audio-converse-{ctx.options.title}.mp3"
    else:
        audio_filename = f"audio-converse-{random.randint(1, 372855)}.mp3"

    combined_audio.export(audio_filename, format='mp3')
    hikari_file = hikari.File(audio_filename)
    await ctx.respond(hikari_file)
    os.remove(audio_filename)

    return

@bot.command
@lightbulb.command("user_info", "Gets more info about character count, sub tier, etc")
@lightbulb.implements(lightbulb.SlashCommand)
async def user_info(ctx: lightbulb.context.Context):
    if not os.environ.get('ELEVEN_API_KEY'):
        await ctx.respond("ERROR: No API key provided! Please provide an API key in the .env file.")
        return
    else:
        site = "https://api.elevenlabs.io/v1/user"
        headers = {
                'accept': 'application/json',
                'xi-api-key': os.environ.get('ELEVEN_API_KEY')
            }
        await ctx.respond("Getting user info... ⏰")
        r = requests.get(site, headers=headers)
        await ctx.edit_last_response(f"User info for user {ctx.user.username}:\n\nSubscription: {r.json()['subscription']['tier']}\nCharacter count: {r.json()['subscription']['character_count']}\nCharacter limit: {r.json()['subscription']['character_limit']}\nCan user extend character limit? {r.json()['subscription']['can_extend_character_limit']}\nIs user allowed to extend character limit? {r.json()['subscription']['allowed_to_extend_character_limit']}\nTime until next character reset (in datetime format): {datetime.datetime.fromtimestamp(int(r.json()['subscription']['next_character_count_reset_unix'])).strftime('%m-%d-%Y %H:%M:%S')}\nVoice limit: {r.json()['subscription']['voice_limit']}\nCan user extend voice limit? {r.json()['subscription']['can_extend_voice_limit']}\nCan user use instant voice cloning? {r.json()['subscription']['can_use_instant_voice_cloning']}\nIs user a new user? {r.json()['is_new_user']}")


@lightbulb.command(name="ping", description="Gets the bot's ping.")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping_command(ctx: lightbulb.context.Context):
    latency = round(ctx.bot.heartbeat_latency * 1000, 2)
    response_message = f"🏓 Ping: {latency}ms"

    await ctx.respond(response_message)
