import re
import yaml
import openai


def main():
    query_story = f'Little Red Cap'
    query_base = f'please say English, and please list 10 style key word of Grimms Märchen story {query_story}. Make sure all style word have diversity'

    # Get API key
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.CLoader)
    openai.api_key = config['api_key']

    # Link to ChatGPT
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=query_base,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    ans = response['choices'][0]['text']

    # Extract Story style keywords
    keywords = re.findall(r'\d+\.\s(\w+)', ans)
    # print(f'{keywords=}')
    for i, k in enumerate(keywords):
        print(f'{i=}, {k=}')

    pass

if __name__ == '__main__':
    main()
