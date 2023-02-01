import re
import yaml
import openai
import datetime

from utils import logging


class CHATGPT:
    def __init__(self):
        # Get API key
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
    # query_steps = f'tell me about {query_story} full story step by step to the end, with number list'
    query_steps = f'list {query_story} full story step by step to the end, each step with only one sentence and with number count'

    bot = CHATGPT()
    styles, _ = bot.query(query_style, mode='keyword')
    # print(f'{styles=}')
    steps, steps_raw = bot.query(query_steps, mode='sentence')

    for i, s in enumerate(steps):
        print(f'{i=}, {s=}')


    now = datetime.datetime.now()
    now = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f'./output/{now}.txt'
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


    pass

# i=0, s=' Once upon a time, there was a sweet little girl who was called Little Red Cap'
# i=1, s=' She had a cap of red velvet which her grandmother had given her'
# i=2, s=' One day Little Red Cap\'s mother said to her: "Come Little Red Cap, here is a piece of cake and a bottle of wine; take them to your grandmother, she is ill and weak, and they will do her good'
# i=3, s=" So Little Red Cap put the cake and wine into a basket and set out on her way to her grandmother's house"
# i=4, s=' As she was walking through the forest, she met a big bad wolf'
# i=5, s=' He asked Little Red Cap where she was going, and she'


if __name__ == '__main__':
    main()

    # s = f"\n\n1. Little Red Cap is a folktale about a young girl who goes to visit her sick grandmother. \n\n2. On her way, she meets a cunning wolf who tricks her into telling him where she is going and what she is carrying in her basket. \n\n3. He then devises a plan to get her to his home first, so he can eat her. \n\n4. Little Red Cap is warned by her mother not to talk to strangers, however, she finds the wolf's pleasant demeanor inviting and talks to him anyway. \n\n5. The Wolf argues with her to take a shortcut through the woods, which she agrees to. \n\n6. Once they arrive at the Wolf."
    # # ans = re.findall(r'\d+\.\s.', s)
    # sentences = re.findall(r'\d+\.([^\.]+)', s)
    # # sentences = re.findall(r'\d+\.().', s)

    # s = '\n\n1. Once upon a time, there was a young girl who went by the name of Little Red Cap.\n2. She wore a red cap and she went to visit her grandmother who lived in the nearby woods. \n3. On her way there, she met a wolf who wanted to eat her. \n4. He tricked her into telling him where her grandmother lived and what she was wearing.\n5. The wolf then ran ahead of the Little Red Cap and arrived at her grandmother’s house first.\n6. He had disguised himself as the grandmother and was waiting in bed for the little girl.\n7. When Little Red Cap entered, she noticed something strange about her grandmother, but she couldn'
    # ans = re.findall(r'\d+[.:]([^\.]+)', s)
    #
    # pass