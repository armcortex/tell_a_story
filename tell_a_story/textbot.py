import re
import yaml
import openai

from utils import logging, current_time


class CHATGPT:
    def __init__(self):
        with open('config.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.CLoader)
        openai.api_key = config['openai']['api_key']

    @staticmethod
    def _filter_keyword(s: str) -> list:
        return re.findall(r'\d+\.\s(\w+)', s)

    @staticmethod
    def _filter_sentence(s:str) -> list:
        return re.findall(r'\d+[.:]([^\.]+)', s)

    def query(self, prompt, mode: str='keyword'):
        logging.info('Start')

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )
        ans = response['choices'][0]['text']

        if 'keyword' in mode:
            return self._filter_keyword(ans), ans
        elif 'sentence' in mode:
            return self._filter_sentence(ans), ans
        else:
            raise ValueError('Mode should be keyword or sentence')


def main():
    query_story = f'Little Red Cap'
    query_style = f'please say English, and please list 10 style key word of Grimms Märchen story {query_story}. Make sure all style word have diversity'
    query_steps = f'list {query_story} full story step by step to the end, each step with only one sentence and with number count'

    bot = CHATGPT()
    styles, _ = bot.query(query_style, mode='keyword')
    print(f'{styles=}')

    steps, steps_raw = bot.query(query_steps, mode='sentence')
    for i, s in enumerate(steps):
        print(f'{i=}, {s=}')


if __name__ == '__main__':
    main()
