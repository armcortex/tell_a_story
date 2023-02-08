import datetime
import discord

from utils import read_yaml, start_process

cf = read_yaml('config.yaml')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


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
    p = start_process(client.run, args=(cf['discord']['token'], ))
    p.join()


if __name__ == '__main__':
    run_discord_bot_client()
    # client.run(cf['discord']['token'])


# class DiscordBot:
#     def __init__(self, filename):
#         with open(filename, 'r') as f:
#             self.cf = yaml.load(f, Loader=yaml.CLoader)
#
#         intents = discord.Intents.default()
#         intents.message_content = True
#         self.client = discord.Client(intents=intents)
#
#         self.fetch_id()
#
#     @staticmethod
#     def get_current_time():
#         return datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S.%f")[:-3]
#
#     async def fetch_id(self):
#         self.user = await self.client.fetch_user(int(self.cf['discord']['my_id']))
#         self.channel = await self.client.fetch_channel(int(self.cf['discord']['bot_message_id']))
#
#     def send_dm_user(self):
#         self.user.send(f'{self.get_current_time()}: Hello there! Y')
#
#     def send_dm_channel(self):
#         self.user.send(f'{self.get_current_time()}: Hello there! Y')
#
#     # @self.client.event
#     # async def on_ready(self):
#     #     print(f'Logged User as {client.user}')
#     #     await send_dm_user()
#     #     await send_dm_channel()
#
#     def run(self):
#         self.client.run(self.cf['discord']['token'])
#
#
# if __name__ == '__main__':
#     bot = DiscordBot('config.yaml')
#
#     bot_process = Process(target=bot.run)
#     bot_process.start()
#
#     bot.send_dm_user()
#     bot.send_dm_channel()
#
