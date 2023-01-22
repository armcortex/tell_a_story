import yaml
import discord

# Get Discord Token
with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.CLoader)
discord_token = config['discord_token']


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Logged User as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == 'bot-message':
        # # Bot response in group
        await message.channel.send(f'Bot: {message.content}')

    print(f'Channel: {message.channel}, Message: {message.content}')

    # Bot response in persion
    await message.author.send(f'[Author send] {message.channel.name}: {message.content}')


def main():
    client.run(discord_token)


if __name__ == '__main__':
    main()
