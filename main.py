import discord
from discord.ext import commands
import logging
import asyncio

from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
# Configure root logger so logs appear both in file and stdout (Railway logs)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
# Avoid adding duplicate handlers if module reloaded
if not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
    root_logger.addHandler(file_handler)
if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
    root_logger.addHandler(stream_handler)

class Otimous(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        try:
            await self.load_extension("cogs.avatar")
            
            await self.load_extension("cogs.scheduler")

            synced = await self.tree.sync()

            print("Comandos registrados:")
            for cmd in self.tree.get_commands():
                print(f"- {cmd.name}")

            print(f"{len(synced)} comandos sincronizados")

        except Exception as e:
            print(e)

bot = Otimous()
bot.run(TOKEN, log_level=logging.DEBUG)