import disnake
import datetime
from disnake.ext import commands


class ButtonAdminHelp(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @disnake.ui.button(label="Назад", style=disnake.ButtonStyle.gray)
    async def btBack(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            await interaction.response.defer()

            view = ButtonHelp()
            
            embed = disnake.Embed(
                title="Основные команды бота",
                description=f"**`/profile` - Карточка пользователя**\n"
                "**`/promocode_details` - Получить детали промокода**\n"
                "**`/use_promocode` - Использовать промокод**\n"
                "**`/list_promocodes` - Показать все промокоды**\n"
                "**`/admin_list` - Список администраторов**\n",
                color=disnake.Color.old_blurple()
            )
            
            embed.timestamp = datetime.datetime.now()

            await interaction.edit_original_message(embed=embed, view=view, attachments=[])

        except Exception as e:
            await interaction.response.send_message(f"Ошибка: {e}")  


class ButtonHelp(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @disnake.ui.button(label="Администратор", style=disnake.ButtonStyle.blurple)
    async def btBack(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            await interaction.response.defer()

            view = ButtonAdminHelp()
            
            embed = disnake.Embed(
                title="Команды администратора",
                description=f"**`/user` - Действия над пользователем**\n"
                              "**`/set_welcome_channel` - Установить канал приветствия**\n"
                              "**`/remove_welcome_channel ` - Удалить канал приветствия**\n"
                              "**`/set_log` - Установить канал логирования**\n"
                              "**`/remove_log_channel ` - Удалить канал логирования**\n"
                              "**`/clear ` - Очистка чата**\n"
                              "**`/add_admin` - Добавить администатора в список**\n"
                              "**`/del_admin` - Удалить администаратора из списка**\n"
                              "**`/set_autorole` - Установить роль для автовыдачи**\n"
                              "**`/remove_autorole` - Удалить роль для автовыдачи**\n",
                color=disnake.Color.old_blurple()
            )
            embed.timestamp = datetime.datetime.now()
            
            await interaction.edit_original_message(embed=embed, view=view, attachments=[])

        except Exception as e:
            await interaction.response.send_message(f"Ошибка: {e}")  
    

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help", description="Основные команды")
    async def help(self, interaction):
        view = ButtonHelp() 
        
        embed = disnake.Embed(
            title="Основные команды бота",
            description=f"**`/profile` - Карточка пользователя**\n"
            "**`/promocode_details` - Получить детали промокода**\n"
            "**`/use_promocode` - Использовать промокод**\n"
            "**`/list_promocodes` - Показать все промокоды**\n"
            "**`/admin_list` - Список администраторов**\n",
            color=disnake.Color.old_blurple()
            )
        embed.timestamp = datetime.datetime.now()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        
def setup(bot):
    bot.add_cog(Help(bot))
        