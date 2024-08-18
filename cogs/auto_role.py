import disnake

from disnake.ext import commands
from database.AutoroleDB import AutoRoleDanabase
from database.LogsDatabase import LogsDatabase


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_role = AutoRoleDanabase()
        self.logs = LogsDatabase()
        
    @commands.slash_command(name="set_autorole", description="Установить роль для автовыдачи")
    @commands.has_permissions(administrator=True)
    async def setautorole(self, interaction, role: disnake.Role):
        await self.auto_role.add_autorole(interaction.guild, role)
        await interaction.send(f"### В качестве автороли была установлена {role.mention}", ephemeral=True)
        log = await self.logs.get_log_channel(interaction.guild)
        if not log:
            await interaction.send(f"### В гильдии не установлен канал логирования. Используйте  - `/sel_log`", ephemeral=True)
        else:
            channel = interaction.guild.get_channel(log)  # Вставить ID канала куда будут отправляться заявки
            await channel.send(f"### Администратор {interaction.author.mention} установил {role.mention} в качестве роли для автовыдачи")
    
    @commands.slash_command(name="remove_autorole", description="Удалить роль для автовыдачи")
    @commands.has_permissions(administrator=True)
    async def removeautorole(self, interaction):
        await self.auto_role.remove_autorole(interaction.guild)
        await interaction.send(f"### Вы удалили автороль", ephemeral=True)
        log = await self.logs.get_log_channel(interaction.guild)
        if not log:
            await interaction.send(f"### В гильдии не установлен канал логирования. Используйте  - `/sel_log`", ephemeral=True)
        else:
            channel = interaction.guild.get_channel(log)  # Вставить ID канала куда будут отправляться заявки
            await channel.send(f"### Администратор {interaction.author.mention} удалил роль для автовыдачи")
            
    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        guild = member.guild
        role = await self.auto_role.get_autorole(guild)
        if role:
            await member.add_roles(role)
        

def setup(bot):
    bot.add_cog(AutoRole(bot))       