import discord
from discord.ext import commands
import rawpy
from PIL import Image
import io
import os
import dotenv

dotenv.load_dotenv()
BOT_TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = False
# intents.attachments = True

bot = commands.Bot(command_prefix=os.environ["PREFIX"], intents=intents)


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

                # Process the raw image using rawpy
                with rawpy.imread(io.BytesIO(raw_data)) as raw:
                    rgb_image = raw.postprocess()

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
                await message.channel.send(
                    f"Failed to process {attachment.filename}: {e}"
                )


# Run the bot
bot.run(BOT_TOKEN)
