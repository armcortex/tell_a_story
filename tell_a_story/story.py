import yaml
import time
import datetime

from utils import logging
from textbot import CHATGPT
from photobot import PhotoBot


def prompt_log(styles, steps, steps_raw):
    now = datetime.datetime.now()
    now = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f'./output/{now}_prompts_log.txt'
    with open(filename, 'w') as f:
        # All
        f.write('All: \n')
        f.write(f'{", ".join(styles)}, ')
        f.write(str(steps[0]))
        f.write('\n\n')

        # Styles
        f.write('Sytles: \n')
        f.write(', '.join(styles))
        f.write('\n\n')

        # Steps
        f.write('Steps:\n')
        for i, s in enumerate(steps):
            f.write(f'{i}. {str(s)}\n')
        f.write('\n\n')

        # Raw Steps
        f.write('Raw Steps: \n')
        f.write(steps_raw)


def open_settings(filename: str):
    with open(filename, 'r') as f:
        cf = yaml.load(f, Loader=yaml.CLoader)

    return cf


if __name__ == '__main__':
    # parameter settings
    story_filename = 'story_settings.yaml'
    story_cf = open_settings(story_filename)

    photobot_filename = 'config.yaml'

    # parameter settings
    story_topic = story_cf['topics'][25]
    story_style = f'please say English, and please list 10 style key word of Grimms Märchen story {story_topic}. Make sure all style word have diversity'
    story_steps = f'list {story_topic} full story step by step to the end with 10 steps, each step with only one sentence and with number count'

    # Generate Story guideline and style
    chatbot = CHATGPT()
    styles, _ = chatbot.query(story_style, mode='keyword')
    steps, steps_raw = chatbot.query(story_steps, mode='sentence')

    prompt_log(styles, steps, steps_raw)

    # Generate Images
    photobot = PhotoBot(photobot_filename)

    for i, step in enumerate(steps):
        prompts = step + ', ' + ', '.join(styles)
        _ = photobot.gen_photo(prompts)
        photobot.wait_event()
        _ = photobot.get_msg_id(prompts)

        for idx in range(4):
            _ = photobot.upscale(idx)
            photobot.wait_event()
            _ = photobot.get_msg_id(prompts)

            photobot.download_image(0, prefix=f'{i+1}_{idx+1}-{story_topic}')
