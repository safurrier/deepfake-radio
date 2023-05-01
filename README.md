
![image info](radio.png)
# Deepfake Radio

Code for using Elevenlabs voice cloning for fun with friends

### Discord Bot

 * `/speak`

    * Choose a voice, provide text and receive an audio clip in a message (embeds natively on Desktop but on mobile may need an app like VLC to open)

 * `/conversation`

    * Provide a script in the format `---Voice Name: hi how are you? --Voice Name: Pretty good!` and have the bot generate audio and splice it together into a conversation

### Tools for processing and uploading audio samples for voice cloning

  * Config for specifying

    * Source (local or YouTube URL)

    * Audio start and end time

    * Voice isolation using an open source ML model ([Demucs](https://github.com/facebookresearch/demucs))

    * Set clip sizes to automatically clip into smaller parts

## Bot Setup

1) Clone this repo
> git clone https://github.com/safurrier/deepfake-radio/

2) Set up the bot

  * Visit the [Discord Developer portal](https://discord.com/developers/applications) to creata new bot application

  * In the top right, select `New Application` and give the app a name

  * If you want to update the bot avatar, description etc do so here

  * On the left, click `Bot`

  * Scroll down to find the section `MESSAGE CONTENT INTENT` and turn this on. Save Changes.

  * Scroll back up and click `Reset Token`. Make sure to copy this information down as you'll need it to run your bot

  * Create a file in the top level directory called `.env`. You can do this by making a copy of the file `example.env`

  * In the `.env` file, set `BOT_TOKEN=$YOUR_TOKEN` on a line. E.g. `BOT_TOKEN=WWKDEQX8JOoxW61WPb6dXIzklNjaMHJf2zuHGk`

2) Join [ElevenLabs](https://beta.elevenlabs.io/speech-synthesis) and sign up for an account with API access

3) Copy your ElevenLabs API token (Top Right -> Profile -> API Key Section) to the `.env` file under `ELEVEN_API_KEY` like `ELEVEN_API_KEY=asdfaskjd123498sasw`

4) Create some voice clones using ElevenLabs.
  * See section **Add Custom Voices** for how to do this programtically, or clone them on the ElevenLabs platform

  * This is a [good short guide](https://github.com/elevenlabs/discord-bot/blob/main/elevenbot.py) on some tips to creating good voice clones

  * In general, quality > quantitity. (It's possible Elevenlabs doesn't use anything longer than 2 minutes for samples)

  * Diversity of voice samples and short clips can help

  * Consider adding many short clips and on the web UI editing the voice clones to select only the best ones

  * The best samples are of a clear voice with no interruptions or background noise (like a monologue or audio book).


5) Get a python environment
  * This was written with a python 3.11 environment but may work with other major versions

  * I would suggest using Conda as an environment manager as it's fairly simple to use

  * Installing conda is outside of the scope of this tutorial (some [instructions here](https://docs.conda.io/en/latest/miniconda.html)), but if it's already installed you can run the make command to get a python env setup

  > conda create --name deepfake_radio python=3.11 -y

  or using the make command `make create-conda-env`

  And then activate the env

  > conda activate deepfake_radio


6) Install the dependencies
  > make requirements
  or manually run:
  ```
	pip install -r requirements.txt
	chmod +x install_dependencies.sh
	sh install_dependencies.sh
  ```

6) Run the bot

  > python main.py

  * Depoying as an app on Railway

    * Go to [Railway](https://railway.app/verify)

    * Sign up using Github

    * Verify your account

    * Create a new project

    * Deploy from a Github Repo -> select the repo you've cloned this to

    * Add Variables -> Add the env variables for `BOT_TOKEN` and `ELEVEN_API_KEY` (optionally set `UPLOAD_VOICES` if you want to upload voices before startup. *Do not set `PROCESS_VOICES`* as it breaks the Runway deployment as of now)


7) Invite the bot to your server

  * Return to the [Discord Developer portal](https://discord.com/developers/applications)

  * Select `OAuth 2` -> URL Generator

  * Under Scopes, select `bot`

  * Under Bot Permissions select at least `Send Messages`, `Send Messages in Threads`, `Embed Links`, `Attach Links`, and `Use Slash Commands`

  * Copy the generated URL underneath (you may want to save this link somewhere if you plan on inviting the bot to multiple servers)

  * Select the server that you're a modmin on and add it to server. Authorize the bot.

8) Use the bot! Use the `/speak` command to select a voice add text and generate audio. If no voices are present in the options, try running `/update-voices` first. Have fun!


## Add Custom Voices

1) You will need audio samples to create voice clones in ElevenLabs. You can do this through the platform, or alternatively there are automated tools to do so included here. By default, the bot will process and upload custom voices to the ElevenLabs API before startup. Previously added voices are skipped.

*There may or may not be a `voice catalog` branch with many voice samples already set up. All you would have to do is copy over the voices you'd like to into the `voices` directory and turn on env variable `UPLOAD_VOICES`. You didn't hear it from me.*

2) All voice clones belong in the `voices` directory and require a `config.yaml` file. The two accepted sources for samples are a local mp3 file and a Youtube video link

3) Each config file requires a `name`, an optional `description` and at minimum, a specified `source` and `location` setting.

4) There is an example config under `voices/example`:

```yaml
name: Joe Biden
description: President Joe Biden

1:
  source:
    location: input/biden.mp3
    type: file
2:
  source:
    location: https://www.youtube.com/watch?v=KADpsS8fbg8
    type: youtube
    # Note: start_time and end_time are optional
    # but must be in format "HH:MM:SS"
    start_time: "00:00:01"
    end_time: "00:10:01"
  isolate: True
  clip_size: 60
```

  Each number is a separate source, location is a URL for Youtube and filepath for file (relative to the config file). In general this should be `input/your_sample.mp3`

  There are other optional configurations to facilitate creating good samples including start and end time, voice isolation and clip size.

  The voice isolation uses an open source model demucs for voice isolation. This can be helpful if there is background noise, but does not always work well. It will also increase the processing time substantially.

5) Make sure in the .env file `PROCESS_VOICES` and `UPLOAD_VOICES` is set to a value. Remove this env var if you don't want custom voices to be processed, and uploaded on bot startup.

6) NOTE: Remove the example voice otherwise it will be uploaded as a voice clone to your ElevenLabs account

7) Run the bot with env vars set for `PROCESS_VOICES` (if adding new custom voices that need processing) and/or `UPLOAD_VOICES` (if processed files present and no processing needed, just set this to upload to ElevenLabs)

8) If you're looking for voice clone samples, there may or may not be a branch on this repo with available files.

## Future Improvements and TODOs

[] Add CLI tool for processing + uploading voices

[] Add tag support for voice config

[] Improve voice selection option to sort by tags

[] Have the bot set the API key using a command

[] Add tests

## TODO: Tests

Where we're going, we don't need tests. If the bot breaks on your server and your friends complain tell them to kick rocks or fix it themselves.

Original inspiration of the speak command from [ElevenLabsBot](https://github.com/elevenlabs/discord-bot)
