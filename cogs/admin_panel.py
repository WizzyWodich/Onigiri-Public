import disnake
from disnake.ext import commands
import datetime
import aiohttp, io, disnake, random

from PIL import Image, ImageFont, ImageDraw
from disnake.ui.action_row import ModalUIComponent
from disnake.utils import MISSING
from database.UserInfoDatabase import UsersDataBase
from database.LogsDatabase import LogsDatabase
from database.RankDatabase import RankDatabase

log_db = LogsDatabase()
user_db = UsersDataBase()


class ModalDeleteWarn(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.member = member
        
        components = [
            disnake.ui.TextInput(label="Количество предупреждений", placeholder="Введите кол-во предупреждений", custom_id="count_warns"),
        ]

        title = f"Снятие предупреждения у {member.name}"
        
        super().__init__(title=title, components=components, custom_id="modalDeleteWarn")
        
        
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        countDeleteWarn = interaction.text_values["count_warns"]
        
        await user_db.create_table_warns()
        result_cheak_db = await user_db.check_user_warndb(self.member.id)
        
        if result_cheak_db: # Если пользователь есть в таблице тогда
            await user_db.delete_warn_user(self.member.id, countDeleteWarn)
            embed = disnake.Embed(color=disnake.Color.old_blurple(), title="Снятие предупреждения")
            embed.description = f"### {interaction.author.mention}, вы успешно сняли предупреждение пользователю {self.member.mention} " \
                                f"в количестве {countDeleteWarn}."
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            
            log_channel = await log_db.get_log_channel(interaction.guild)
            if not log_channel:
                await interaction.send(f"### В гильдии не установлен канал логирования. Используйте  - `/sel_log`", ephemeral=True)
            else:
                channel = interaction.guild.get_channel(log_channel)  # Вставить ID канала куда будут отправляться заявки
                await channel.send(f"### (Снятие предупреждения) Администратор {interaction.author.mention} снял предупреждение пользователю {self.member.mention} в количестве {countDeleteWarn}")
                
        else: # Если лож
            embed = disnake.Embed(color=disnake.Color.old_blurple(), title="Пользователя не найдено!")
            embed.description = f"### {interaction.author.mention}, Пользователь {self.member.mention} " \
                                f"не найден в таблице."
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        

class ModalWarn(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.member = member
        
        components = [
            disnake.ui.TextInput(label="Количество предупреждений", placeholder="Введите количество предупреждений", custom_id="count_warns"),
            disnake.ui.TextInput(label="Причина предупреждения", placeholder="Введите причину предупреждения", custom_id="reason")
        ]

        title = f"Выдача варна - {member.name}"
        
        super().__init__(title=title, components=components, custom_id="modalWarn")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        countWarn = interaction.text_values["count_warns"]
        reason = interaction.text_values["reason"]
        
        await user_db.create_table_warns()
        result_cheak_db = await user_db.check_user_warndb(self.member.id)
        
        if result_cheak_db: # Если пользователь есть в таблице тогда
            if await user_db.get_user_warn_count(self.member.id) >= 3: # Проверяем количество предупреждений и кикаем если больше или равно 3
                await self.member.kick()
                await interaction.response.send_message("### Количество предупреждений пользователя было больше 3-х он был изгнан с сервера.", ephemeral=True)
                
            elif await user_db.get_user_warn_count(self.member.id) < 3: # Если меньше 3 тогда обновляем количество предупреждений
                await user_db.update_warns(interaction, self.member.id, countWarn)
                
                embed = disnake.Embed(color=disnake.Color.old_blurple(), title="Предупреждение выдано!")
                embed.description = f"### {interaction.author.mention}, Вы успешно выдали предупреждение пользователю {self.member.mention} " \
                                    f"в количестве {countWarn}"
                embed.set_thumbnail(url=interaction.author.display_avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                log_channel = await log_db.get_log_channel(interaction.guild)
                
                if not log_channel:
                    await interaction.send(f"### В гильдии не установлен канал логирования. Используйте  - `/sel_log`", ephemeral=True)
                else:
                    channel = interaction.guild.get_channel(log_channel)  # Вставить ID канала куда будут отправляться заявки
                    await channel.send(f"### Администратор {interaction.author.mention} выдал предупреждение пользователю {self.member.mention} в количестве {countWarn} ( по причине: {reason})")
                
                if await user_db.get_user_warn_count(self.member.id) >= 3: # Опять проверяем в случае истины кикаем
                    await self.member.kick()
                    await interaction.response.send_message("Количество предупреждений пользователя было больше 3-х он был изгнан с сервера.")
        else: # Если лож
            await user_db.create_table_warns()
            await user_db.insert_warns(interaction, self.member.id, self.member.name, countWarn)
            
            embed = disnake.Embed(color=disnake.Color.old_blurple(), title="Предупреждение выдано!")
            embed.description = f"### {interaction.author.mention}, Вы успешно выдали предупреждение пользователю {self.member.mention} " \
                                f"в количестве {countWarn}"
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            log_channel = await log_db.get_log_channel(interaction.guild)
            if not log_channel:
                await interaction.send(f"### В гильдии не установлен канал логирования. Используйте  - `/sel_log`", ephemeral=True)
            else:
                channel = interaction.guild.get_channel(log_channel)  # Вставить ID канала куда будут отправляться заявки
                await channel.send(f"### Администратор {interaction.author.mention} выдал предупреждение пользователю {self.member.mention} в количестве {countWarn} ( по причине: {reason})")
                
                
class ModalMute(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.member = member

        components = [
            disnake.ui.TextInput(label="Время мута (в минутах)", placeholder="Введите времяя мута",
                                 custom_id="time"),
            disnake.ui.TextInput(label="Причина мута", placeholder="Введите причину мута", custom_id="reason")
        ]

        title = f"Замьют пользователя {member.name}"

        super().__init__(title=title, components=components, custom_id="modalMute")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        time_str = interaction.text_values["time"]
        reason = interaction.text_values["reason"]
        time_minutes = int(time_str)

        time = datetime.datetime.now() + datetime.timedelta(minutes=time_minutes)
        await self.member.timeout(until=time, reason=reason)

        embed = disnake.Embed(color=disnake.Color.old_blurple(), title="Пользователь замючен!")
        embed.description = f"### {interaction.author.mention}, Вы успешно замьютили пользователя {self.member.mention} " \
                            f"на `{time_minutes}` минут"
        embed.set_thumbnail(url=interaction.author.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        log_channel = await log_db.get_log_channel(interaction.guild)
        if not log_channel:
            await interaction.send(f"### В гильдии не установлен канал логирования. Используйте  - `/sel_log`", ephemeral=True)
        else:
            channel = interaction.guild.get_channel(log_channel)  # Вставить ID канала куда будут отправляться заявки
            await channel.send(f"### Администратор {interaction.author.mention} замьютил пользователя {self.member.mention} на {time_minutes} ( по причине: {reason})")

            
            
class ModalReaname(disnake.ui.Modal):
    def __init__(self, member: disnake.Member):
        self.member = member
        
        components = [
            disnake.ui.TextInput(label="Новое имя пользователя", placeholder="Введите новое имя пользователя", custom_id="new_name"),
            disnake.ui.TextInput(label="Причина изменения", placeholder="Введите причину изменения", custom_id="reason")
        ]
        
        title = f"Изменение имени пользователя {member.name}"
        
        super().__init__(title=title, components=components, custom_id="modalReaname")
        
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        new_name = interaction.text_values["new_name"]
        reason = interaction.text_values["reason"]
        
        await self.member.edit(nick=new_name)        
        embed = disnake.Embed(color=disnake.Color.old_blurple(), title="Имя изменино!")
        embed.description = f"### {interaction.author.mention}, Вы успешно изменили имя пользователю {self.member.mention} " \
                            f"на {new_name}"
        embed.set_thumbnail(url=interaction.author.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        log_channel = await log_db.get_log_channel(interaction.guild)
        if not log_channel:
            await interaction.send(f"### В гильдии не установлен канал логирования. Используйте  - `/sel_log`", ephemeral=True)
        else:
            channel = interaction.guild.get_channel(log_channel)  # Вставить ID канала куда будут отправляться заявки
            await channel.send(f"### Администратор {interaction.author.mention} изменил имя пользователю {self.member.mention} на {new_name} ( по причине: {reason})")
    
class ButtonViev(disnake.ui.View):
    def __init__(self, member: disnake.Member):
        super().__init__(timeout=None)
        self.member = member

    @disnake.ui.button(label="Мут", style=disnake.ButtonStyle.danger, custom_id="btMute")
    async def btMuteAll(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if not self.member:
            await interaction.response.defer()
        else:
            await interaction.response.send_modal(ModalMute(self.member))

    @disnake.ui.button(label="Выгнать", style=disnake.ButtonStyle.danger, custom_id="btKick")
    async def btKick(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.member.kick()
        embed = disnake.Embed(
            title="Пользователь кикнут",
            description=f"Пользователь {self.member.mention} был выгнан с сервера.",
            color=disnake.Color.old_blurple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @disnake.ui.button(label="Забанить", style=disnake.ButtonStyle.danger, custom_id="btBan")
    async def btBan(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.member.ban()
        embed = disnake.Embed(
            title="Пользователь забанен",
            description=f"Пользователь {self.member.mention} был забанен.",
            color=disnake.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    
    @disnake.ui.button(label="Выдать предупреждение", style=disnake.ButtonStyle.danger, custom_id="btWarn")
    async def btSetWarn(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if not self.member:
            await interaction.response.defer()
        else:
            await interaction.response.send_modal(ModalWarn(self.member))
    
    @disnake.ui.button(label="Размьютить", style=disnake.ButtonStyle.green, custom_id="btUnMute")
    async def btUnMute(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.member.timeout(until=None, reason=None)
        await interaction.send(f"{self.member.mention} Размьючен", ephemeral=True)
    
    @disnake.ui.button(label="Снять предупреждения", style=disnake.ButtonStyle.blurple, custom_id="btDeleteWarns")
    async def btDeleteWarns(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if not self.member:
            await interaction.response.defer()
        else:
            await interaction.response.send_modal(ModalDeleteWarn(self.member))
    
    @disnake.ui.button(label="Изменить имя", style=disnake.ButtonStyle.blurple, custom_id="btRename")
    async def btRename(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        if not self.member:
            await interaction.response.defer()
        else:
            await interaction.response.send_modal(ModalReaname(self.member))
            
    
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_avatar(self, url: str) -> bytes: # алгоритм жля получения и чтения аватара юзера
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                avatar = await resp.read()
        return avatar

    async def limit_string_length(self, string, max_length=12) -> None: # сокращение никнейма
        if len(string) > max_length:
            return f'{string[:max_length-1]}...'
        else:
            return string

    @commands.slash_command(name="user", description="Управление пользователем", dm_permission=False)
    @commands.has_permissions(administrator=True)
    async def user_panel(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member):
        self.db = RankDatabase(self.bot)
        view = ButtonViev(member)
        
        user_name = member.display_name
        role = max(member.roles, key=lambda role: role.position)
        role_name = role.name  
        countWarnsUser = await user_db.get_user_warn_count(member.id)
        coins = await self.db.get_user_coins(member.id)
        ruby = await self.db.get_user_rubins(member.id)
        score = await self.db.get_user_score(member.id)
        
        await interaction.response.defer(ephemeral=True)
        
        font = ImageFont.truetype('font/IBMPlexSerif-Medium.ttf', 24) # ваш путь к шрифту
        fill_color = '#FFFFFF'
        
        background = Image.open('image/admin_patel/Adminpanel.png') # ваш путь к фону профиля
        backdraw = ImageDraw.Draw(background)   


        avatar = await self.get_avatar(member.display_avatar.url)
        avatar_image = Image.open(io.BytesIO(avatar))
        avatar_image = avatar_image.resize((160, 160), Image.LANCZOS)
        bigsize = (avatar_image.size[0] * 3, avatar_image.size[1] * 3)
        mask = Image.new("L", bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, 255)
        mask = mask.resize(avatar_image.size, Image.LANCZOS)
        background.paste(avatar_image, (26, 21), mask)
        
        name = await self.limit_string_length(user_name)
        text_width = backdraw.textbbox((0, 0), name, font=font)[2] - backdraw.textbbox((0, 0), name, font=font)[0]
        x = (241 - text_width) // 2 + 251
        backdraw.text((x, 50), name, font=font, fill=fill_color)
        
        role_display = await self.limit_string_length(role_name)  # Используем имя роли
        text_width = backdraw.textbbox((0, 0), role_display, font=font)[2] - backdraw.textbbox((0, 0), role_display, font=font)[0]
        x = (176 - text_width) // 2 + 273
        backdraw.text((x, 135), role_display, font=font, fill=fill_color)
        
        if countWarnsUser is None: countWarnsUser = 0
        warns = f'{str(countWarnsUser)}/3'
        text_width = backdraw.textlength(warns, font)
        x = (44 - text_width) // 2 + 335
        backdraw.text((x, 220), warns, font=font, fill=fill_color)
        
        
        if score is None:
            score = 0
        if coins is None:
            coins = 0
        if ruby is None:
            ruby = 0
            
        if score >= 100000: 
            score = f'{str(score)[:-3]}k' # сокращение чисел
        if coins >= 100000:
            coins = f'{str(coins)[:-3]}k' # сокращение 
        if ruby >= 100000:
            ruby = f'{str(ruby)[:-3]}k' # сокращение
        
        score = str(score)
        text_width = backdraw.textlength(score, font)
        x = (183 - text_width) // 2 + 562
        backdraw.text((x, 219), score, font=font, fill=fill_color)
        
        coins = str(coins)
        text_width = backdraw.textlength(coins, font)
        x = (105 - text_width) // 2 + 615
        backdraw.text((x, 60), coins, font=font, fill=fill_color)
        
        ruby = str(ruby)
        text_width = backdraw.textlength(ruby, font)
        x = (105 - text_width) // 2 + 615
        backdraw.text((x, 128), ruby, font=font, fill=fill_color)
        
        img_bytes = io.BytesIO()
        background.save(img_bytes, 'PNG')
        img_bytes.seek(0)
        image_file = disnake.File(img_bytes, filename=f'{member.display_name}_profile.png')

        await interaction.followup.send(view=view, file=image_file)


def setup(bot):
    bot.add_cog(Admin(bot))