import aiosqlite
import disnake
from disnake.ext import commands

class WelcomeChannel:
    def __init__(self):
        self.botDatabase = "database/fileDB/BotDDatabase.db"
        
    async def create_table(self):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS welcomeChannel (
                                        guildId INTEGER PRIMARY KEY AUTOINCREMENT,
                                        channelId INTEGER NULL
                                    )''')
                await db.commit()
    
    async def get_welcome_channel(self, guild: disnake.Guild):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT channelId FROM welcomeChannel WHERE guildId = ?', (guild.id,))
                result = await cursor.fetchone()
                return guild.get_channel(result[0]) if result else None
    
    async def add_welcome_channel(self, guild, channel: disnake.TextChannel):
        query_select = "SELECT * FROM welcomeChannel WHERE guildID = ?"
        query_insert = "INSERT INTO welcomeChannel (guildID, channelId) VALUES (?, ?)"
        query_update = "UPDATE welcomeChannel SET channelId = ? WHERE guildID = ?"

        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute(query_select, (guild.id,))
                result = await cursor.fetchone()
                if result:
                    await cursor.execute(query_update, (channel.id, guild.id))
                else:
                    await cursor.execute(query_insert, (guild.id, channel.id))
            await db.commit()
                
    async def remove_channel(self, guild: disnake.Guild):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute('DELETE FROM welcomeChannel WHERE guildId = ?', (guild.id,))
                await db.commit()
                