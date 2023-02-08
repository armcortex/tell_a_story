from utils import start_process, read_yaml
from story import run_gen_story
from discordbot import client as discordbot_client


if __name__ == '__main__':
    # Discord Process
    cf = read_yaml('config.yaml')
    p1 = start_process(discordbot_client.run, args=(cf['discord']['token'], ))

    # Story Process
    p2 = start_process(run_gen_story)

    # Run Processes
    p1.join()
    p2.join()
