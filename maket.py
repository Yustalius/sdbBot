import telebot
import sqlite3
import random
import io
from datetime import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

bot = telebot.TeleBot('7029750604:AAEh3Ozvv2BGmDY_VUvQBseulIiPQ-fKP60')
paymentToken = '381764678:TEST:83709'

global markupKeyboard
markupKeyboard = ReplyKeyboardMarkup(resize_keyboard=True)
# servicesButton = KeyboardButton("КУПИТЬ БИЛЕТ🎫")
# markupKeyboard.add(servicesButton)
trackRequestButton = KeyboardButton("ЗАКАЗАТЬ ТРЕК🎶")
markupKeyboard.add(trackRequestButton)
infoButton = KeyboardButton('О SDBℹ️')
nextPartyButton = KeyboardButton('Когда следующая тусовка?🧐')
markupKeyboard.row(infoButton, nextPartyButton)

global delete_track_markup
delete_track_markup = InlineKeyboardMarkup()
delete_track_button = InlineKeyboardButton('Удалить трек', callback_data='delete track')
delete_track_markup.add(delete_track_button)

global new_track_message
new_track_message = None

global party_name
party_name = None

global track_clicks
track_clicks = 0

global track_cancellations
track_cancellations = 0

global sdb_channel_id
sdb_channel_id = -1002065888143

global track_name
track_name = None

global verified_track_name
verified_track_name = None

global track_query
track_query = False

global transfer_verification_query
transfer_verification_query = False

global transfer_verification_callback
transfer_verification_callback = None

global verified_track_query
verified_track_query = False

global track_list
track_list = []

global tickets_list
tickets_list = []

global verified_track_dict
verified_track_dict = {}

ticket_price = [LabeledPrice(f'Билет на {party_name}', 35000)]
track_price = [LabeledPrice('Заказать трек', 30000)]


def ticket_invoice(message):
    bot.send_invoice(
        message.chat.id,
        'Билет',
        f'Билет на {party_name}',
        'TICKET',
        paymentToken,
        'RUB',
        ticket_price,
    )


def db_check(message):
    name = message.from_user.first_name
    tg_id = message.from_user.id
    nickname = message.from_user.username

    conn = sqlite3.connect('/data/sdb.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT( * ) FROM users WHERE tg_id = ?', (tg_id,))
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute('INSERT INTO users (name, nickname, tg_id) VALUES (?, ?, ?)', (name, nickname, tg_id))
        make_log(nickname, 'added to database')
    make_log(nickname, 'in database')
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
    global tracks_text
    tracks_text = 'Заказанные треки:'
    i = 1
    for track in track_list:
        tracks_text += f'\n{i}. {track}'
        i += 1
    make_log('admin', f'{track_list}')


def find_all_tickets():
    conn = sqlite3.connect('/data/sdb.db')
    cursor = conn.cursor()

    cursor.execute('SELECT ticket_key FROM tickets')
    tickets = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return tickets


def make_tickets_list_text(tickets):
    global tickets_list
    tickets_list = [ticket[0] for ticket in tickets]
    make_log('admin', f'Available tickets: {tickets_list}')

    tickets_text = 'Купленные билеты: '
    for ticket in tickets_list:
        tickets_text += f'\n• Билет {ticket}'

    return tickets_text


def delete_ticket(message):
    global tickets_list
    if message.text in f'{tickets_list}':
        conn = sqlite3.connect('/data/sdb.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM tickets WHERE ticket_key = ?', (message.text,))

        conn.commit()
        cursor.close()
        conn.close()

        tickets = find_all_tickets()
        tickets_text = make_tickets_list_text(tickets)

        bot.edit_message_text(tickets_text, message.chat.id, message.message_id - 1)
        bot.delete_message(message.chat.id, message.id)
        make_log('admin', f'ticket {message.text} deleted')

        bot.register_next_step_handler(message, delete_ticket)
    control_panel(message)


def control_panel(message):
    make_log(message.from_user.username, 'control panel')
    bot.send_message(message.chat.id, '<b>Панель управления</b>⬇️', reply_markup=markupKeyboard, parse_mode='html')


def track(message):
    global track_query, track_name, new_track_message, track_cancellations
    track_name = message.text.strip()
    new_track_message = message
    print(message.text.lower())

    if message.text.lower() == '/start':
        print('start')
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.delete_message(message.chat.id, message.message_id)

        track_cancellations += 1
        make_log(message.from_user.username, 'request /start cancelled')
    if message.text.lower() == 'отмена':
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.delete_message(message.chat.id, message.message_id)

        track_cancellations += 1
        make_log(message.from_user.username, 'request cancelled')
        control_panel(message)
    else:
        if track_name == '/start':
            control_panel(message)
        else:
            track_query = True
            bot.send_message(message.chat.id, 'Ожидайте одобрения трека⏳', reply_markup=markupKeyboard)
            make_log(message.from_user.username, f'request: {track_name}')

            verification_markup = InlineKeyboardMarkup()
            verifyButton = InlineKeyboardButton('Одобрить', callback_data='verify track')
            rejectButton = InlineKeyboardButton('Отказать', callback_data='reject track')
            verification_markup.row(verifyButton, rejectButton)
            make_log('INFO', f"'{track_name}' sent to verification")

            bot.send_message(905069756,
                             'Заказали трек ' + track_name +
                             '\n\nДанные:\n' + 'ID: ' + f'{message.from_user.id}' +
                             '\n' + 'Имя: ' + f'{message.from_user.first_name}' +
                             '\n' + 'Ник: @' + f'{message.from_user.username}'
                             , reply_markup=verification_markup)


def track_waiting_time():
    track_time = (len(track_list) * 10) + 10
    return track_time


def make_log(username, comment):
    log_file = open('/data/logs.txt', 'a', encoding='utf-8')
    date = datetime.now().strftime("%d-%m-%Y")
    time = datetime.now().strftime("%H:%M:%S")

    log_file.write(f'[{date} {time}][@{username}][{comment}]\n')
    log_file.close()


@bot.message_handler(commands=['start'])
def start(message):
    make_log(message.from_user.username, 'START')
    if subscribe_check(message) == True:
        make_log(message.from_user.username, 'subscribed')
        db_check(message)
        control_panel(message)
    else:
        markup = InlineKeyboardMarkup()
        controlPanelButton = InlineKeyboardButton('Подписался', callback_data='subscribe')
        markup.add(controlPanelButton)

        make_log(message.from_user.username, 'not subscribed')
        bot.send_message(message.chat.id,
                         'Для дальнейшей работы с ботом нужно подписаться на наш канал\n\nhttps://t.me/sdb_party',
                         reply_markup=markup)


@bot.message_handler(commands=['admin'])
def admin_command(message):
    bot.register_next_step_handler(message, admin)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global track_query, verified_track_name, transfer_verification_query, transfer_verification_callback, track_nu

    if callback.data == 'control_panel':
        make_log(callback.message.chat.username, 'control panel call')
        print(callback.message)
        if subscribe_check(callback.message) == True:
            control_panel(callback.message)

    elif callback.data == 'subscribe':
        subscribe = bot.get_chat_member(sdb_channel_id, callback.message.chat.id)
        if subscribe.status == "member" or subscribe.status == "creator" or subscribe.status == "administrator":
            make_log(callback.message.chat.username, 'subscribe')

            make_log(callback.message.chat.username, 'control panel')
            bot.send_message(callback.message.chat.id, '<b>Панель управления</b>⬇️', reply_markup=markupKeyboard,
                             parse_mode='html')
        else:
            make_log(callback.message.chat.username, 'did not subscribed')
            pass

    elif callback.data == 'information':
        bot.send_message(callback.message.chat.id, 'Что-то про бот')

    elif callback.data == 'buy another ticket':
        make_log(callback.message.chat.username, 'buy another ticket')
        ticket_invoice(callback.message)

    elif callback.data == 'track list':
        make_log('admin', 'show all tracks')
        list_of_tracks()
        bot.send_message(callback.message.chat.id, tracks_text, reply_markup=delete_track_markup)

    elif callback.data == 'ticket list':
        make_log('admin', 'show all tickets')
        tickets = find_all_tickets()
        tickets_text = make_tickets_list_text(tickets)

        bot.send_message(callback.message.chat.id, tickets_text)
        bot.register_next_step_handler(callback.message, delete_ticket)

    elif callback.data == 'delete track':
        track_for_deleting = track_list[0]
        del track_list[0]
        make_log('admin', f"'{track_for_deleting}' deleted")

        list_of_tracks()
        bot.edit_message_text(tracks_text, callback.message.chat.id, callback.message.message_id,
                              reply_markup=delete_track_markup)

    elif callback.data == 'verify track':
        payment_markup = InlineKeyboardMarkup()
        card_payment_button = InlineKeyboardButton('Оплатить картой', callback_data='card')
        transfer_payment_button = InlineKeyboardButton('Оплатить переводом', callback_data='transfer')
        # payment_markup.row(card_payment_button)
        payment_markup.row(transfer_payment_button)

        verified_track_name = track_name
        verified_track_dict[new_track_message.from_user.id] = verified_track_name

        make_log(new_track_message.from_user.username, f"'{verified_track_name}' verified")
        bot.edit_message_text('Трек "' + verified_track_name + '" одобрен', callback.message.chat.id,
                              callback.message.message_id)
        bot.send_message(new_track_message.chat.id, 'Трек "' + verified_track_name + '" одобрен🥳\n\nОплата⬇️', reply_markup=payment_markup)
        track_query = False

    elif callback.data == 'card':
        make_log(callback.from_user.username, f'card chosen')
        bot.send_invoice(
            callback.message.chat.id,
            'Трек на заказ',
            'Ваш трек одобрен!\nКак только пройдет оплата, мы включим ' + verified_track_dict[
                callback.from_user.id] + f' в течение {track_waiting_time() - 10} минут',
            verified_track_dict[callback.from_user.id],
            paymentToken,
            'RUB',
            track_price)

    elif callback.data == 'transfer':
        transfer_markup = InlineKeyboardMarkup()
        transfer_send_button = InlineKeyboardButton('Перевел(а)', callback_data='verify transfer')
        transfer_markup.add(transfer_send_button)

        make_log(new_track_message.from_user.username, f'transfer chosen')
        bot.send_message(callback.message.chat.id, 'Перевод 300₽ по номеру телефона/карты на *Сбербанк*' +
                         '\nВ комментарии нужно указать название трека, который вы заказали' +
                         f' (`{verified_track_dict[callback.from_user.id]}`)' +
                         '\nРеквизиты/трек копируются при нажатии'
                         '\n\n`+7(920)631-39-51`' +
                         '\n\n`2202 2017 1573 9195`' +
                         '\n\n*Владислав Максимилианович Ю.*', reply_markup=transfer_markup, parse_mode="MARKDOWN")

    elif callback.data == 'verify transfer':
        make_log(new_track_message.from_user.username,
                 f"transfer '{verified_track_dict[callback.from_user.id]}' send to verification")
        if transfer_verification_query == False:
            transfer_verification_query = True
            transfer_verification_callback = callback

            make_log(new_track_message.from_user.username, 'no transfer query')

            admin_verify_transfer_markup = InlineKeyboardMarkup()
            admin_verify_transfer_button = InlineKeyboardButton('Подтвердить перевод',
                                                                callback_data='admin verify transfer')
            admin_verify_transfer_markup.add(admin_verify_transfer_button)

            bot.send_message(905069756, f'Выполнен перевод за трек "{verified_track_dict[callback.from_user.id]}"',
                             reply_markup=admin_verify_transfer_markup)
            bot.send_message(callback.message.chat.id, 'Ожидайте подтверждение платежа')

        else:
            make_log(new_track_message.from_user.username, 'TRANSFER QUERY')
            bot.send_message(callback.message.chat.id,
                             'В данный момент происходит обработка платежа, подождите чуть-чуть :)')

    elif callback.data == 'admin verify transfer':
        make_log('admin', f"transfer '{verified_track_dict[transfer_verification_callback.from_user.id]}' verified")
        transfer_verification_query = False
        track_list.append(verified_track_dict[transfer_verification_callback.from_user.id])
        bot.edit_message_text('Перевод за трек "' + verified_track_dict[transfer_verification_callback.from_user.id] +
                              '" подтвержден', callback.message.chat.id, callback.message.message_id)
        bot.send_message(transfer_verification_callback.message.chat.id,
                         f'Платеж подтвержден! Мы включим "{verified_track_dict[transfer_verification_callback.from_user.id]}" в течение {track_waiting_time() - 10} минут')
        make_log('INFO', f"Track list: {track_list}")

    elif callback.data == 'reject track':
        make_log(new_track_message.from_user.username, f"'{track_name}' rejected")
        bot.send_message(new_track_message.chat.id,
                         'Трек не был одобрен, вы можете выбрать другой трек нажав на кнопку "Заказать трек"')
        bot.edit_message_text('Трек "' + track_name + '" не был одобрен', callback.message.chat.id,
                              callback.message.message_id)
        track_query = False

    elif callback.data == 'statistic':
        bot.send_message(callback.message.chat.id, f'Кликов: {track_clicks}\nОтмен: {track_cancellations}')


@bot.message_handler()
def answer(message):
    global track_query, party_name

    if message.text.lower() == 'купить билет':
        make_log(message.from_user.username, 'buy a ticket')
        tg_id = message.from_user.id

        conn = sqlite3.connect('/data/sdb.db')
        cursor = conn.cursor()

        cursor.execute('SELECT party_name FROM parties LIMIT 1')
        party_name = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT( * ) FROM tickets WHERE telegram_id = ?', (tg_id,))
        is_ticket_owner = cursor.fetchone()[0]

        if is_ticket_owner == 0:
            make_log(message.from_user.username, "don't have a ticket")
            ticket_invoice(message)
        else:
            cursor.execute('SELECT COUNT( * ) FROM tickets WHERE telegram_id = ?', (tg_id,))
            tickets_amount = cursor.fetchone()[0]

            ticket_markup = InlineKeyboardMarkup()
            another_ticket_button = InlineKeyboardButton('Да', callback_data='buy another ticket')
            ticket_markup.add(another_ticket_button)

            text = f'Вы уже приобрели билет, вы действительно хотите купить еще один билет?\n\n<b>Ваши билеты:</b>'
            ticket_keys = ''
            for i in range(tickets_amount):
                cursor.execute('SELECT ticket_key FROM tickets WHERE telegram_id = ? LIMIT ? OFFSET ?',
                               (tg_id, tickets_amount, i))
                key = cursor.fetchone()[0]
                text += f'\n• Билет {key}'
                ticket_keys += f'{key} '
            make_log(message.from_user.username, f'already have {tickets_amount} tickets(s): {ticket_keys.strip()}')
            bot.send_message(message.chat.id, text, reply_markup=ticket_markup, parse_mode='html')

        conn.commit()
        cursor.close()
        conn.close()

    elif message.text.lower() == 'заказать трек🎶':
        global track_clicks
        track_clicks += 1
        make_log(message.from_user.username, 'request a song')

        if track_query == False:
            cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_button = InlineKeyboardButton('ОТМЕНА')
            cancel_markup.add(cancel_button)

            bot.send_message(message.chat.id, '*Стоимость заказа трека - 300₽*' +
                             '\n\nОтправь нам название трека , который ты хочешь услышать и мы включим его для тебя!🎵' +
                             '\n\n❗Название трека и исполнитель должны быть написаны одним сообщением ❗' +
                             '\n\nТрек должен соответствовать тематике вечеринки и должен пройти верификацию☺️' +
                             '\n*Рок, метал, джаз, барбарики верификацию не пройдут🚫*' +
                             f'\n\nТреков в очереди: {len(track_list)}' +
                             f'\nПримерное время ожидания ~ {track_waiting_time()} минут', reply_markup=cancel_markup, parse_mode='markdown')
            bot.register_next_step_handler(message, track)
        else:
            make_log(message.from_user.username, 'TRACK QUERY')
            bot.send_message(message.chat.id, 'В данный момент на верификации уже есть трек, попробуйте через 5 минут🥺')

    elif message.text.lower() == 'о sdbℹ️':
        bot.send_message(message.chat.id, 'Мы - *SDB PARTY*, организаторы ночных вечеринок города Р.'
                                          '\n\n*Почему SDB?* Потому что четверо организаторов любят сдобные булочки и называют свой сквад - Сдобная братва 🥐'
                                          '\n\n*SDB* - нестандартный подход к организации вечеринок и к их рекламе '
                                          '\n\n🪩*SDB* - вечеринка, на которой музыку знает каждый, и ты гарантированно будешь танцевать, пока не устанешь 💃'
                                          '\n\n*SDB* - смешные и порой мега кринжевые Reels в инстаграме и мы это делаем не от того, что не умеем по другому, а потому что - это смешно 🤭'
                                          '\n\nЖдем вас на наших вечеринках во *VMESTE BAR* ❤️', parse_mode='MARKDOWN')
        make_log(message.from_user.username, 'about us')

    elif message.text.lower() == 'когда следующая тусовка?🧐':
        conn = sqlite3.connect('/data/sdb.db')
        cursor = conn.cursor()

        cursor.execute('SELECT party_name, description, date FROM parties LIMIT 1')
        party_info = cursor.fetchall()

        info = ''
        for element in party_info:
            info += f'Следующая тусовка: {element[0]}\n\nДата: {element[2]}\n\nОписание:\n{element[1]}'

        cursor.close()
        conn.close()

        sdb_logo = open('resources/sdb b а 3.jpg', 'rb')
        bot.send_photo(message.chat.id, sdb_logo, caption=info)
        make_log(message.from_user.username, 'next party info')


def admin(message):
    if message.text.strip() == '14882012':
        admin_markup = InlineKeyboardMarkup()
        list_of_tracks_button = InlineKeyboardButton('Список треков', callback_data='track list')
        list_of_tickets_button = InlineKeyboardButton('Список билетов', callback_data='ticket list')
        statistic_button = InlineKeyboardButton('Статистика', callback_data='statistic')
        admin_markup.row(list_of_tracks_button, list_of_tickets_button)
        admin_markup.row(statistic_button)

        bot.send_message(message.chat.id, 'Панель управления', reply_markup=admin_markup)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Что-то пошло не так :(\nПопробуйте еще раз")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    global verified_track_name

    if message.successful_payment.invoice_payload == 'TICKET':
        tg_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        key = random.randint(0, 9999)
        make_log(message.from_user.username, f'ticket {key} paid successfully')

        conn = sqlite3.connect('/data/sdb.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO tickets (first_name, username, telegram_id, ticket_key) VALUES (?, ?, ?, ?)',
                       (first_name, username, tg_id, key))

        conn.commit()
        cursor.close()
        conn.close()

        bot.send_message(message.chat.id, 'Вы купили билет! Ваш код: ' + f'{key}', parse_mode='Markdown')

    elif message.successful_payment.total_amount == 30000:
        make_log(message.from_user.username, f"'{verified_track_dict[message.from_user.id]}' paid successfully")
        bot.send_message(905069756, f"'{message.successful_payment.invoice_payload}' оплатили")
        bot.send_message(message.chat.id,
                         f'Трек успешно оплачен! Мы включим его в течение {track_waiting_time()} минут',
                         parse_mode='Markdown')

        track_list.append(message.successful_payment.invoice_payload)
        make_log('INFO', f"Track list: {track_list}")


bot.infinity_polling()
