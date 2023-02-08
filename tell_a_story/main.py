from utils import start_process, read_yaml
from story import run_gen_story
from discordbot import run_discord_bot_client

if __name__ == '__main__':
    # Discord Process
    cf = read_yaml('config.yaml')
    p1 = start_process(run_discord_bot_client)

    # Story Process
    p2 = start_process(run_gen_story)

    # Run Processes
    p1.join()
    p2.join()
