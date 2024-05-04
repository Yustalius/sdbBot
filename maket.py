import telebot
import sqlite3
import random
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

bot = telebot.TeleBot('7029750604:AAEh3Ozvv2BGmDY_VUvQBseulIiPQ-fKP60')
paymentToken = '381764678:TEST:83709'

ticket_price = [LabeledPrice('Билет на SDB PARTY', 35000)]
track_price = [LabeledPrice('Заказать трек', 30000)]

global markupKeyboard
markupKeyboard = ReplyKeyboardMarkup(resize_keyboard=True)

servicesButton = KeyboardButton("КУПИТЬ БИЛЕТ")
markupKeyboard.add(servicesButton)

trackRequestButton = KeyboardButton("ЗАКАЗАТЬ ТРЕК")
markupKeyboard.add(trackRequestButton)

infoButton = KeyboardButton('О нас')
nextPartyButton = KeyboardButton('Когда следующая тусовка?')
markupKeyboard.row(infoButton, nextPartyButton)

global new_track_chat_id
new_track_chat_id = None

global sdb_channel_id
sdb_channel_id = -1002065888143

global track_name
track_name = None

global verified_track_name
verified_track_name = None

global track_query
track_query = False

global track_list
track_list = ["Царица", "Асфальт 8", "Georgian Disco"]

def ticket_invoice(message):
    bot.send_invoice(
        message.chat.id,
        'Билет',
        'Билет на SDB PARTY',
        'TICKET',
        paymentToken,
        'RUB',
        ticket_price,
        photo_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpZa6jHJ1z_tK5mRf2zEUcP3EKl7wL7wDhTv7AYfweEQ&s',
        photo_height=1024,  # !=0/None or picture won't be shown
        photo_width=1024,
        photo_size=1024)

def db_check(message):
    name = message.from_user.first_name
    tg_id = message.from_user.id
    nickname = message.from_user.username

    conn = sqlite3.connect('database/sdb.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT( * ) FROM users WHERE tg_id = ?', (tg_id,))
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute('INSERT INTO users (name, nickname, tg_id) VALUES (?, ?, ?)', (name, nickname, tg_id))
    conn.commit()
    cursor.close()
    conn.close()

def subscribe_check(message):
    subscribe = bot.get_chat_member(sdb_channel_id, message.from_user.id)

    if subscribe.status == "member" or subscribe.status == "creator" or subscribe.status == "administrator":
        return True
    else:
        return False

def list_of_tracks():
    global delete_markup
    delete_markup = InlineKeyboardMarkup()
    delete_track_button = InlineKeyboardButton('Удалить трек', callback_data='delete track')
    delete_markup.add(delete_track_button)

    global text
    text = 'Заказанные треки:'
    i = 1
    for element in track_list:
        text += f'\n{i}. {element}'
        i += 1

def control_panel(message):
    bot.send_message(message.chat.id, 'Панель управления⬇️', reply_markup = markupKeyboard)

@bot.message_handler(commands=['start'])
def start(message):
    subscribe_check(message)
    if subscribe_check(message) == True:
        db_check(message)
        control_panel(message)
    else:
        markup = InlineKeyboardMarkup()
        controlPanelButton = InlineKeyboardButton('Подписался', callback_data='control_panel')
        markup.add(controlPanelButton)

        bot.send_message(message.chat.id, 'Для дальнейшей работы с ботом нужно подписаться на наш канал\n\nhttps://t.me/sdb_party', reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    bot.register_next_step_handler(message, admin)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global track_query
    global verified_track_name

    if callback.data == 'control_panel':
        subscribe_check(callback.message)

        if subscribe_check(callback.message) == True:
            control_panel(callback.message)

    elif callback.data == 'information':
        bot.send_message(callback.message.chat.id, 'Что-то про бот')

    elif callback.data == 'buy another ticket':
        ticket_invoice(callback.message)

    elif callback.data == 'track list':
        list_of_tracks()
        bot.send_message(callback.message.chat.id, text, reply_markup=delete_markup)

    elif callback.data == 'delete track':
        del track_list[0]
        list_of_tracks()
        bot.edit_message_text(text, callback.message.chat.id, callback.message.message_id, reply_markup=delete_markup)

    elif callback.data == 'verify':
        verified_track_name = track_name
        bot.edit_message_text('Трек "' + verified_track_name + '" одобрен', callback.message.chat.id, callback.message.message_id)
        bot.send_message(new_track_chat_id, 'Трек "' + verified_track_name + '" одобрен')
        bot.send_invoice(
            new_track_chat_id,
            'Трек на заказ',
            'Ваш трек одобрен!\nКак только пройдет оплата, мы включим ' + verified_track_name + ' в течение 10-15 минут',
            'TRACK',
            paymentToken,
            'RUB',
            track_price)
        track_query = False

    elif callback.data == 'reject':
        bot.send_message(new_track_chat_id, 'Трек не был одобрен, вы можете выбрать другой трек нажав на кнопку "Заказать трек"')
        bot.edit_message_text('Трек "' + track_name + '" не был одобрен', callback.message.chat.id, callback.message.message_id)
        track_query = False

@bot.message_handler()
def answer(message):
    global track_query

    if message.text.lower() == 'купить билет':
        tg_id = message.from_user.id

        conn = sqlite3.connect('database/sdb.db')
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT( * ) FROM tickets WHERE telegram_id = ?', (tg_id,))
        is_ticket_owner = cursor.fetchone()[0]

        if is_ticket_owner == 0:
            ticket_invoice(message)
        else:
            cursor.execute('SELECT party_name FROM parties')
            party_name = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT( * ) FROM tickets WHERE telegram_id = ?', (tg_id,))
            tickets_amount = cursor.fetchone()[0]

            ticket_markup = InlineKeyboardMarkup()
            another_ticket_button = InlineKeyboardButton('Да', callback_data='buy another ticket')
            ticket_markup.add(another_ticket_button)

            text = f'Вы уже приобрели билет, вы действительно хотите купить еще один билет?\n\n<b>Ваши билеты:</b>'
            for i in range (tickets_amount):
                cursor.execute('SELECT ticket_key FROM tickets WHERE telegram_id = ? LIMIT ? OFFSET ?',
                                   (tg_id, tickets_amount, i))
                text += f'\n• Билет {cursor.fetchone()[0]}'
            bot.send_message(message.chat.id, text, reply_markup=ticket_markup, parse_mode='html')

        conn.commit()
        cursor.close()
        conn.close()

    elif message.text.lower() == 'заказать трек':
        if track_query == False:
            cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_button = InlineKeyboardButton('ОТМЕНА')
            cancel_markup.add(cancel_button)

            track_number = len(track_list)
            bot.send_message(message.chat.id,
                             'Заказ трека стоит 300 рублей, трек можно заказать в таком то стиле такие условия и тд\n' +
                             'Введите трек, который хотите заказать и ждите, пока он пройдет верификацию' +
                             f'\n\nСейчас треков в очереди: {track_number}' +
                             f'\nПримерное время ожидания ~ {track_number * 10} минут', reply_markup=cancel_markup)
            bot.register_next_step_handler(message, track)
        else:
            bot.send_message(message.chat.id, 'Попробуйте позже')

    elif message.text.lower() == 'о нас':
        bot.send_message(message.chat.id, 'Что-то про нас')

    elif message.text.lower() == 'когда следующая тусовка?':
        conn = sqlite3.connect('database/sdb.db')
        cursor = conn.cursor()

        cursor.execute('SELECT party_name, description, date FROM parties LIMIT 1')
        users = cursor.fetchall()

        info = ''
        for element in users:
            info += f'Следующая тусовка: {element[0]}\n\nДата: {element[2]}\n\nОписание:\n{element[1]}'

        cursor.close()
        conn.close()

        bot.send_message(message.chat.id, info)

def admin(message):
    password = '14882012'

    if message.text.strip() == password:
        admin_markup = InlineKeyboardMarkup()
        list_of_tracks_button = InlineKeyboardButton('Список треков', callback_data='track list')
        admin_markup.add(list_of_tracks_button)

        bot.send_message(message.chat.id, 'Панель управления', reply_markup=admin_markup)

def track(message):
    if message.text.lower() == 'отмена':
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.delete_message(message.chat.id, message.message_id)
        control_panel(message)
    else:
        global track_query
        track_query = True

        global track_name
        track_name = message.text.strip()

        global new_track_chat_id
        new_track_chat_id = message.chat.id

        bot.send_message(message.chat.id, 'Ожидайте одобрения трека ', reply_markup = markupKeyboard)

        verification_markup = InlineKeyboardMarkup()
        verifyButton = InlineKeyboardButton('Одобрить', callback_data = 'verify')
        rejectButton = InlineKeyboardButton('Отказать', callback_data = 'reject')
        verification_markup.row(verifyButton, rejectButton)

        bot.send_message(905069756,
                         'Заказали трек ' + track_name + '\n\nДанные:\n' + 'ID: ' + f'{message.from_user.id}' + '\n' + 'Имя: ' + f'{message.from_user.first_name}' + '\n' + 'Ник: @' + f'{message.from_user.username}'
                         , reply_markup = verification_markup)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Что-то пошло не так :(\nПопробуйте еще раз")

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    global verified_track_name
    global track_number

    if message.successful_payment.invoice_payload == 'TICKET':
        tg_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        key = random.randint(0, 9999)

        conn = sqlite3.connect('database/sdb.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO tickets (first_name, username, telegram_id, ticket_key) VALUES (?, ?, ?, ?)', (first_name, username, tg_id, key))

        conn.commit()
        cursor.close()
        conn.close()

        bot.send_message(message.chat.id, 'Вы купили билет! Ваш код: ' + f'{key}', parse_mode='Markdown')

    elif message.successful_payment.invoice_payload == 'TRACK':
        bot.send_message(905069756, '"' + verified_track_name + '" оплатили')
        bot.send_message(message.chat.id, 'Трек успешно оплачен!', parse_mode='Markdown')

        track_list.append(verified_track_name)

bot.infinity_polling()