import disnake
from disnake.ext import commands
from database.LogsDatabase import LogsDatabase

log_db = LogsDatabase()

class Set_LogChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command(description="Установка канала логирования")
    @commands.has_permissions(administrator=True)
    async def set_log(self, interaction: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        guild = interaction.guild
        await log_db.insert_logs_channel(interaction, channel, guild)
        await interaction.send(f"### Вы установили {channel.mention} для логирования", ephemeral=True)
        
        
    @commands.slash_command(description="Удаление канала логирования")
    @commands.has_permissions(administrator=True)
    async def remove_log_channel(self, interaction: disnake.ApplicationCommandInteraction):
        guild = interaction.guild
        await log_db.remove_log_channel(guild)
        await interaction.response.send_message("### Канал логирования удален", ephemeral=True)    
        
def setup(bot):
    bot.add_cog(Set_LogChannel(bot))