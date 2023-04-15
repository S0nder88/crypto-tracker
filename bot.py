

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from pycoingecko import CoinGeckoAPI
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram.dispatcher import FSMContext
from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text, state
from sqlighter import SQLighter


import config

storage = MemoryStorage()
api = CoinGeckoAPI()
# инициализируем бота
bot = Bot(token=config.API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

#  инициализируем базу данных
db = SQLighter('db.db')


class AddCoins(StatesGroup):
    coin = State()
    price = State()


# =====================================================================================================
# ====================================== ФУНКЦЫИ ======================================================
# =====================================================================================================

# =====================================================================================================
# ====================================== ПРИВЕТСВИЕ ===================================================
# =====================================================================================================
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        course_btn = types.KeyboardButton(text="💰 Курс")
        alerts_btn = types.KeyboardButton(text="🔔 Оповещение")
        profile_btn = types.KeyboardButton(text="👤 Профиль")
        keyboard.add(course_btn, alerts_btn, profile_btn)
        await message.answer(
            "<b>Привет👋\nЯ буду всегда держать тебя в курсе актуальной информации по ценами и новостям криптовалютного рынка. Используй клавиатуру ниже, для навигации.</b>",
            reply_markup=keyboard)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        course_btn = types.KeyboardButton(text="💰 Курс")
        alerts_btn = types.KeyboardButton(text="🔔 Оповещение")
        profile_btn = types.KeyboardButton(text="👤 Профиль")
        keyboard.add(course_btn, alerts_btn, profile_btn)
        await message.answer(
            "<b>Привет👋\nЯ буду всегда держать тебя в курсе актуальной информации по ценами и новостям криптовалютного рынка. Используй клавиатуру ниже, для навигации.</b>",
            reply_markup=keyboard)


# =====================================================================================================
# ====================================== ПРОФИЛЬ=======================================================
# =====================================================================================================
@dp.message_handler(Text(equals="👤 Профиль"))
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    user = await bot.get_chat(user_id)
    alerts = db.get_alerts(user_id)
    num_alerts = len(alerts)

    # Получаем информацию о пользователе
    username = user.username
    first_name = user.first_name
    last_name = user.last_name

    # Формируем ответ на запрос профиля пользователя
    response = f"<b>👤 Профиль</b>\n\n"
    response += f"<b>Ник:</b> <code>{first_name if first_name else ''} {last_name if last_name else ''}</code>\n"
    response += f"<b>Имя пользователя:</b> {'@' + username if username else '<i>не указано</i>'}\n"
    response += f"<b>Количество уведомлений:</b> <code>{num_alerts}</code>\n"

    await message.answer(response)


# =====================================================================================================
# ====================================== ОБРАБОТКА МЕНЮ ===============================================
# =====================================================================================================
@dp.message_handler(Text(equals="💰 Курс"))
async def courser(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    buttons_curr = [
        types.InlineKeyboardButton(text="BTC", callback_data="btc"),
        types.InlineKeyboardButton(text="ETN", callback_data="etn"),
        types.InlineKeyboardButton(text="LTC", callback_data="ltc"),
        types.InlineKeyboardButton(text="Еще", callback_data="more")

    ]
    keyboard.add(*buttons_curr)
    await message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)


@dp.callback_query_handler(text=["more", "back"])
async def more_btn(call: types.CallbackQuery):
    if call.data == "more":
        keyboard = types.InlineKeyboardMarkup()
        more_btn = [
            types.InlineKeyboardButton(text="TWT", callback_data="twt"),
            types.InlineKeyboardButton(text="BNB", callback_data="bnb"),
            types.InlineKeyboardButton(text="DOT", callback_data="dot"),
            types.InlineKeyboardButton(text="CAKE", callback_data="cake"),
            types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
        ]
        keyboard.add(*more_btn)
        await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)
        await call.answer()
        await call.message.delete()
    else:
        prev_keyboard = call.message.reply_markup
        keyboard = types.InlineKeyboardMarkup()
        buttons_curr = [
            types.InlineKeyboardButton(text="BTC", callback_data="btc"),
            types.InlineKeyboardButton(text="ETN", callback_data="etn"),
            types.InlineKeyboardButton(text="LTC", callback_data="ltc"),
            types.InlineKeyboardButton(text="Еще", callback_data="more")

        ]
        keyboard.add(*buttons_curr)
        await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)
        await call.answer()
        await call.message.delete()


# =====================================================================================================
# ====================================== ОПОВЕЩЕНИЕ ===================================================
# =====================================================================================================
@dp.message_handler(Text(equals="🔔 Оповещение"))
async def courser(message: types.Message):
    if not db.alerts_exists(message.from_user.id):
        keyboard = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton(text="✅ Создать", callback_data="create"),
            # types.InlineKeyboardButton(text="❌ Удалить", callback_data="delete")
        ]
        keyboard.add(*buttons)
        await message.answer("У вас пока нет оповещений, создайте новое, нажав на кнопку ниже.", reply_markup=keyboard)
    else:
        records = db.get_alerts(message.from_user.id)
        if len(records):
            answer = (f"🔔<b>Ваши установленные оповещения:</b>\n\n")
            for r in records:
                answer += f"🪙 <b>{r[2]}</b>\n"
                answer += f"  <b>L</b> <code>{r[3]}</code> <b>USD</b>\n"

            keyboard = types.InlineKeyboardMarkup()
            buttons = [
                types.InlineKeyboardButton(text="✅ Создать", callback_data="create"),
                types.InlineKeyboardButton(text="❌ Удалить", callback_data="delete")
            ]
            keyboard.add(*buttons)
            await message.answer(answer, reply_markup=keyboard)


# =====================================================================================================
# ====================================== УДАЛЕНИЕ =====================================================
# =====================================================================================================
@dp.callback_query_handler(text="delete")
async def delete(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = db.get_alerts(user_id)
    keyboard = types.InlineKeyboardMarkup()
    button_list = [types.InlineKeyboardButton(f"🪙 {x[2]}/{x[3]} USD", callback_data=f"del_{x[0]}") for x in data]
    keyboard.add(*button_list)

    await call.message.answer("<b>Выберите оповещение, которое хотите удалить:</b>", reply_markup=keyboard)
    await call.message.delete()
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('del_'))
async def process_callback_delete(callback_query: types.CallbackQuery):
    alert_id = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    db.delete_alert(int(alert_id))

    # загрузить обновленный список оповещений для данного пользователя
    updated_data = db.get_alerts(user_id)

    # сформировать новую клавиатуру с кнопками на основе обновленного списка оповещений и отправить ее пользователю
    keyboard = types.InlineKeyboardMarkup()
    button_list = [types.InlineKeyboardButton(f"🪙 {x[2]}/{x[3]} USD", callback_data=f"del_{x[0]}") for x in
                   updated_data]
    keyboard.add(*button_list)

    await callback_query.message.answer("<b>Выберите оповещение, которое хотите удалить:</b>", reply_markup=keyboard)
    await callback_query.message.delete()
    await callback_query.answer()
    # обновить запись в базе данных
    # db.update_alerts(user_id, updated_data)

    await bot.answer_callback_query(callback_query.id, text="Оповещение успешно удалено")


# =====================================================================================================
# ====================================== СОЗДАНИЕ =====================================================
# =====================================================================================================
# @dp.callback_query_handler(text="create")
# async def add_coins(call: types.CallbackQuery):
#     await AddCoins.coin.set()
#     await call.message.answer("Для начала, укажите валюту BTC, ETH, BNB или любую другую.")
#     await call.message.delete()
#     await call.answer()
#
#
# @dp.message_handler(state=AddCoins.coin)
# async def get_coins(message: types.Message, state: FSMContext):
#     answer = message.text
#     coin_list = api.get_coins_list()
#
#     if test_coin(answer, coin_list):
#         await state.update_data(answer1=answer)
#         await AddCoins.next()
#         await message.answer("<b>Введите цену, при которой хотите получить оповещение.</b>\n\n"
#                              "<b>Для добавления сразу нескольких цен - разделите их пробелом.</b>\n\n"
#                              "<b>20000 30000</b>")
#
#     else:
#         await message.answer("Введите корректное название монеты.")
#
#
def test_coin(coin_title: str, coins_list: list) -> bool:
    for coiny in coins_list:
        if coin_title.lower() == coiny.get('symbol').lower():
            return True
    return False


class CancelMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        if isinstance(obj, types.Message) and obj.text == "/cancel":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            course_btn = types.KeyboardButton(text="💰 Курс")
            alerts_btn = types.KeyboardButton(text="🔔 Оповещение")
            profile_btn = types.KeyboardButton(text="👤 Профиль")
            keyboard.add(course_btn, alerts_btn, profile_btn)
            await obj.answer("Действие отменено, воспользуйтесь клавиатурой для навигации.",
                             reply_markup=keyboard)
            await state.finish()


@dp.callback_query_handler(text="create")
async def add_coins(call: types.CallbackQuery):
    await AddCoins.coin.set()
    await call.message.answer("Для начала, укажите валюту BTC, ETH, BNB или любую другую.")
    await call.message.delete()
    await call.answer()


@dp.message_handler(state=AddCoins.coin)
async def get_coins(message: types.Message, state: FSMContext):
    answer = message.text
    coin_list = api.get_coins_list()

    if test_coin(answer, coin_list):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        course_btn = types.KeyboardButton(text="💰 Курс")
        alerts_btn = types.KeyboardButton(text="🔔 Оповещение")
        profile_btn = types.KeyboardButton(text="👤 Профиль")
        keyboard.add(course_btn, alerts_btn, profile_btn)
        await state.update_data(answer1=answer)
        await AddCoins.next()
        await message.answer("<b>Введите цену, при которой хотите получить оповещение.</b>\n\n"
                             "<b>Для добавления сразу нескольких цен - разделите их пробелом.</b>\n\n"
                             "<b>20000 30000</b>", reply_markup=keyboard)

    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        course_btn = types.KeyboardButton(text="💰 Курс")
        alerts_btn = types.KeyboardButton(text="🔔 Оповещение")
        profile_btn = types.KeyboardButton(text="👤 Профиль")
        keyboard.add(course_btn, alerts_btn, profile_btn)
        await message.answer("Введите корректное название монеты.", reply_markup=keyboard)


@dp.message_handler(state=AddCoins.price)
async def get_price(message: types.Message, state: FSMContext):
    res = db.get_alerts(message.from_user.id)
    data = await state.get_data()
    answer1 = data.get("answer1")
    answer2 = message.text
    if len(res) >= 5:
        await message.answer('Установлен лимит на создание оповещений!')
    elif answer2.isdigit():
        db.add_alerts(message.from_user.id, answer1, answer2)
        keyboard = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton(text="✅ Создать", callback_data="create"),
            types.InlineKeyboardButton(text="❌ Удалить", callback_data="delete")
        ]
        btn_view = [
            types.InlineKeyboardButton(text="🔍 Посмотреть все оповещения", callback_data="view_alerts")
        ]
        keyboard.add(*buttons)
        keyboard.add(*btn_view)
        await message.answer(f"<b>Ваше оповещение добавлено✅</b>\n"
                             f"🪙 <b>{answer1}</b>\n"
                             f"  <b>L</b> <code>{answer2}</code> <b>USD</b>", reply_markup=keyboard)
        await state.finish()

    else:
        await message.answer("Введите правильное значение цены!")


# =====================================================================================================
# ====================================== ОБРАБОТКА КУРСА ВАЛЮТ ========================================
# =====================================================================================================
@dp.callback_query_handler(text="btc")
async def send_random_value(call: types.CallbackQuery):
    price = api.get_price(ids='bitcoin', vs_currencies='usd')["bitcoin"]["usd"]
    await call.message.answer(f" 1 BTC = {price}")
    await call.message.delete()
    await call.answer()
    keyboard = types.InlineKeyboardMarkup()
    buttons_curr = [
        types.InlineKeyboardButton(text="BTC", callback_data="btc"),
        types.InlineKeyboardButton(text="ETN", callback_data="etn"),
        types.InlineKeyboardButton(text="LTC", callback_data="ltc"),
        types.InlineKeyboardButton(text="Еще", callback_data="more")

    ]
    keyboard.add(*buttons_curr)
    await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)


@dp.callback_query_handler(text="etn")
async def send_random_value(call: types.CallbackQuery):
    price = api.get_price(ids='ethereum', vs_currencies='usd')["ethereum"]["usd"]
    await call.message.answer(f" 1 ETN = {price}")
    await call.message.delete()
    await call.answer()
    keyboard = types.InlineKeyboardMarkup()
    buttons_curr = [
        types.InlineKeyboardButton(text="BTC", callback_data="btc"),
        types.InlineKeyboardButton(text="ETN", callback_data="etn"),
        types.InlineKeyboardButton(text="LTC", callback_data="ltc"),
        types.InlineKeyboardButton(text="Еще", callback_data="more")

    ]
    keyboard.add(*buttons_curr)
    await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)


@dp.callback_query_handler(text="ltc")
async def send_random_value(call: types.CallbackQuery):
    price = api.get_price(ids='litecoin', vs_currencies='usd')["litecoin"]["usd"]
    await call.message.answer(f" 1 LTC = {price}")
    await call.message.delete()
    await call.answer()
    keyboard = types.InlineKeyboardMarkup()
    buttons_curr = [
        types.InlineKeyboardButton(text="BTC", callback_data="btc"),
        types.InlineKeyboardButton(text="ETN", callback_data="etn"),
        types.InlineKeyboardButton(text="LTC", callback_data="ltc"),
        types.InlineKeyboardButton(text="Еще", callback_data="more")

    ]
    keyboard.add(*buttons_curr)
    await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)


@dp.callback_query_handler(text="twt")
async def send_random_value(call: types.CallbackQuery):
    price = api.get_price(ids='trust-wallet-token', vs_currencies='usd')["trust-wallet-token"]["usd"]
    await call.message.answer(f" 1 TWT = {price}")
    await call.message.delete()
    await call.answer()
    keyboard = types.InlineKeyboardMarkup()
    more_btn = [
        types.InlineKeyboardButton(text="TWT", callback_data="twt"),
        types.InlineKeyboardButton(text="BNB", callback_data="bnb"),
        types.InlineKeyboardButton(text="DOT", callback_data="dot"),
        types.InlineKeyboardButton(text="CAKE", callback_data="cake"),
        types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
    ]
    keyboard.add(*more_btn)
    await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)


@dp.callback_query_handler(text="bnb")
async def send_random_value(call: types.CallbackQuery):
    price = api.get_price(ids='binancecoin', vs_currencies='usd')["binancecoin"]["usd"]
    await call.message.answer(f" 1 BNB = {price}")
    await call.message.delete()
    await call.answer()
    keyboard = types.InlineKeyboardMarkup()
    more_btn = [
        types.InlineKeyboardButton(text="TWT", callback_data="twt"),
        types.InlineKeyboardButton(text="BNB", callback_data="bnb"),
        types.InlineKeyboardButton(text="DOT", callback_data="dot"),
        types.InlineKeyboardButton(text="CAKE", callback_data="cake"),
        types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
    ]
    keyboard.add(*more_btn)
    await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)


@dp.callback_query_handler(text="dot")
async def send_random_value(call: types.CallbackQuery):
    price = api.get_price(ids='polkadot', vs_currencies='usd')["polkadot"]["usd"]
    await call.message.answer(f" 1 DOT = {price}")
    await call.message.delete()
    await call.answer()
    keyboard = types.InlineKeyboardMarkup()
    more_btn = [
        types.InlineKeyboardButton(text="TWT", callback_data="twt"),
        types.InlineKeyboardButton(text="BNB", callback_data="bnb"),
        types.InlineKeyboardButton(text="DOT", callback_data="dot"),
        types.InlineKeyboardButton(text="CAKE", callback_data="cake"),
        types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
    ]
    keyboard.add(*more_btn)
    await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)


@dp.callback_query_handler(text="cake")
async def send_random_value(call: types.CallbackQuery):
    price = api.get_price(ids='pancakeswap-token', vs_currencies='usd')["pancakeswap-token"]["usd"]
    await call.message.answer(f" 1 CAKE = {price}")
    await call.message.delete()
    await call.answer()
    keyboard = types.InlineKeyboardMarkup()
    more_btn = [
        types.InlineKeyboardButton(text="TWT", callback_data="twt"),
        types.InlineKeyboardButton(text="BNB", callback_data="bnb"),
        types.InlineKeyboardButton(text="DOT", callback_data="dot"),
        types.InlineKeyboardButton(text="CAKE", callback_data="cake"),
        types.InlineKeyboardButton(text="🔙 Back", callback_data="back")
    ]
    keyboard.add(*more_btn)
    await call.message.answer("🤑Выберите валюту🤑", reply_markup=keyboard)


# @dp.message_handler()
# async def echo_message(msg: types.Message):
#     await bot.send_message(msg.from_user.id, msg.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
