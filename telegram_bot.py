import telebot
import json
from PIL import Image
import database_functions as dbf
import asyncio
import threading
import schedule
import time
import os
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto



config_file_path = r'venv\config.json'
message_texts_path = 'message_texts.json'

# Загрузка конфигурации и текстов сообщений из файлов
with open(config_file_path, 'r') as config_file, open(message_texts_path, 'r', encoding='utf-8') as message_texts_file:
    config = json.load(config_file)
    message_texts = json.load(message_texts_file)

# Инициализация бота с указанием токена из конфигурации
static_channel_id = config["channel_id"]
bot = telebot.TeleBot(config["tg_token"])

# Декоратор для проверки блокировки пользователя
def check_blocked(func):
    def wrapper(*args, **kwargs):
        message = args[0]  # Первый аргумент - message
        user_id = message.from_user.id
        if dbf.is_blocked(user_id):
            bot.send_message(user_id, "Ваш доступ к боту ограничен. Обратитесь к администратору.")
            return
        else:
            return func(*args, **kwargs)  # Передаем все аргументы в оборачиваемую функцию
    return wrapper

# Проверка новый ли юзер
def is_new_user(message):
    username = message.from_user.username
    user_id = message.from_user.id
    user_data = dbf.select("users", "*", "WHERE user_id=?", (user_id,))
    if username == None:
        bot.send_message(message.from_user.id, "Чтобы начать пользоваться ботом, укажите 'Имя пользователя' в настройках Телеграм ")
        return
    if user_data == []:
        dbf.insert("users", "user_id, username", (user_id, username))

#Создание и отправка карточки лота в канал
def channel_create_lot(lot_info=None, message_id=None, new_ninja=None):
    keyboard = InlineKeyboardMarkup()
    info_button = InlineKeyboardButton("ℹ️", callback_data=f"info:{lot_info[0]}")
    starting_time_button = InlineKeyboardButton("🕒", callback_data=f"time:{lot_info[0]}")
    images = lot_info[1].split(", ")
    end_time = datetime.strptime(lot_info[7], "%Y-%m-%d %H:%M:%S")
    current_datetime = datetime.now()
    channel_id = static_channel_id
    open_lot_button = InlineKeyboardButton("Открыть лот", callback_data=f"open_lot:{lot_info[0]}", url=f"http://t.me/AuctionBotAtt_bot?start={lot_info[0]}")
    keyboard.row(starting_time_button, info_button)
    keyboard.add(open_lot_button)

    bet_info = dbf.select("lots", "current_bet, ninja_bet", "WHERE id = ?", (lot_info[0],))[0]
    if new_ninja:
        bet_info = (lot_info[12], lot_info[14])
    if bet_info[0] and bet_info[0] != None:
        current_bet = bet_info[0]
    else:
        current_bet = 0

    next_bet = round((current_bet + calculate_min_increase(current_bet)), -1)
    lot_card_text = f"{lot_info[5]}\n{lot_info[4]}\nПродавец: {lot_info[3]}\n\n\n"
    lot_card_text += f"<b>Следующая ставка:</b> {next_bet}₽"

    if current_datetime > end_time:
        lot_card_text += f"\n<b>Аукцион завершен</b>"

    top_bets_text = top_bet_text(lot_info[0])
    if top_bets_text and top_bets_text != None:
        lot_card_text += top_bets_text

    if len(images) > 1:
        # Открываем первое изображение и создаем основу для объединенного изображения
        combined_image = Image.open(images[0])
        width, height = combined_image.size

        # Вычисляем ширину и высоту объединенного изображения
        combined_width = width * len(images)
        combined_height = height

        # Создаем новое изображение с нужными размерами для всех изображений
        combined_image = Image.new('RGB', (combined_width, combined_height))

        # Изменяем размер каждого изображения, чтобы они имели одинаковые размеры
        for i, image_path in enumerate(images):
            img = Image.open(image_path)
            img = img.resize((width, height))
            combined_image.paste(img, (width * i, 0))

        # Сохраняем объединенное изображение
        combined_image.save("combined_image.jpg")

        combined_image_path = "combined_image.jpg"

        image = combined_image_path
    else:
        image = images[0]
    with open(image, 'rb') as photo:
        if message_id:
            try:
                bot.edit_message_caption(chat_id=channel_id, caption=lot_card_text, message_id=message_id,
                                        reply_markup=keyboard,
                                        parse_mode="HTML")
            except telebot.apihelper.ApiTelegramException as e:
                if "message is not modified" in str(e):
                    pass
        else:
            sent_message = bot.send_photo(chat_id=channel_id, photo=photo, caption=lot_card_text, reply_markup=keyboard, parse_mode="HTML")
            dbf.update("lots", ("message_id", sent_message.message_id), ("id", lot_info[0]))
            dbf.update("lots", ("status", "одобрен"), ("id", lot_info[0]))

#Отправка фотографий отдельно
@bot.callback_query_handler(func=lambda call: call.data.startswith(("show_photo:",)))
@check_blocked
def send_photo(call):
    if call.data.startswith("show_photo:"):
        lot_id = call.data.split(":")[1]
        chat_id = call.from_user.id
        images = dbf.select("lots", "images", "WHERE id = ?", (lot_id,))[0][0].split(", ")
        media_group = []
        for image in images:
            media = InputMediaPhoto(open(image, 'rb'))
            media_group.append(media)
        bot.send_media_group(chat_id, media_group)
        bot.answer_callback_query(call.id, "✅Отправили вам фото")

#Создание и отправка карточки лота в личный чат с ботом
def bot_create_lot(username, lot_info=None, chat_id=None, message_id=None, new_ninja=None):
    keyboard = InlineKeyboardMarkup()

    info_button = InlineKeyboardButton("ℹ️", callback_data=f"info:{lot_info[0]}")
    starting_time_button = InlineKeyboardButton("🕒", callback_data=f"time:{lot_info[0]}")

    images = lot_info[1].split(", ")
    attached_files = lot_info[9]

    do_bet_button = InlineKeyboardButton("Сделать ставку", callback_data=f"do_bet:{lot_info[0]}")
    ninja_bet_button = InlineKeyboardButton("Настроить скрытую ставку", callback_data=f"ninja_bet:{lot_info[0]}:{message_id}:")
    show_photo_button = InlineKeyboardButton("Смотреть фото", callback_data=f"show_photo:{lot_info[0]}")

    keyboard.row(starting_time_button, info_button)
    keyboard.add(do_bet_button)
    keyboard.add(ninja_bet_button)
    keyboard.add(show_photo_button)
    if attached_files:
        show_attached_files = InlineKeyboardButton("Прикрепленные файлы", callback_data=f"show_attached_files:{lot_info[0]}")
        keyboard.add(show_attached_files)
    bet_info = dbf.select("lots", "current_bet, ninja_bet", "WHERE id = ?", (lot_info[0],))[0]
    if new_ninja:
        bet_info = (lot_info[12], lot_info[14])
    if bet_info[0] and bet_info[0] != None:
        current_bet = bet_info[0]
    else:
        current_bet = 0

    next_bet = round((current_bet + calculate_min_increase(current_bet)), -1)

    lot_card_text = f"{lot_info[5]}\n{lot_info[4]}\nПродавец: {lot_info[3]}\n\n\n"
    lot_card_text += f"<b>Следующая ставка:</b> {next_bet}₽"

    if bet_info[1]:
        ninja_bets = json.loads(bet_info[1])
        if ninja_bets and username in ninja_bets.keys():
            lot_card_text += f"\n\n<b>Ваша скрытая ставка:</b> {ninja_bets[username]}₽"
    top_bets = top_bet_text(lot_info[0])
    if top_bets and top_bets != None:
        lot_card_text += top_bets
    if len(images) > 1:
        # Открываем первое изображение и создаем основу для объединенного изображения
        combined_image = Image.open(images[0])
        width, height = combined_image.size

        # Вычисляем ширину и высоту объединенного изображения
        combined_width = width * len(images)
        combined_height = height

        # Создаем новое изображение с нужными размерами для всех изображений
        combined_image = Image.new('RGB', (combined_width, combined_height))

        # Изменяем размер каждого изображения, чтобы они имели одинаковые размеры
        for i, image_path in enumerate(images):
            img = Image.open(image_path)
            img = img.resize((width, height))
            combined_image.paste(img, (width * i, 0))

        # Сохраняем объединенное изображение
        combined_image.save("combined_image.jpg")

        combined_image_path = "combined_image.jpg"

        image = combined_image_path
    else:
        image = images[0]

    save_lot_id = dbf.select("users", "lots_ids, bot_chat_id", "WHERE username=?", (username,))[0]
    save_lot_id_json = save_lot_id[0] if save_lot_id[0] else "{}"
    save_id = json.loads(save_lot_id_json)
    with open(image, 'rb') as photo:
        if message_id:
            sent_message = bot.edit_message_caption(chat_id=chat_id, caption=lot_card_text, message_id=message_id, reply_markup=keyboard,
                                      parse_mode="HTML")
        else:
            sent_message = bot.send_photo(chat_id=chat_id, photo=photo, caption=lot_card_text, reply_markup=keyboard,
                           parse_mode="HTML")

        save_id[str(lot_info[0])] = sent_message.message_id
        dbf.update("users", ("lots_ids", json.dumps(save_id)), ("username", username))
        if not save_lot_id[1]:
            dbf.update("users", ("bot_chat_id", chat_id), ("username", username))

#Удаление лота при снятии его с аукциона
def delete_lot(lot_id):
    participate_users = dbf.select("users", "*", f"WHERE lots_ids LIKE '%\"{lot_id}\"%'", ())
    lot_message_id = dbf.select("lots", "message_id", "WHERE id = ?", (lot_id,))[0]
    if participate_users:
        for user in participate_users:
            user_message_id = json.loads(user[3])
            bot.edit_message_caption(chat_id=user[5], message_id=user_message_id[str(lot_id)], caption="Лот был снят с аукциона приносим свои извинения.")
            del user_message_id[lot_id]
            dbf.update("users", ("lots_ids", json.dumps(user_message_id)), ("id", user[0]))
    bot.delete_message(chat_id=static_channel_id, message_id=lot_message_id)
    return

# Асинхронно дожидается создание лота из буффера
async def schedule_lot(lot_info):
    # Получаем дату и время из колонки "buffer"
    buffer_datetime = datetime.strptime(lot_info[10], '%Y-%m-%d %H:%M')
    current_datetime = datetime.now()

    # Вычисляем время до отправки лота
    delay_seconds = (buffer_datetime - current_datetime).total_seconds()

    if delay_seconds > 0:
        # Ждем указанное время
        await asyncio.sleep(delay_seconds)

    # Отправляем лот после ожидания
    channel_create_lot(lot_info=lot_info)

# Расчет минимального повышения цены для след. ставки
def calculate_min_increase(current_bid):
    base_increase = 20  # Базовое значение минимального повышения
    thresholds = [200]  # Пороговые значения
    increase_ratio = 0.1  # Коэффициенты для изменения правил
    min_increase = base_increase
    for i, threshold in enumerate(thresholds):
        if int(current_bid) > threshold:
            thresholds.append(threshold*2)
            # Если текущая ставка превышает пороговое значение, применяем новые правила
            min_increase = max(current_bid * increase_ratio, min_increase)
    return min_increase

#Форммирование текста 3 последних ставок на лот
def top_bet_text(lot_id):
    all_bets_lot = dbf.select("lots", "all_bets", "WHERE id = ?", (lot_id,))[0][0]
    all_bets_json = all_bets_lot if all_bets_lot else "{}"
    all_bets = json.loads(all_bets_json)

    sorted_bets = sorted(all_bets.items(), key=lambda x: x[1], reverse=True)

    # Получаем топ-3 ставки
    top_3_bets = sorted_bets[:3]
    if top_3_bets == [] or top_3_bets == []:
        return
    # Добавляем информацию о топ-3 ставках в текст карточки лота
    top_bets_text = "\n\nТоп-3 ставок:\n"
    emojis = ["🥇", "🥈", "🥉"]
    for index, (username, bet) in enumerate(top_3_bets):
        emoji = emojis[index] if index < len(emojis) else ""
        top_bets_text += f"{emoji}{bet}₽ ({username[:3]})***\n"

    return top_bets_text

# Отправка прикрепленных файлов
@bot.callback_query_handler(func=lambda call: call.data.startswith("show_attached_files:"))
@check_blocked
def show_attached_files(call):
    # Извлекаем lot_id из call.data
    lot_id = call.data.split(":")[1]

    # Получаем строку с путями прикрепленных файлов из базы данных
    attached_files_info = dbf.select("lots", "attached_files", "WHERE id=?", (lot_id,))
    if attached_files_info:
        attached_files_str = attached_files_info[0][0]

        # Разделяем строку по запятым
        attached_files_paths = attached_files_str.split(',')
        # Отправляем каждый файл как документ
        for file_path in attached_files_paths:
            try:
                with open(file_path.strip(), "rb") as file:
                    # Проверяем, не пуст ли файл
                    if os.path.getsize(file_path.strip()) > 0:
                        bot.send_document(call.from_user.id, file)
                    else:
                        bot.answer_callback_query(callback_query_id=call.id, text=f"Файл '{file_path.strip()}' пуст.")
            except FileNotFoundError:
                bot.answer_callback_query(callback_query_id=call.id, text=f"Файл '{file_path.strip()}' не найден.")
        bot.answer_callback_query(callback_query_id=call.id, text=f"Отправили вам прикрепленные файлы.")
    else:
        bot.send_message(call.from_user.id, "Нет прикрепленных файлов для этого лота.")

# Обработчик "Сделать ставку" и автоставки
@bot.callback_query_handler(func=lambda call: call.data.startswith("do_bet:"))
@check_blocked
def do_bet_handler(call=None, message_id=None, info=None, new_ninja_bet=None, new_ninja_bet_username=None):
    if call:
        lot_id = call.data.split(":")[1]
        user_username = call.from_user.username
        chat_id = call.from_user.id
        if message_id:
            message_id = message_id
        else:
            message_id = call.message.message_id
    else:
        lot_id, user_username, call_username = info
        chat_info = dbf.select("users", "bot_chat_id, lots_ids", "WHERE username=?", (user_username,))
        chat_id = chat_info[0][0]
        message_id = json.loads(chat_info[0][1])[lot_id]
        call_info = dbf.select("users", "bot_chat_id, lots_ids", "WHERE username=?", (call_username,))
        call_chat_id = call_info[0][0]
        call_message_id = json.loads(call_info[0][1])[lot_id]

    # Получаем информацию о лоте из базы данных
    lot_info = dbf.select("lots", "*", "WHERE id = ?", (lot_id,))[0]

    end_time = datetime.strptime(lot_info[7], "%Y-%m-%d %H:%M:%S")
    current_datetime = datetime.now()
    if current_datetime > end_time:
        bot.answer_callback_query(callback_query_id=call.id, text="Аукцион завершен.")
        channel_create_lot(lot_info=lot_info, message_id=lot_info[15])
        return
    elif (end_time - datetime.now()).total_seconds() <= 600:
        # Если да, обновляем время окончания на 10 минут вперед
        end_time += timedelta(minutes=10)
        dbf.update("lots", ("end_time", end_time), ("id", lot_id))

    ninja_bets = dbf.select("lots", "ninja_bet", "WHERE id = ?", (lot_id,))[0][0]
    if ninja_bets:
        ninja_bets = json.loads(ninja_bets)

    # Получаем текущее значение колонки all_bets
    all_bets_json = lot_info[13] if lot_info[13] else "{}"
    all_bets = json.loads(all_bets_json)

    # Определяем следующую ставку
    current_bet = lot_info[12] if lot_info[12] and lot_info[12] != None else 0
    min_increase = calculate_min_increase(current_bet)
    new_current_bet = round((current_bet + min_increase), -1)
    if new_ninja_bet:
        if new_ninja_bet_username:
            second_max_ninja_bet_username, second_max_ninja_bet = max(ninja_bets.items(), key=lambda x: x[1])
            new_current_bet = second_max_ninja_bet + calculate_min_increase(second_max_ninja_bet)
            if new_current_bet > new_ninja_bet:
                new_current_bet = new_ninja_bet
            ninja_bets[new_ninja_bet_username] = new_ninja_bet

            all_bets[second_max_ninja_bet_username] = second_max_ninja_bet
            all_bets[new_ninja_bet_username] = new_current_bet

            lot_info = lot_info[:12] + (new_current_bet,) + (json.dumps(all_bets),) + (json.dumps(ninja_bets),) + lot_info[15:]

            for_second_save_messages_ids, for_second_chat_id = dbf.select("users", "lots_ids, bot_chat_id", "WHERE username=?", (second_max_ninja_bet_username,))[0]
            for_second_save_message_id = json.loads(for_second_save_messages_ids)[str(lot_info[0])]

            for_new_save_messages_ids, for_new_chat_id = dbf.select("users", "lots_ids, bot_chat_id", "WHERE username=?", (new_ninja_bet_username,))[0]
            for_new_save_message_id = json.loads(for_new_save_messages_ids)[str(lot_info[0])]

            dbf.update("lots", ("all_bets", json.dumps(all_bets)), ("id", lot_id))
            dbf.update("lots", ("current_bet", new_current_bet), ("id", lot_id))
            dbf.update("lots", ("ninja_bet", json.dumps(ninja_bets)), ("id", lot_id))
            dbf.update("lots", ("current_lot_winner", new_ninja_bet_username), ("id", lot_id))

            bot_create_lot(lot_info=lot_info, message_id=for_second_save_message_id, chat_id=for_second_chat_id, username=second_max_ninja_bet_username, new_ninja=True)
            bot_create_lot(lot_info=lot_info, message_id=for_new_save_message_id, chat_id=for_new_chat_id,
                     username=new_ninja_bet_username, new_ninja=True)
            channel_create_lot(lot_info=lot_info, message_id=lot_info[15], new_ninja=True)
            send_bet_notification(second_max_ninja_bet_username, lot_id[0])
            return
        else:
            new_current_bet = new_ninja_bet

    if all_bets == {} or all_bets == None:
        is_highest_bet = False
    elif len(all_bets.values()) == 1 and user_username in all_bets.keys() or user_username == max(all_bets, key=all_bets.get):
        is_highest_bet = True
    else:
        all_bets[user_username] = new_current_bet
        is_highest_bet = new_current_bet > max(all_bets.values()) and all_bets.get(user_username, 0) == max(all_bets.values())
        if is_highest_bet == False and len(all_bets.values()) > 1:
            max_bet_username, max_bet_value = sorted(all_bets.items(), key=lambda x: x[1], reverse=True)[1]
            call_info = dbf.select("users", "bot_chat_id, lots_ids", "WHERE username=?", (max_bet_username,))
            call_chat_id = call_info[0][0]
            call_message_id = json.loads(call_info[0][1])[lot_id]
            message_id = json.loads(dbf.select("users", "lots_ids", "WHERE username=?", (user_username,))[0][0])[lot_id]
            if ninja_bets:
                if type(ninja_bets) == str:
                    ninja_bets = json.loads(ninja_bets)
                if not max_bet_username in ninja_bets.keys() and call:
                    send_bet_notification(max_bet_username, lot_id)
                elif max_bet_username in ninja_bets.keys() and max(ninja_bets.values()) < current_bet:
                    send_bet_notification(max_bet_username, lot_id)
            else:
                send_bet_notification(max_bet_username, lot_id)
    # Если ставка пользователя самая высокая, отправляем уведомление об этом
    if is_highest_bet:
        notification_text = "Ваша и так самая высокая."
        bot.answer_callback_query(call.id, text=notification_text)
        return

    all_bets[user_username] = new_current_bet
    # Обновляем значение колонки all_bets в базе данных
    dbf.update("lots", ("all_bets", json.dumps(all_bets)), ("id", lot_id))
    dbf.update("lots", ("current_bet", all_bets[user_username]), ("id", lot_id))
    dbf.update("lots", ("current_lot_winner", user_username), ("id", lot_id))

    # Отправляем сообщение с обновленными данными о лоте
    bot_create_lot(lot_info=lot_info, message_id=message_id, chat_id=chat_id, username=user_username)
    if len(all_bets.values()) > 1:
        if call:
            bot_create_lot(lot_info=lot_info, message_id=call_message_id, chat_id=call_chat_id, username=max_bet_username)
        else:
            bot_create_lot(lot_info=lot_info, message_id=call_message_id, chat_id=call_chat_id, username=call_username)

    channel_create_lot(lot_info=lot_info, message_id=lot_info[15])

    # Получаем информацию о скрытых ставках
    if ninja_bets:
        if type(ninja_bets) == str:
            ninja_bets = json.loads(ninja_bets)
        ninja_bet_username, ninja_bet = max(ninja_bets.items(), key=lambda x: x[1])
        if (new_current_bet + calculate_min_increase(new_current_bet)) < ninja_bet and ninja_bet_username != user_username:
            # Отправляем уведомление последнему ставившему пользователю
            send_bet_notification(username=user_username, lot_id=lot_id, current_bet=new_current_bet, ninja_bet_username=ninja_bet_username, message_id=message_id)

# Отправка уведомлений пользователям чьи ставки перебили
def send_bet_notification(username, lot_id, current_bet=None, message_id=None, ninja_bet_username=None):
    # Получаем идентификатор чата пользователя с ботом
    user_chat_id = dbf.select("users", "bot_chat_id", "WHERE username=?", (username,))[0][0]
    if not user_chat_id:
        return  # Выход, если идентификатор чата не найден

    # Получаем идентификатор сообщения в чате пользователя для данного лота
    lot_message_id = json.loads(dbf.select("users", "lots_ids", "WHERE username=?", (username,))[0][0]).get(
        str(lot_id))
    if not lot_message_id:
        return  # Выход, если идентификатор сообщения не найден

    # Отправляем уведомление пользователю
    notification_text = f"Ваша ставка на лот была перебита."
    bot.send_message(user_chat_id, notification_text, reply_to_message_id=lot_message_id)
    if current_bet:
        info = (lot_id, ninja_bet_username, username)
        do_bet_handler(info=info, message_id=message_id)


current_ninja_bet = {}
#Обработчик и вся логика скрытых ставок(автоставок)
@bot.callback_query_handler(
    func=lambda call: call.data.startswith(("ninja_bet:", "add:", "cancel_ninja_bet", "save_ninja_bet")))
@check_blocked
def ninja_bet_handler(call):
    global current_ninja_bet
    lot_id = call.data.split(":")[1]
    message_id = call.message.message_id
    user_username = call.from_user.username
    user_winned_lots = dbf.select("lots", "id", "WHERE status = 'завершен' AND current_lot_winner = ?", (user_username,))
    user_balance = dbf.select("users", "balance", "WHERE username = ?", (user_username,))
    if len(user_winned_lots) < 10 and int(user_balance[0][0]) < 500:
        bot.answer_callback_query(callback_query_id=call.id, text=message_texts["ninja_bet_text"])
        return

    if call.data.startswith("add:"):
        current_ninja_bet[user_username] += int(call.data.split(":")[2])

    elif call.data.startswith("cancel_ninja_bet"):
        cancel_answer = lambda: bot.answer_callback_query(call.id, "Текущая скрытая ставка сброшена")
        if current_ninja_bet[user_username] == 0:
            cancel_answer()
            return
        current_ninja_bet[user_username] = 0
        cancel_answer()

    elif call.data.startswith("save_ninja_bet"):
        # Получаем текущее значение скрытых ставок из базы данных
        lot_info = dbf.select("lots", "*", "WHERE id = ?", (lot_id,))[0]
        all_bets_json = lot_info[13] if lot_info[13] else "{}"
        all_bets = json.loads(all_bets_json)
        ninja_bet_json = lot_info[14] if lot_info[14] else "{}"
        ninja_bets = json.loads(ninja_bet_json)
        save_messages_ids = dbf.select("users", "lots_ids", "WHERE username=?", (user_username,))[0][0]
        save_message_id = json.loads(save_messages_ids)[str(lot_info[0])]
        # Если есть ставки
        if all_bets.values():
            # Пользователь с максимальной ставкой и ставка
            max_bet_username, max_bet_value = max(all_bets.items(), key=lambda x: x[1])
            # Если есть скрытые ставки
            if ninja_bets.values():
                # Если выбранная ставка больше текущей ставки(обычной)
                if current_ninja_bet[user_username] > max_bet_value:
                    # Пользователь с максимальной скрытой ставкой и скрытая ставка
                    max_ninja_bet_username, max_ninja_bet = max(ninja_bets.items(), key=lambda x: x[1])
                    # Если пользователь перебивает свою же скрытую ставку
                    if max_ninja_bet_username == user_username:
                        bot.answer_callback_query(call.id, "Ваша скрытая ставка сохранена.")
                        ninja_bets[user_username] = current_ninja_bet[user_username]
                        dbf.update("lots", ("ninja_bet", json.dumps(ninja_bets)), ("id", lot_id))
                        current_ninja_bet[user_username] = 0
                        bot.delete_message(call.from_user.id, call.message.message_id)
                        return
                    # Получение id слотов пользователя с максимальной скрытой ставкой
                    max_ninja_bet_save_messages_ids = dbf.select("users", "lots_ids", "WHERE username=?", (max_bet_username,))[0][0]
                    max_ninja_bet_save_message_id = json.loads(max_ninja_bet_save_messages_ids)[str(lot_info[0])]

                    ninja_bets[user_username] = current_ninja_bet[user_username]
                    # Если скрытая ставка меньше или равна максимальной скрытой ставке
                    if ninja_bets[user_username] < max_ninja_bet:
                        do_bet_handler(call, int(save_message_id), new_ninja_bet=ninja_bets[user_username])
                    # Если скрытая ставка больше максимальной скрытой ставки
                    elif ninja_bets[user_username] >= max_ninja_bet:
                        info = (lot_id, user_username, max_ninja_bet_username)
                        do_bet_handler(call=call, message_id=int(max_ninja_bet_save_message_id), info=info,
                                       new_ninja_bet=ninja_bets[user_username],
                                       new_ninja_bet_username=user_username)

                    ninja_bets[user_username] = current_ninja_bet[user_username]
                    dbf.update("lots", ("ninja_bet", json.dumps(ninja_bets)), ("id", lot_id))
                    bot.delete_message(call.from_user.id, call.message.message_id)
                    current_ninja_bet[user_username] = 0
                    return
                else:
                    bot.answer_callback_query(call.id, f"Ваша скрытая ставка должна быть выше текущей ставки.")
                    bot.delete_message(call.from_user.id, call.message.message_id)
                    current_ninja_bet[user_username] = 0
                    return

        ninja_bets[user_username] = current_ninja_bet[user_username]
        dbf.update("lots", ("ninja_bet", json.dumps(ninja_bets)), ("id", lot_id))
        # Если id лота в id_lots пользователя
        if str(lot_info[0]) in json.loads(save_messages_ids).keys():
            bot_create_lot(username=user_username, lot_info=lot_info, chat_id=call.from_user.id,
                     message_id=int(save_message_id))
        else:
            bot_create_lot(username=user_username, lot_info=lot_info, chat_id=call.from_user.id,
                     message_id=message_id - 1)
        bot.delete_message(call.from_user.id, call.message.message_id)
        current_ninja_bet[user_username] = 0
        # После сохранения скрытой ставки, вызываем обработчик do_bet_handler для обновления ставок
        try:
            save_message_id = json.loads(save_messages_ids)[str(lot_info[0])]
            do_bet_handler(call, int(save_message_id))
        except:
            do_bet_handler(call, message_id=message_id - 1)

    ninja_bet_text = f"❔ Ваша максимальная сумма, до которой будет идти скрытая ставка: {current_ninja_bet.get(user_username, 0)}₽\nТут ты можешь изменить эту скрытую ставку:"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("10₽", callback_data=f"add:{lot_id}:10:{message_id}"),
                 InlineKeyboardButton("50₽", callback_data=f"add:{lot_id}:50:{message_id}"),
                 InlineKeyboardButton("100₽", callback_data=f"add:{lot_id}:100:{message_id}"))
    keyboard.add(InlineKeyboardButton("500₽", callback_data=f"add:{lot_id}:500:{message_id}"),
                 InlineKeyboardButton("1000₽", callback_data=f"add:{lot_id}:1000:{message_id}"),
                 InlineKeyboardButton("5000₽", callback_data=f"add:{lot_id}:5000:{message_id}"))
    keyboard.add(InlineKeyboardButton("Сбросить скрытую ставку", callback_data=f"cancel_ninja_bet:{lot_id}"),
                 InlineKeyboardButton("Сохранить скрытую ставку", callback_data=f"save_ninja_bet:{lot_id}"))

    if call.data.startswith("ninja_bet:"):
        current_ninja_bet[user_username] = 0
        bot.answer_callback_query(call.id, "Отправили вам настройки скрытой ставки")
        bot.send_message(call.from_user.id, ninja_bet_text, reply_markup=keyboard)

    elif call.data.startswith(("ninja_bet:", "add:")):
        bot.edit_message_text(chat_id=call.from_user.id, message_id=message_id, text=ninja_bet_text,
                              reply_markup=keyboard)

    elif call.data.startswith("cancel_ninja_bet"):
        bot.edit_message_text(chat_id=call.from_user.id, message_id=message_id, text=ninja_bet_text,
                              reply_markup=keyboard)

# Обработчик нажатия на кнопки info о лоте и время
@bot.callback_query_handler(func=lambda call: call.data.startswith(("info:", "time:")))
@check_blocked
def info_n_time_handler(call):
    lot_id = call.data.split(":")[1]
    if call.data.startswith("info:"):
        bot.answer_callback_query(call.id, message_texts["info_text"], show_alert=True)
    elif call.data.startswith("time:"):
        time_before_lot = dbf.select("lots", "start_time, end_time", "WHERE id = ?", (lot_id,))[0]
        start_time, end_time = time_before_lot
        # Преобразуем строки времени в объекты datetime
        start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        # Получаем текущее время
        current_datetime = datetime.now()

        # Вычисляем разницу между текущим временем и временем начала/окончания аукциона
        if current_datetime < start_datetime:
            time_difference = start_datetime - current_datetime
            time_text = f"До начала аукциона {time_difference.days} дней {time_difference.seconds // 3600} часов {time_difference.seconds // 60 % 60} минут {time_difference.seconds % 60} секунд"
        elif current_datetime < end_datetime:
            time_difference = end_datetime - current_datetime
            time_text = f"Осталось {time_difference.days} дней {time_difference.seconds // 3600} часов {time_difference.seconds // 60 % 60} минут {time_difference.seconds % 60} секунд"
        else:
            time_text = "Аукцион уже завершен"

        # Отправляем текстовое сообщение с информацией о времени
        bot.answer_callback_query(call.id, time_text)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
@check_blocked
def handle_start(message, message_id=None):
    is_new_user(message)
    if message.from_user.username == None:
        return
    command_text = message.text
    command_parts = command_text.split()
    if len(command_parts) > 1 and "/start" in command_parts:
        parameter = command_parts[1]
        lot_info = dbf.select("lots", "*", "WHERE id = ?", (parameter,))[0]
        bot_create_lot(lot_info=lot_info, chat_id=message.from_user.id, username=message.from_user.username)
    else:
        message_text = message_texts["start_message"]

        keyboard = InlineKeyboardMarkup()

        my_lots_button = InlineKeyboardButton("Мои лоты", callback_data=f"m_my_lots:")
        rules_button = InlineKeyboardButton("Правила", callback_data=f"m_rules:")
        help_button = InlineKeyboardButton("Помощь", callback_data=f"m_help:")
        balance_button = InlineKeyboardButton("Баланс", callback_data=f"m_balance:")

        keyboard.add(my_lots_button)
        keyboard.add(balance_button)
        keyboard.add(rules_button, help_button)

        if message_id:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message_id, text=message_text, reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, message_text, reply_markup=keyboard)

# Обработчик нажатий на кнопки меню
@bot.callback_query_handler(func=lambda call: call.data.startswith("m_"))
@check_blocked
def main_menu_handler(call):
    message_id = call.message.message_id

    back_keyboard = InlineKeyboardMarkup()
    # Получаем информацию о лотах пользователя из базы данных
    back_main_menu_button = InlineKeyboardButton("Главное меню", callback_data=f"back_main_menu:{message_id}")

    if call.data.startswith("m_my_lots:"):
        message_text = message_texts["my_lots_message"]

        user_lots_info = dbf.select("lots", "*", "WHERE all_bets LIKE ? ORDER BY id DESC LIMIT 10",
                                    (f'%"{call.from_user.username}"%',))

        for lot_info in user_lots_info:
            lot_id = lot_info[0]
            all_bets_str = lot_info[13]  # Получаем строку с информацией о ставках в лоте
            all_bets_dict = json.loads(all_bets_str)  # Преобразуем строку в словарь
            # Проверяем, участвует ли пользователь в данном лоте
            if call.from_user.username in all_bets_dict.keys():
                # Создаем кнопку для лота, если пользователь участвует в нем
                back_keyboard.add(InlineKeyboardButton(f"{lot_info[5]}", callback_data=f"use_lot:{lot_id}"))
        back_keyboard.add(back_main_menu_button)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=message_text,
                          reply_markup=back_keyboard)
    elif call.data.startswith("m_rules:"):
        message_text = message_texts["rules_message"]
        back_keyboard.add(back_main_menu_button)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=message_text,
                              reply_markup=back_keyboard)
    elif call.data.startswith("m_help:"):
        message_text = message_texts["help_message"]
        back_keyboard.add(back_main_menu_button)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=message_text,
                              reply_markup=back_keyboard)

    elif call.data.startswith("m_balance:"):
        user_balance = dbf.select("users", "balance", "WHERE user_id = ?", (call.from_user.id,))[0][0]
        message_text = f"Ваш баланс: {user_balance}"
        refill_balance_button = InlineKeyboardButton("Пополнить балнс", callback_data=f"m_refill_balance:{user_balance}")
        back_keyboard.add(refill_balance_button)
        back_keyboard.add(back_main_menu_button)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=message_text,
                              reply_markup=back_keyboard)

    elif call.data.startswith("m_refill_balance:"):
        user_balance = int(call.data.split(":")[1]) + 1000
        dbf.update("users", ("balance", user_balance), ("user_id", call.from_user.id))
        message_text = f"Ваш баланс: {user_balance}"
        back_keyboard.add(back_main_menu_button)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=message_text,
                              reply_markup=back_keyboard)

# Обработчик нажатий на кнопки back
@bot.callback_query_handler(func=lambda call: call.data.startswith("use_lot:"))
@check_blocked
def use_lot(call):
    lot_id = call.data.split(":")[1]
    lot_info = dbf.select("lots", "*", "WHERE id = ?", (lot_id,))[0]
    bot_create_lot(call.from_user.username, lot_info, call.from_user.id)

# Обработчик нажатий на кнопки back
@bot.callback_query_handler(func=lambda call: call.data.startswith("back_"))
@check_blocked
def back_handler(call):
    message_data = call.data.replace("back_", "")
    message_id = call.data.split(":")[1]
    if message_data.startswith("main_menu:"):
        handle_start(call.message, message_id)

if __name__ != "__main__":
    bot.stop_bot()
    print("Stoped")
else:
    # Запуск бота
    print("Ready")
    if __name__ == "__main__":
        def check_database():
            buffer_lots = dbf.select("lots", "*", "WHERE buffer IS NOT NULL AND waiting_publication = ?", (0,))
            current_time = datetime.now()
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            ended_lots = dbf.select("lots", "*", "WHERE end_time <= ? AND status != ?", (current_time_str, "завершен"))
            if ended_lots:
                for lot in ended_lots:
                    admin_balance = dbf.select("finances", "current_balance",
                                               "WHERE id = (SELECT id FROM finances ORDER BY id DESC LIMIT 1)", ())[0][0]
                    lot_current_bet = dbf.select("lots", "current_bet, start_price", "WHERE id = ?", (lot[0],))[0]
                    if lot_current_bet[0] == None:
                        lot_current_bet = lot_current_bet[1]
                    else:
                        lot_current_bet = lot_current_bet[0]
                    five_percent = int(lot_current_bet) * 0.05
                    new_current_balance = int(admin_balance) - five_percent
                    dbf.insert("finances", "current_balance, lot_id, count, comment", (new_current_balance, lot[0],
                                                                                       f"-{five_percent}",
                                                                                       "Завершение аукциона."))
                    dbf.update("lots", ("status", "завершен"), ("id", lot[0]))

            if buffer_lots:
                for lot_info in buffer_lots:
                    dbf.update("lots", ("waiting_publication", 1), ("id", lot_info[0]))
                    buffer_datetime = datetime.strptime(lot_info[10], '%Y-%m-%d %H:%M')
                    delay_seconds = (buffer_datetime - datetime.now()).total_seconds()
                    if delay_seconds <= 360:
                        asyncio.run(schedule_lot(lot_info))
            print("Checking database...")


        def schedule_check():
            schedule.every(1).minutes.do(check_database)

            while True:
                schedule.run_pending()
                time.sleep(1)

        schedule_thread = threading.Thread(target=schedule_check)
        schedule_thread.start()
    bot.infinity_polling()
