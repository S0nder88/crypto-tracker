import sqlite3


class SQLighter:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        with self.connection:
            result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
            return bool(len(result.fetchall()))

    # def get_user_id(self, user_id):
    #     """Достаем id юзера в базе по его user_id"""
    #     with self.connection:
    #         result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
    #         return result.fetchone()[0]

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        with self.connection:
            self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))

    def alerts_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        with self.connection:
            result = self.cursor.execute("SELECT `id` FROM `alerts` WHERE `user_id` = ?", (user_id,))
            return bool(len(result.fetchall()))

    def add_alerts(self, user_id, answer1, answer2):
        """Создаем сигнал о цене"""
        with self.connection:
            self.cursor.execute("INSERT INTO alerts (user_id, coin_name, coin_price) VALUES (?, ?, ?)", (user_id, answer1, answer2,))

    def get_alerts(self, user_id):
        """Читаем все данные из БД"""
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `alerts` WHERE `user_id` =?", (user_id,))
            return result.fetchall()

    def get_coins(self, user_id):
        """получаем coin_name|price"""
        with self.connection:
            result = self.cursor.execute("SELECT coin_name, coin_price FROM `alerts` WHERE `user_id` =?", (user_id,))
            return result.fetchall()

    def get_users_id(self,):
        """Получаем ЮЗЕР ИД"""
        with self.connection:
            result = self.cursor.execute("SELECT user_id FROM users")
            return result.fetchall()

    def delete_coin(self, user_id, coin_name):
        """Удаление отправленных оповещений"""
        with self.connection:
            self.cursor.execute("DELETE FROM `alerts` WHERE `user_id` =? AND `coin_name` = ?", (user_id, coin_name,))

    def delete_alert(self, id,):
        self.cursor.execute("DELETE FROM alerts WHERE id=?", (id,))

    def close(self):
        self.connection.close()
