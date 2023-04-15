import requests
import json
import schedule
import time
from pycoingecko import CoinGeckoAPI
from sqlighter import SQLighter

db = SQLighter('db.db')
api = CoinGeckoAPI()


def coin_data():
    """Дергаем АПИ и смотрим текущий курс валют"""
    data = api.get_coins_markets(vs_currency='usd')
    if len(data):
        coin_info = []
        for k in data:
            coin_info.append((k['symbol'], k['current_price']))
        return coin_info


print(coin_data())


def check_alert():
    """Смотрим созданные оповещения каждого пользователя """
    values = []
    data = db.get_users_id()
    for user_id in data:
        coin_data = db.get_coins(user_id[0])
        if len(coin_data):
            for coin in coin_data:
                values.append((user_id[0], coin[0], coin[1]))
    return values


def check_send():
    occupied_names = set(map(lambda x: x[1].lower(), check_alert()))
    print(occupied_names)
    for name, price in coin_data():
        if name.lower() in occupied_names:
            for user_id, alert_name, alert_price in check_alert():
                if alert_name.lower() == name.lower() and alert_price >= price:
                    # send message to user
                    message = f"{name} цена достигла {alert_price} USD"
                    send_message(user_id, message)
        else:
            print(name)


def send_message(user_id, message):
    """Отправляем сообщение пользователю"""
    token = '5886854603:AAEEvUIdKf91nivUe8czRsJYP6Q3xqrKzo4'
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': user_id,
        'text': message
    }
    response = requests.post(url, json=payload)
    print(response.json())


def main():
    coin_data()
    check_alert()
    check_send()


schedule.every(30).seconds.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)


if __name__ == '__main__':
    main()

class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()



    # other methods...
