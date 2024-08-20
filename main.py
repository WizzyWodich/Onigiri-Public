import disnake
from disnake.ext import commands
import os
import sys
from dotenv import load_dotenv
import logging
import asyncio

from database.UserInfoDatabase import UsersDataBase
from database.AdminsListDB import AdminListDatabase
from database.AutoroleDB import AutoRoleDanabase
from database.LogsDatabase import LogsDatabase
from database.Welcome_Channel import WelcomeChannel
from database.RankDatabase import RankDatabase
from database.PromocodeDB import PromocodeDB

# Load environment variables
load_dotenv("config/config.env")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

intents = disnake.Intents.all()
intents.message_content = True
prefix = os.getenv('PREFIX')
bot = commands.Bot(command_prefix=prefix, intents=intents, test_guilds=[1155576584523231373])
bot.remove_command("help")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Логи в консоль
        logging.FileHandler("bot.log")  # Логи в файл bot.log
    ]
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(
        status=disnake.Status.online,
        activity=disnake.Activity(
            type=disnake.ActivityType.streaming,
            name="Watching YouTube",
            url="https://www.youtube.com/watch?v=y3Q2fRqLlFk"
        ))

    # Initialize databases
    logs_db = LogsDatabase()
    users_db = UsersDataBase()
    welcome_channel_db = WelcomeChannel()
    autorole_db = AutoRoleDanabase()
    admin_list_db = AdminListDatabase()
    rank_db = RankDatabase(bot)
    promo_db = PromocodeDB()

    await promo_db.create_table_promocodes()
    await promo_db.create_table_userd_promocodes()
    await rank_db.create_table_ranked()
    await logs_db.create_table_log_chanel()
    await users_db.create_table()
    await users_db.create_table_warns()
    await welcome_channel_db.create_table()
    await autorole_db.create_table_autorole()
    await admin_list_db.create_table_admins_list()

    # Load all cogs
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")

async def reload_cogs(interaction):
    try:
        # Перезагрузка файлов бота
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                cog_name = file[:-3]
                try:
                    bot.unload_extension(f"cogs.{cog_name}")
                    bot.load_extension(f"cogs.{cog_name}")
                    logging.info(f"Rebooted cog: {cog_name}")
                except commands.ExtensionNotLoaded:
                    logging.warning(f"Since {cog_name} was not loaded, I can’t unload it.")
                except commands.ExtensionNotFound:
                    logging.error(f"Cog {cog_name} not found.")
                except Exception as e:
                    logging.error(f"Error while rebooting {cog_name}: {e}")
                    await interaction.followup.send(f"### {interaction.author.mention} Ошибка при перезагрузке когов: {e}", ephemeral=True)
                    return  # Прекратить перезагрузку, если произошла ошибка
    except Exception as e:
        logging.error(f"Error during reboot process: {e}")
        await interaction.followup.send(f"### {interaction.author.mention} Произошла ошибка при перезагрузке файлов бота.", ephemeral=True)

async def countdown(interaction):
    message = await interaction.followup.send(f"### {interaction.author.mention} Перезагрузка завершится через 20 секунд.", ephemeral=True)
    for i in range(20, 0, -1):
        await asyncio.sleep(1)
        await message.edit(content=f"### {interaction.author.mention} Перезагрузка завершится через `{i}` секунд.")

    # Сообщение о завершении перезагрузки
    await message.edit(content=f"### {interaction.author.mention} Файлы успешно перезагрузились.")

@bot.slash_command(name="reload_cog", description="Перезагрузить ког")
@commands.is_owner()  # Команда доступна только владельцу бота
async def reload(interaction: disnake.AppCommandInteraction):
    await interaction.response.defer(ephemeral=True)

    # Запускаем перезагрузку когов и обратный отсчёт параллельно
    await asyncio.gather(
        reload_cogs(interaction),
        countdown(interaction)
    )

@bot.event
async def on_slash_command_error(interaction: disnake.AppCommandInteraction, error):
    color = disnake.Colour(0x1D53CA)  # Создание объекта цвета

    if not interaction.response.is_done():
        try:
            if isinstance(error, commands.CommandInvokeError):
                embed = disnake.Embed(
                    description=f"### <:wrong1:1274387454987735123> Произошла ошибка при выполнении команды:\n```{error}```",
                    color=color
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            elif isinstance(error, commands.MissingPermissions):
                embed = disnake.Embed(
                    description=f"### <:roleuser:1274387457298927711> У вас недостаточно прав для выполнения этой команды\n```Отказано в доступе```",
                    color=color
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            elif isinstance(error, commands.NotOwner):
                embed = disnake.Embed(
                    description=f"### <:wrong1:1274387454987735123> Эта команда доступна только для владельца бота\n```Отказано в доступе```",
                    color=color
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = disnake.Embed(
                    description=f"### <:wrong1:1274387454987735123> Произошла неизвестная ошибка:\n```{error}```",
                    color=color
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                logging.error(f"Неизвестная ошибка: {error}")
        except disnake.errors.NotFound:
            logging.error("Webhook not found or interaction is already responded to.")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
    else:
        logging.warning("Cannot send response; interaction is already done.")


token = os.getenv('BETA')
bot.run(token)
