import aiosqlite
import disnake
from disnake.ext import commands


class AdminListDatabase:
    def __init__(self):
        self.botDatabase = "database/fileDB/BotDDatabase.db"

    async def create_table_admins_list(self):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS adminsList (
                                        guildID INTEGER,
                                        adminName TEXT
                                    )''')
                await db.commit()

    async def insert_admins(self, guild: disnake.Guild, member: disnake.Member):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = '''INSERT INTO adminsList (guildID, adminName) VALUES (?, ?)'''
                await cursor.execute(query, (guild.id, member.name))
                await db.commit()

    async def get_admins(self, member: disnake.Member):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = 'SELECT * FROM adminsList WHERE adminName = ?'
                await cursor.execute(query, (member.name,))
                return await cursor.fetchone()

    async def get_admins_sorted(self, guild_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = 'SELECT * FROM adminsList WHERE guildID = ? ORDER BY adminName'
                await cursor.execute(query, (guild_id,))
                return await cursor.fetchall()

    async def remove_admin(self, member: disnake.Member):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = 'DELETE FROM adminsList WHERE adminName = ?'
                await cursor.execute(query, (member.name,))
                await db.commit()