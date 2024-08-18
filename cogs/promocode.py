import disnake
from disnake.ext import commands
from database.PromocodeDB import PromocodeDB

class PromocodeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.promocode_db = PromocodeDB()
        
    @commands.slash_command(name="add_promocode", description="Добавить новый промокод")
    @commands.is_owner()
    async def add_promocode(self, interaction: disnake.ApplicationCommandInteraction, code: str, description: str, expires_at: str):
        await self.promocode_db.insert_promocode(code, description, expires_at)
        await interaction.response.send_message(f"### Промокод '{code}' успешно добавлен и будет действителен до {expires_at}.", ephemeral=True)


    @commands.slash_command(name="update_promocode", description="Обновить промокод", dm_permission=False)
    @commands.is_owner()
    async def update_promocode(self, interaction: disnake.ApplicationCommandInteraction, code: str, p_score: int = 0, p_coin: int = 0, p_ruby: int = 0):
        await self.promocode_db.update_promocode(code, p_score, p_coin, p_ruby)
        await interaction.response.send_message(f"### Промокод '{code}' успешно обновлен.", ephemeral=True)
    
    @commands.slash_command(name="use_promocode", description="Использовать промокод")
    async def use_promocode(self, interaction: disnake.ApplicationCommandInteraction, code: str):
        result = await self.promocode_db.use_promocode(code, interaction.author.id)
        await interaction.response.send_message(result, ephemeral=True)

    @commands.slash_command(name="promocode_details", description="Получить детали промокода")
    async def promocode_details(self, interaction: disnake.ApplicationCommandInteraction, code: str):
        promocode = await self.promocode_db.get_promocode_details(code)
        if promocode:
            response = (f"**Промокод: `{promocode[0]}`**\n"
                        f"Описание: `{promocode[1]}`**\n"
                        f"**Очки оыпыта: `{promocode[2]}`**\n"
                        f"**Монеты: `{promocode[3]}`**\n"
                        f"**Рубины: `{promocode[4]}`**\n"
                        f"**Создан: `{promocode[5]}`**"
                        f"**Действует до: `{promocode[6]}`**")
        else:
            response = "### Промокод не найден."
        await interaction.response.send_message(response, ephemeral=True)
    
    @commands.slash_command(name="delete_promocode", description="Удалить промокод")
    @commands.is_owner()
    async def delete_promocode(self, interaction: disnake.ApplicationCommandInteraction, code: str):
        await self.promocode_db.delete_promocode(code)
        await interaction.response.send_message(f"Промокод '{code}' успешно удален.", ephemeral=True)

    @commands.slash_command(name="list_promocodes", description="Показать все промокоды")
    async def list_promocodes(self, interaction: disnake.ApplicationCommandInteraction):
        promocodes = await self.promocode_db.get_all_promocodes()
        
        if not promocodes:
            await interaction.response.send_message("### Нет доступных промокодов.", ephemeral=True)
            return
        
        embed = disnake.Embed(title="Список промокодов", color=disnake.Color.blue())
        for pc in promocodes:
            embed.add_field(
                name=f"Код: `{pc['code']}`",
                value=(
                    f"**Описание: {pc['description']}**\n"
                    f"**Счёт: {pc['p_score']}**\n"
                    f"**Монеты: {pc['p_coin']}**\n"
                    f"**Рубины: {pc['p_ruby']}**\n"
                    f"**Создан: {pc['created_at']}**\n"
                    f"**Истекает: {pc['expires_at']}**"
                ),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(PromocodeCog(bot))
