import asyncio
import datetime
import requests
import random
import os
import logging

import hikari
import lightbulb
import miru

from itertools import islice
from typing import Dict
from dotenv import load_dotenv
from deepfake_radio.api import fetch_voices

logger = logging.getLogger(__name__)
load_dotenv()


bot = lightbulb.BotApp(os.environ.get('BOT_TOKEN'))
miru.install(bot)

@bot.listen(hikari.StartedEvent)
async def on_ready(event):
    print("Ready!")

VOICES = fetch_voices()
# This is a Lightbulb thing




@bot.command
@lightbulb.command("update_voices", "Update the voices available to the bot. Defaults to all cloned voices.")
@lightbulb.implements(lightbulb.SlashCommand)
async def update_voices(ctx: lightbulb.context.Context):
    api_key = os.environ.get('ELEVEN_API_KEY')

    if not api_key:
        await ctx.respond("ERROR: No API key provided! Please provide an API key in the .env file.")
        return

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        'accept': 'application/json',
        'xi-api-key': api_key
    }
    response = requests.get(url, headers=headers)
    await asyncio.sleep(0.50)

    global VOICES
    cloned_voices = [voice for voice in response.json()['voices'] if voice['category'] == 'cloned']
    VOICES = {voice['name']: voice['voice_id'] for voice in cloned_voices}

    # This is a Lightbulb thing
    # TODO: Improve handling of this beyond just truncating
    max_voices = 25
    if len(VOICES) > max_voices:
        warning_msg = f"More than {max_voices} custom voices detected items, some items will be excluded."
        logger.warning(warning_msg)
        await ctx.respond(f'Uh oh! More than {max_voices} custom voices detected items, some voices will be excluded 😢')
        VOICES = dict(islice(VOICES.items(), max_voices))

    await ctx.respond('🔄 Updated voices!')

@bot.command
@lightbulb.option("text", "Text to use the TTS. Max is 1000.", required=True)
@lightbulb.option("voices", "Voices to utilize", choices=list(VOICES.keys()), required=True)
@lightbulb.option("title", "Voices to utilize", required=False)
@lightbulb.command("speak", "Create an audio file voiced by you know who")
@lightbulb.implements(lightbulb.SlashCommand)
async def speak(ctx: lightbulb.context.Context):
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
