import discord
from discord import app_commands
from discord.ext import commands, tasks

import time

from utils.config_manager import (
    load_configs,
    save_configs
)

class AvatarScheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.avatar_loop.start()
       
    def cog_unload(self):
        self.avatar_loop.cancel()

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="agendar_avatar",
        description="Agenda o envio automático de um avatar"
    )
    async def agendar_avatar(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        canal: discord.TextChannel,
        intervalo: app_commands.Range[int, 1, 10080]
    ):
        configs = load_configs()
        
        configs[str(interaction.guild.id)] = {
            "member_id": usuario.id,
            "channel_id": canal.id,
            "interval_minutes": intervalo,
            "last_sent": 0
        }
        
        save_configs(configs)
        
        await interaction.response.send_message(
            f"Avatar de {usuario.mention} será enviado em {canal.mention} a cada {intervalo} minuto(s).",
            allowed_mentions=discord.AllowedMentions.none()
        )
    
    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="avatar_agendado_status",
        description="Mostra a configuração atual do envio automático."
    )
    
    async def status(
        self,
        interaction: discord.Interaction
    ):
        configs = load_configs()

        config = configs.get(
            str(interaction.guild.id)
        )

        if not config:
            return await interaction.response.send_message(
                "Nenhuma configuração encontrada.",
                ephemeral=True
            )

        membro = interaction.guild.get_member(
            config["member_id"]
        )

        canal = interaction.guild.get_channel(
            config["channel_id"]
        )
        
        agora = int(time.time())
        
        intervalo_segundos = config["interval_minutes"] * 60
        proximo_envio = config["last_sent"] + intervalo_segundos
        restante = max(0, proximo_envio - agora)
        minutos = restante // 60
        segundos = restante % 60

        await interaction.response.send_message(
            f"""
Usuário: {membro.mention if membro else 'Não encontrado'}
Canal: {canal.mention if canal else 'Não encontrado'}
Intervalo: {config['interval_minutes']} minuto(s)
Próximo envio em: {minutos}m {segundos}s
""",
            allowed_mentions=discord.AllowedMentions.none()
        )
    
    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="avatar_agendado_remover",
        description="Remove a configuração de envio automático."
    )
    async def remover(
        self,
        interaction: discord.Interaction
    ):
        configs = load_configs()

        if str(interaction.guild.id) in configs:
            del configs[str(interaction.guild.id)]

            save_configs(configs)

        await interaction.response.send_message(
            "Configuração removida."
        )

    @tasks.loop(seconds=30)
    async def avatar_loop(self):
        configs = load_configs()

        now = int(time.time())

        for guild_id, config in configs.items():

            intervalo = config["interval_minutes"] * 60

            if now - config["last_sent"] < intervalo:
                continue

            guild = self.bot.get_guild(
                int(guild_id)
            )

            if guild is None:
                continue

            canal = guild.get_channel(
                config["channel_id"]
            )

            membro = guild.get_member(
                config["member_id"]
            )

            if canal is None or membro is None:
                continue

            embed = discord.Embed(
                title=f"Avatar de {membro}"
            )

            embed.set_image(
                url=membro.display_avatar.url
            )

            await canal.send(embed=embed)

            config["last_sent"] = now

        save_configs(configs)

    @avatar_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(
        AvatarScheduler(bot)
    )