import aiosqlite
import datetime

class PromocodeDB:
    def __init__(self):
        self.botDatabase = "database/fileDB/BotDDatabase.db"
        
    async def create_table_promocodes(self):
        async with aiosqlite.connect(self.botDatabase) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS promocodes (
                                code TEXT PRIMARY KEY,
                                description TEXT NOT NULL,
                                p_score INTEGER DEFAULT 0,
                                p_coin INTEGER DEFAULT 0,
                                p_ruby INTEGER DEFAULT 0,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                expires_at DATE)''')
            await db.commit()

    
    async def create_table_userd_promocodes(self):
        async with aiosqlite.connect(self.botDatabase) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS used_promocodes (
                                    code TEXT,
                                    userID INTEGER
                            )''')
            await db.commit()
            
    async def insert_promocode(self, code: str, description: str, expires_at: str):
        try:
            async with aiosqlite.connect(self.botDatabase) as db:
                async with db.cursor() as cursor:
                    query = '''INSERT INTO promocodes (code, description, expires_at) VALUES (?, ?, ?)'''
                    await cursor.execute(query, (code, description, expires_at))
                    await db.commit()
        except aiosqlite.Error as e:
            print(f"Error inserting promocode: {e}")


            
    async def update_promocode(self, code: str, p_score: int = 0, p_coin: int = 0, p_ruby: int = 0):
        try:
            async with aiosqlite.connect(self.botDatabase) as db:
                async with db.cursor() as cursor:
                    query = '''UPDATE promocodes 
                               SET p_score = ?, p_coin = ?, p_ruby = ? 
                               WHERE code = ?'''
                    await cursor.execute(query, (p_score, p_coin, p_ruby, code))
                    await db.commit()
        except aiosqlite.Error as e:
            print(f"Ошибка при обновлении промокода: {e}")

    async def use_promocode(self, code: str, user_id: int):
        try:
            async with aiosqlite.connect(self.botDatabase) as db:
                async with db.cursor() as cursor:
                    # Проверка, существует ли промокод и не истек ли его срок действия
                    query = '''SELECT expires_at FROM promocodes WHERE code = ?'''
                    await cursor.execute(query, (code,))
                    result = await cursor.fetchone()

                    if result:
                        expires_at_str = result[0]
                        expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d").date()
                        today = datetime.datetime.now().date()

                        if expires_at < today:
                            return "### Этот промокод истек."

                        # Проверка, использовал ли пользователь этот промокод
                        use_promo_query = '''SELECT code FROM used_promocodes WHERE userID = ? AND code = ?'''
                        await cursor.execute(use_promo_query, (user_id, code))
                        used_result = await cursor.fetchone()

                        if used_result is not None:
                            return "### Вы уже использовали этот промокод."
                        else:
                            # Получение вознаграждений по промокоду
                            select_reward = '''SELECT p_score, p_coin, p_ruby FROM promocodes WHERE code = ?'''
                            await cursor.execute(select_reward, (code,))
                            reward_result = await cursor.fetchone()

                            if reward_result:
                                p_score, p_coin, p_ruby = reward_result

                                # Обновляем вознаграждения пользователя
                                update_user_reward = '''UPDATE ranked SET score = score + ?, coins = coins + ?, rubins = rubins + ? WHERE id = ?'''
                                await cursor.execute(update_user_reward, (p_score, p_coin, p_ruby, user_id))

                                # Отмечаем промокод как использованный
                                insert_use_query = '''INSERT INTO used_promocodes (code, userID) VALUES (?, ?)'''
                                await cursor.execute(insert_use_query, (code, user_id))
                                
                                await db.commit()
                                return "### Промокод успешно использован."
                            else:
                                return "### Ошибка: Не удалось получить вознаграждения для промокода."
                    else:
                        return "### Промокод не найден."
        except aiosqlite.Error as e:
            print(f"Error using promocode: {e}")
            return "### Произошла ошибка при использовании промокода."


    async def get_promocode_details(self, code: str):
        try:
            async with aiosqlite.connect(self.botDatabase) as db:
                async with db.cursor() as cursor:
                    query = '''SELECT * FROM promocodes WHERE code = ?'''
                    await cursor.execute(query, (code,))
                    promocode = await cursor.fetchone()
                    return promocode
        except aiosqlite.Error as e:
            print(f"Ошибка при получении деталей промокода: {e}")
            return None

    async def delete_promocode(self, code: str):
        try:
            async with aiosqlite.connect(self.botDatabase) as db:
                async with db.cursor() as cursor:
                    query = '''DELETE FROM promocodes WHERE code = ?'''
                    await cursor.execute(query, (code,))
                    await db.commit()
        except aiosqlite.Error as e:
            print(f"Ошибка при удалении промокода: {e}")
                
    async def get_all_promocodes(self):
        try:
            async with aiosqlite.connect(self.botDatabase) as db:
                async with db.cursor() as cursor:
                    query = '''SELECT code, description, p_score, p_coin, p_ruby, created_at, expires_at FROM promocodes'''
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
                    
                    # Форматируем результат
                    promocodes = []
                    for row in rows:
                        promocodes.append({
                            'code': row[0],
                            'description': row[1],
                            'p_score': row[2],
                            'p_coin': row[3],
                            'p_ruby': row[4],
                            'created_at': row[5],
                            'expires_at': row[6]
                        })
                    return promocodes
        except aiosqlite.Error as e:
            print(f"Error fetching promocodes: {e}")
            return []

