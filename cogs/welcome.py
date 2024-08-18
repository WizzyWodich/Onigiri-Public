import aiohttp, io, disnake, random
from disnake.ext import commands
from PIL import Image, ImageFont, ImageDraw
from disnake.ext import commands
from disnake import Permissions
from database.Welcome_Channel import WelcomeChannel

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_db = WelcomeChannel()
        
    async def get_avatar(self, url: str) -> bytes: # алгоритм жля получения и чтения аватара юзера
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                avatar = await resp.read()
        return avatar

    async def limit_string_length(self, string, max_length=15) -> None: # сокращение никнейма
        if len(string) > max_length:
            return f'{string[:max_length-1]}...'
        else:
            return string
        
        
    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        guild = member.guild
        welcome_db = WelcomeChannel()
        channel = await welcome_db.get_welcome_channel(guild)
        
        welcome_pictures_rand = {
            "pic1": "image/welcome_baner/Pic1.png",
            "pic2": "image/welcome_baner/Pic2.png",
            "pic3": "image/welcome_baner/Pic3.png",
            "pic4": "image/welcome_baner/Pic4.png",
            "pic5": "image/welcome_baner/Pic5.png",
            "pic6": "image/welcome_baner/Pic6.png",
            "pic7": "image/welcome_baner/Pic7.png",
            "pic8": "image/welcome_baner/Pic8.png",
            "pic9": "image/welcome_baner/Pic9.png",
            "pic10": "image/welcome_baner/Pic10.png",
            "pic11": "image/welcome_baner/Pic11.png",
            "pic12": "image/welcome_baner/Pic12.png",
            "pic13": "image/welcome_baner/Pic13.png",
            "pic14": "image/welcome_baner/Pic14.png",
            "pic15": "image/welcome_baner/Pic15.png",
            "pic16": "image/welcome_baner/Pic16.png",
            "pic17": "image/welcome_baner/Pic17.png",
            "pic18": "image/welcome_baner/Pic18.png",
            "pic19": "image/welcome_baner/Pic19.png"
        }
        
        random_background = random.choice(list(welcome_pictures_rand.values()))
        background = Image.open(random_background)
        
        fill_color = "#1A1A1A"
        
        backdraw = ImageDraw.Draw(background)
        font = ImageFont.truetype(font ='font/IBMPlexSerif-LightItalic.ttf', size = 100)
        
        # Аватарка
        avatar = await self.get_avatar(member.display_avatar.url)
        avatar_image = Image.open(io.BytesIO(avatar))
        avatar_image = avatar_image.resize((390, 390), Image.LANCZOS)
        bigsize = (avatar_image.size[0] * 3, avatar_image.size[1] * 3)
        mask = Image.new("L", bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, 255)
        mask = mask.resize(avatar_image.size, Image.LANCZOS)
        background.paste(avatar_image, (764, 84), mask)
        
        
        name = await self.limit_string_length(member.display_name)
        text_width = backdraw.textbbox((0, 0), name, font=font)[2] - backdraw.textbbox((0, 0), name, font=font)[0]
        x = (661 - text_width) // 2 + 629
        backdraw.text((x, 650), name, font=font, fill=fill_color)
        
        
        img_bytes = io.BytesIO()
        background.save(img_bytes, 'PNG')
        img_bytes.seek(0)
        image_file = disnake.File(img_bytes, filename=f'{member.display_name}_profile.png')
        
        if channel:
            await channel.send(file=image_file)    
        else:
            pass
        
    @commands.slash_command(name="simulate_join", dm_permission=False)
    @commands.is_owner()
    async def simulate_join(self, interaction: disnake.ApplicationCommandInteraction):
        # Получаем участника по ID
        member = interaction.author
        if member:
            await self.on_member_join(member)
            await interaction.response.send_message("Симуляция присоединения участника выполнена.", ephemeral=True)
        else:
            await interaction.response.send_message("Участник не найден.", ephemeral=True)
        

def setup(bot):
    bot.add_cog(Welcome(bot))
