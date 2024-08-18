import aiosqlite
import disnake
from disnake.ext import commands

class UsersDataBase:
    def __init__(self):
        self.botDatabase = "database/fileDB/BotDDatabase.db"
    
    async def create_table(self):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                        userID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        userName TEXT NULL,
                                        age INTEGER NULL
                                    )''')
                await db.commit()
    
    async def create_table_warns(self):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS warns (
                                        userID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        userName TEXT NULL,
                                        countWarns INTEGER NULL
                                    )''')
                await db.commit()
    
    async def insert_warns(self, interaction, member_id, member_name, warn: int):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = '''INSERT INTO warns VALUES (?, ?, ?)'''
                await cursor.execute(query, (member_id, member_name, warn))
                await db.commit()
            
    async def update_warns(self, interaction, member_id, warn: int):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = '''UPDATE warns SET countWarns = countWarns + ? WHERE userID = ?'''
                await cursor.execute(query, (warn, member_id))
                await db.commit()
    
    async def check_user_warndb(self, member_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query_check = '''SELECT * FROM warns WHERE userID = ?'''
                await cursor.execute(query_check, (member_id,))
                row = await cursor.fetchone()
                if row:
                    return row
                
    async def get_user_warn_count(self, member_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query_check = '''SELECT countWarns FROM warns WHERE userID = ?'''
                await cursor.execute(query_check, (member_id,))
                row = await cursor.fetchone()
                
                if row:
                    return row[0]
    
    async def delete_warn_user(self, member_id, countWarn):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query_update = '''UPDATE warns SET countWarns = countWarns - ? WHERE userID = ?'''
                await cursor.execute(query_update, (countWarn, member_id))
                await db.commit()

    async def insert_verify_user(self, interaction, member: disnake.Member):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = '''INSERT INTO users (userID, userName) VALUES (?, ?)'''
                await cursor.execute(query, (member.id, member.name))
                await db.commit()
            await interaction.send("Верефицирован", ephemeral=True)
            
    async def delete_verify_user(self, interaction, member: disnake.Member):
        async with aiosqlite.connect(self.botDatabase) as db:
            async with db.cursor() as cursor:
                query = '''DELETE FROM users WHERE userID = ?'''
                await cursor.execute(query, (member.id,))
                await db.commit()
            await interaction.send("Видалено", ephemeral=True)
    
    async def delete_user_from_all_databases(self, user_id):
        databases = self.botDatabase

        for database in databases:
            async with aiosqlite.connect(database) as db:
                async with db.cursor() as cursor:
                    if 'users' in database:
                        await cursor.execute('DELETE FROM users WHERE userID = ?', (user_id,))
                    elif 'warns' in database:
                        await cursor.execute('DELETE FROM warns WHERE userID = ?', (user_id,))
                    await db.commit()