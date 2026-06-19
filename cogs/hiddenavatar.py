import discord
from discord.ext import commands
from discord import app_commands

class HiddenAvatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="hiddenavatar",
        description="Mostra o avatar sem exibir quem pediu"
    )
    async def hiddenavatar(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member = None
    ):
        usuario = usuario or interaction.user

        embed = discord.Embed(
            title=f"Avatar de {usuario.display_name}"
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
    await bot.add_cog(HiddenAvatar(bot))