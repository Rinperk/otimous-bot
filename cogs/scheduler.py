import discord
from discord import app_commands
from discord.ext import commands, tasks

import time

from utils.database import (
    save_config,
    get_config,
    get_all_configs,
    update_last_sent,
    remove_config,
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
        # Persist using SQLite helper
        save_config(
            interaction.guild.id,
            usuario.id,
            canal.id,
            intervalo
        )

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
        row = get_config(interaction.guild.id)

        if not row:
            return await interaction.response.send_message(
                "Nenhuma configuração encontrada.",
                ephemeral=True
            )

        # row: (guild_id, member_id, channel_id, interval_minutes, last_sent)
        membro = interaction.guild.get_member(row[1])
        canal = interaction.guild.get_channel(row[2])
        agora = int(time.time())

        intervalo_segundos = row[3] * 60
        proximo_envio = row[4] + intervalo_segundos
        restante = max(0, proximo_envio - agora)
        minutos = restante // 60
        segundos = restante % 60

        await interaction.response.send_message(
            f"""
Usuário: {membro.mention if membro else 'Não encontrado'}
Canal: {canal.mention if canal else 'Não encontrado'}
Intervalo: {row[3]} minuto(s)
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
        remove_config(interaction.guild.id)

        await interaction.response.send_message(
            "Configuração removida."
        )

    @tasks.loop(seconds=30)
    async def avatar_loop(self):
        rows = get_all_configs()

        now = int(time.time())

        for row in rows:
            guild_id, member_id, channel_id, interval_minutes, last_sent = row

            intervalo = interval_minutes * 60

            if now - last_sent < intervalo:
                continue

            guild = self.bot.get_guild(guild_id)

            if guild is None:
                continue

            canal = guild.get_channel(channel_id)

            membro = guild.get_member(member_id)

            if canal is None or membro is None:
                continue

            embed = discord.Embed(
                title=f"Avatar de {membro}"
            )

            embed.set_image(
                url=membro.display_avatar.url
            )

            await canal.send(embed=embed)

            update_last_sent(guild_id, now)

    @avatar_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(
        AvatarScheduler(bot)
    )