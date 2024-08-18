import disnake, datetime
from disnake.ext import commands
from database.LogsDatabase import LogsDatabase
from database.Welcome_Channel import WelcomeChannel
from database.AutoroleDB import AutoRoleDanabase

class GuildPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_db = LogsDatabase()
        self.welcome_db = WelcomeChannel()
        self.autorole_db = AutoRoleDanabase()
        
    @commands.slash_command(name="info_guild", description="Информация гильдии")
    async def info_guild(self, interaction: disnake.ApplicationCommandInteraction):
        guild = interaction.guild
        
        logs = guild.get_channel(await self.logs_db.get_log_channel(guild))
        
        welcome = await self.welcome_db.get_welcome_channel(guild)
        
        autorole = await self.autorole_db.get_autorole(guild)
        
        member = guild.member_count
        
        owner = guild.owner
        if not welcome:
            welcome = "Не установлен"
        if not logs:
            logs = "Не установлен"
        autorole_name = autorole.name if autorole else "Не установлена"
        embed = disnake.Embed(
            title=f"Информация о гильдии {guild.name}",
            description=f"**ID гильдии: `{guild.id}`**",
            color=disnake.Color.old_blurple()
        )
        embed.add_field(name="Владелец", value=f"`{owner}`")
        embed.add_field(name="Канал логирования", value=f"`{logs}`")
        embed.add_field(name="Канал приветсвия", value=f"`{welcome}`")
        embed.add_field(name="Роль автовыдачи", value=f"`{autorole_name}`")
        embed.add_field(name="Количество участников", value=f"`{member}`")
        embed.add_field(name="Создана", value=f"`{guild.created_at.strftime('%d.%m.%Y %H:%M:%S')}`")
        
        logo_guild = guild.icon
        if not logo_guild:
            embed.set_thumbnail(url=None)
        else:
            embed.set_thumbnail(url=logo_guild)
        
        embed.timestamp = datetime.datetime.now()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(GuildPanel(bot))