import discord
from discord.ext import commands
from discord import app_commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="avatar",
        description="Mostra o avatar de alguém"
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        usuario: discord.User = None
    ):
        usuario = usuario or interaction.user

        embed = discord.Embed(
            title=f"Avatar de {usuario.name}"
        )
        embed.set_image(url=usuario.display_avatar.url)

        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(
        name="hidden_avatar",
        description="Mostra o avatar sem exibir quem pediu"
    )
    async def hidden_avatar(
        self,
        interaction: discord.Interaction,
        usuario: discord.User = None
    ):
        usuario = usuario or interaction.user

        embed = discord.Embed(
            title=f"Avatar de {usuario.name}"
        )
        embed.set_image(url=usuario.display_avatar.url)
        
        try:
            await interaction.channel.send(embed=embed)
            
            await interaction.response.send_message(
                "Avatar enviado!",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "Não tenho permissão para enviar mensagens aqui...",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Avatar(bot))