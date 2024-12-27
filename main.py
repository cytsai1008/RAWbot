#!/usr/bin/env python3

import asyncio
import io
import os
import tempfile

import discord
import dotenv
import rawpy
from PIL import Image
from discord.ext import commands

dotenv.load_dotenv()
BOT_TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = False
# intents.attachments = True

bot = commands.Bot(command_prefix=os.environ["PREFIX"], intents=intents)


async def run_exiftool(byte_data):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(byte_data)
        temp_file_path = temp_file.name

        exif_path = os.environ.get("EXIFTOOL_PATH", "/opt/exiftool/")

        proc = await asyncio.create_subprocess_exec(
            os.path.join(exif_path, "exiftool"),
            "-s",
            "-T",
            "-FileType",
            temp_file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    stdout, stderr = await proc.communicate()
    os.remove(temp_file_path)
    return stdout.decode()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not message.attachments:
        return

    converted_files = []
    for attachment in message.attachments:
        if attachment.filename.lower().endswith(
            (
                "nrw",
                "nef",
                "crw",
                "cr2",
                "cr3",
                "arw",
                "raf",
                "orf",
                "rw2",
                "raw",
                "dng",
            )
        ):
            try:
                async with message.channel.typing():
                    raw_data = await attachment.read()

                    if str(await run_exiftool(raw_data)).strip().lower() in ["jpeg", "jpg"]:
                        converted_file = discord.File(io.BytesIO(raw_data), f"{attachment.filename.split('.')[0]}.jpg")
                        converted_files.append(converted_file)
                        continue

                    with rawpy.imread(io.BytesIO(raw_data)) as raw:
                        rgb_image = raw.postprocess(use_camera_wb=True)

                    image = Image.fromarray(rgb_image)
                    with io.BytesIO() as output:
                        image.save(output, format="JPEG")
                        output.seek(0)
                        converted_file = discord.File(output, filename=f"{attachment.filename.split('.')[0]}.jpg")
                    converted_files.append(converted_file)

            except Exception as e:
                await message.reply(
                    f"Failed to process {attachment.filename}:\n" f"Error: {e}\n" f"Error Type: {type(e).__name__}"
                )
                raise e

    if converted_files:
        await message.reply(content="", files=converted_files)


# Run the bot
bot.run(BOT_TOKEN)
