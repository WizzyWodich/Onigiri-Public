import aiosqlite
import random

class RankDatabase:
    def __init__(self, bot):
        self.bot = bot
        self.botDatabase = "database/fileDB/BotDDatabase.db"

    async def create_table_ranked(self):
        async with aiosqlite.connect(self.botDatabase) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ranked (
                    id INTEGER PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    score INTEGER DEFAULT 5,
                    new_score INTEGER DEFAULT 225,
                    coins INTEGER DEFAULT 1000,
                    rubins INTEGER DEFAULT 10,
                    message_count INTEGER DEFAULT 0,
                    voice_time INTEGER DEFAULT 0
                )
            """)
            await db.commit()

    async def add_user(self, user):
        async with aiosqlite.connect(self.botDatabase) as db:
            await db.execute("INSERT OR IGNORE INTO ranked (id) VALUES (?)", (user.id,))
            await db.commit()

    async def get_user_level(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("SELECT level FROM ranked WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None

    async def get_user_score(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("SELECT score FROM ranked WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None

    async def get_user_new_score(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("SELECT new_score FROM ranked WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None

    async def get_level_experience_threshold(self, level):
        return int(100 * (2.25 ** (level - 1)))

    async def update_level_method(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("SELECT score, level FROM ranked WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                score, level = row
                initial_level = level
                level_up = False
                
                while True:
                    experience_threshold = await self.get_level_experience_threshold(level)
                    
                    if score >= experience_threshold:
                        score -= experience_threshold
                        level += 1
                        level_up = True  # Уровень изменился
                        await self.update_balance(user_id, 1000, 10)
                    else:
                        break

                if level_up:
                    # Обновляем уровень и баллы в базе данных
                    await db.execute("UPDATE ranked SET level = ?, score = ?, new_score = ? WHERE id = ?", (level, score, experience_threshold, user_id))
                    await db.commit()
                    print(f"User {user_id} level up from {initial_level} to {level}")  # Логирование уровня
                    return True
                else:
                    print(f"User {user_id} did not level up (current level: {level})")  # Логирование неудачи уровня
                    return False
            else:
                print(f"User {user_id} not found in database")  # Логирование отсутствия пользователя
                return False




    async def update_score(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            experience_gain = random.randint(5, 30)  # случайное количество опыта от 5 до 30
            await db.execute("UPDATE ranked SET score = score + ? WHERE id = ?", (experience_gain, user_id))
            await db.commit()

            # Обновляем уровень, если необходимо
            if await self.update_level_method(user_id):
                return f"Level up! You are now level {await self.get_user_level(user_id)}."
            else:
                return f"You gained {experience_gain} experience."
            
            

    async def get_user_rubins(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("SELECT rubins FROM ranked WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None
            
    async def get_user_coins(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("SELECT coins FROM ranked WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None

    async def get_user_rank_by_coins(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("""
                SELECT id, coins
                FROM ranked
                ORDER BY coins DESC
            """)
            ranks = await cursor.fetchall()
            rank = 1
            for row in ranks:
                if row[0] == user_id:
                    return rank
                rank += 1
        return None

    async def get_user_rank_by_rubins(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("""
                SELECT id, rubins
                FROM ranked
                ORDER BY rubins DESC
            """)
            ranks = await cursor.fetchall()
            rank = 1
            for row in ranks:
                if row[0] == user_id:
                    return rank
                rank += 1
        return None

    async def get_user_rank_by_score(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("""
                SELECT id, score
                FROM ranked
                ORDER BY score DESC
            """)
            ranks = await cursor.fetchall()
            rank = 1
            for row in ranks:
                if row[0] == user_id:
                    return rank
                rank += 1
        return None

    async def get_user_rank_by_messages(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("""
                SELECT id, message_count
                FROM ranked
                ORDER BY message_count DESC
            """)
            ranks = await cursor.fetchall()
            rank = 1
            for row in ranks:
                if row[0] == user_id:
                    return rank
                rank += 1
        return None

    async def get_user_rank_by_voice_time(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("""
                SELECT id, voice_time
                FROM ranked
                ORDER BY voice_time DESC
            """)
            ranks = await cursor.fetchall()
            rank = 1
            for row in ranks:
                if row[0] == user_id:
                    return rank
                rank += 1
        return None

    

    async def update_message_count(self, user_id, count=1):
        async with aiosqlite.connect(self.botDatabase) as db:
            await db.execute("UPDATE ranked SET message_count = message_count + ? WHERE id = ?", (count, user_id))
            await db.commit()

    async def get_user_message_count(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("SELECT message_count FROM ranked WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None
            
    async def update_voice_time(self, user_id, minutes):
        async with aiosqlite.connect(self.botDatabase) as db:
            await db.execute("UPDATE ranked SET voice_time = voice_time + ? WHERE id = ?", (minutes, user_id))
            await db.commit()

    async def get_user_voice_time(self, user_id):
        async with aiosqlite.connect(self.botDatabase) as db:
            cursor = await db.execute("SELECT voice_time FROM ranked WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                return None

    async def update_balance(self, user_id, countCoin, countRuby):
        async with aiosqlite.connect(self.botDatabase) as db:
            await db.execute(
                "UPDATE ranked SET coins = coins + ?, rubins = rubins + ? WHERE id = ?",
                (countCoin, countRuby, user_id)
            )
            await db.commit()
