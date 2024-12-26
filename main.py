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

        # check if exiftool is in path
        exif_path = ""
        try:
            await asyncio.create_subprocess_exec("exiftool", "--version")
        except FileNotFoundError:
            exif_path = "/opt/exiftool/"

        proc = await asyncio.create_subprocess_exec(
            f"{exif_path}exiftool",
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
                # Download the raw image
                raw_data = await attachment.read()

                # Check the file type using exiftool
                if str(await run_exiftool(raw_data)).strip().lower() in ["jpeg", "jpg"]:
                    # rename the file to jpg
                    converted_file = discord.File(io.BytesIO(raw_data), "{attachment.filename.split('.')[0]}.jpg")
                    await message.reply(
                        content="",
                        file=converted_file,
                    )
                    return

                # Process the raw image using rawpy
                with rawpy.imread(io.BytesIO(raw_data)) as raw:
                    rgb_image = raw.postprocess(use_camera_wb=True)

                # Convert the raw image to JPG using Pillow
                image = Image.fromarray(rgb_image)
                with io.BytesIO() as output:
                    image.save(output, format="JPEG")
                    output.seek(0)

                    # Create a discord.File object
                    converted_file = discord.File(
                        output, filename=f"{attachment.filename.split('.')[0]}.jpg"
                    )

                    # Send the converted file
                    await message.reply(
                        content=f"",
                        file=converted_file,
                    )

            except Exception as e:
                await message.reply(
                    f"Failed to process {attachment.filename}:\n"
                    f"Error: {e}\n"
                    f"Error Type: {type(e).__name__}"
                )


# Run the bot
bot.run(BOT_TOKEN)
