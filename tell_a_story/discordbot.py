import os
import glob
import datetime
import time
import asyncio
import discord

from utils import logging, read_yaml, start_process, current_time, DOWNLOAD_BASE_PATH


cf = read_yaml('config.yaml')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

SIGN_NUM = current_time()
BASE_TMP_PATH = DOWNLOAD_BASE_PATH + 'msg_data_tmp/'
write_msg_cnt = 0


def send_msg(file_path: str, msg: str):
    with open(file_path, 'w') as f:
        f.write(msg)


def read_msg(file_path: str) -> str:
    with open(file_path, 'r') as f:
        msg = f.read()

    os.remove(file_path)
    return msg


async def background_task():
    await client.wait_until_ready()
    await asyncio.sleep(5)

    cnt = 0
    while not client.is_closed():
        file_path = BASE_TMP_PATH + f'{cnt}_{SIGN_NUM}.txt'

        # Checking if any messages need to be sent
        while True:
            if os.path.exists(file_path):
                msg = read_msg(file_path)
                cnt += 1
                break
            else:
                await asyncio.sleep(1)

        await send_dm_channel(msg)
        logging.info(f'background_task(): {msg}')


def write_msg_task(msg):
    global write_msg_cnt

    file_path = BASE_TMP_PATH + f'{write_msg_cnt}_{SIGN_NUM}.txt'
    send_msg(file_path, msg)
    write_msg_cnt += 1


def write_worker():
    while True:
        write_msg_task(current_time())
        time.sleep(3)


def get_current_time():
    return datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S.%f")[:-3]


@client.event
async def on_ready():
    print(f'Logged User as {client.user}')
    await send_dm_channel('Tell Story Service is Up')


async def send_dm_user(msg: str):
    user = await client.fetch_user(int(cf['discord']['my_id']))
    await user.send(f'{get_current_time()}: {msg}')


async def send_dm_channel(msg: str):
    user = await client.fetch_channel(int(cf['discord']['bot_message_id']))
    await user.send(f'{get_current_time()}: {msg}')


def run_discord_bot_client():
    # Clean all previous data
    for f in glob.glob(BASE_TMP_PATH + '*.txt'):
        os.remove(f)

    client.loop.create_task(background_task())
    client.run(cf['discord']['token'])


if __name__ == '__main__':
    p1 = start_process(write_worker)
    p2 = start_process(run_discord_bot_client)

    p1.join()
    p2.join()
