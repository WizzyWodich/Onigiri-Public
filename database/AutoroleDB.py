import aiosqlite
import disnake
from disnake.ext import commands


class AutoRoleDanabase:
    def __init__(self):
        self.botDatabase = "database/fileDB/BotDDatabase.db"

    async def create_table_autorole(self):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS autorole (
                                        guildID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        roleID INT NULL
                                    )''')
                await db.commit()
    
    async def add_autorole(self, guild, role):
        query_select = "SELECT * FROM autorole WHERE guildID = ?"
        query_insert = "INSERT INTO autorole (guildID, roleID) VALUES (?, ?)"
        query_update = "UPDATE autorole SET roleID = ? WHERE guildID = ?"

        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute(query_select, (guild.id,))
                result = await cursor.fetchone()
                if result:
                    await cursor.execute(query_update, (role.id, guild.id))
                else:
                    await cursor.execute(query_insert, (guild.id, role.id))
            await db.commit()
    
    async def get_autorole(self, guild: disnake.Guild):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query_check = '''SELECT roleID FROM autorole WHERE guildID = ?'''
                await cursor.execute(query_check, (guild.id,))
                autorole = await cursor.fetchone()
                if autorole:
                    role_id = autorole[0]
                    role = disnake.utils.get(guild.roles, id=role_id)
                    if role:
                        return role  # Возвращаем объект роли
                return None

                    
    async def remove_autorole(self, guild: disnake.Guild):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = 'DELETE FROM autorole WHERE guildID = ?'
                await cursor.execute(query, (guild.id,))
                await db.commit()