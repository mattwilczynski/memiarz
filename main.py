import os
import random
import discord
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import asyncio

# Google Drive setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1IhV5EPPFKXjUbMTHJDsFzFjN8V04gWWz'

credentials = Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

with open('token.txt', 'r') as file:
    # Read the first line from the file and strip any extra spaces or newline characters
    token_file = file.readline().strip()

# Discord bot setup
TOKEN = token_file
CHANNEL_ID = '1201635452755660932'  # Replace with your channel ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


def get_random_image():
    """Fetch a random image from the Google Drive folder."""
    query = f"'{FOLDER_ID}' in parents and mimeType contains 'image/'"
    results = drive_service.files().list(q=query).execute()
    files = results.get('files', [])
    if not files:
        return None

    random_file = random.choice(files)
    request = drive_service.files().get_media(fileId=random_file['id'])
    file_path = f"temp/{random_file['name']}"

    os.makedirs("temp", exist_ok=True)
    with open(file_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

    return file_path


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    post_daily_image.start()


@bot.command()
async def daj_mema(ctx):
    """Command to post a random image."""
    file_path = get_random_image()
    if file_path:
        await ctx.channel.send(file=discord.File(file_path))
        os.remove(file_path)
    else:
        await ctx.channel.send("No images found in the folder.")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")

@tasks.loop(hours=24)
async def post_daily_image():
    """Post an image once a day."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        file_path = get_random_image()
        if file_path:
            await channel.send(file=discord.File(file_path))
            os.remove(file_path)
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Commands: {bot.commands}")

bot.run(TOKEN)
