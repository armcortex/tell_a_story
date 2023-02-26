# Tell a Story

Automatic create stories with ChatGPT + Midjourney + FFmpeg

## Steps
1. Using ChatGPT to create story content and story image style
2. Get the ChatGPT results as Midjourney prompt to generate images
3. FFmpeg convert images into videos

## Features
- [check_point.py](./tell_a_story/check_point.py) will save the process step, if process failed system will restart and `check_point.py` will restore last step and continue
- [discordbot.py](./tell_a_story/discordbot.py) will report program status

## Setup
- [config_template.yaml](./tell_a_story/config_template.yaml) Setup your configs
  - OpenAI API
  - Discord Token
  - Midjourney Bot Token
  - Midjourney Bot Session ID
  - Midjourney Bot Channel ID
- [story_settings_template.yaml](./tell_a_story/story_settings_template.yaml) Setup story series you want to tell and topics

## Usage
- Rename `config_template.yaml` to `config.yaml`
- Rename `story_settings_template.yaml` to `story_settings.yaml`
- Install `pipenv install`
- Run `pipenv run python main.py`