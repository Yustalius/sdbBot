import telebot
import webbrowser
import sqlite3
from telebot import types

bot = telebot.TeleBot('7029750604:AAEh3Ozvv2BGmDY_VUvQBseulIiPQ-fKP60')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    servicesButton = types.KeyboardButton("КУПИТЬ БИЛЕТ")
    markup.row(servicesButton)
    trackRequestButton = types.KeyboardButton("ЗАКАЗАТЬ ТРЕК")
    markup.row(trackRequestButton)
    infoButton = types.KeyboardButton('О нас')
    nextPartyButton = types.KeyboardButton('Когда следующая тусовка?')
    markup.row(infoButton, nextPartyButton)
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}\nЭто бот SDB, через него можно заказать трек во время тусовки или купить билет', reply_markup=markup)

    bot.register_next_step_handler(message, on_click)

# @bot.message_handler(commands=['start', 'hello'])
# def start(message):
#     markup = types.InlineKeyboardMarkup()
#     siteButton = types.InlineKeyboardButton('Перейти на сайт', url='https://github.com/Yustalius')
#     markup.row(siteButton)
#     mazdaButton = types.InlineKeyboardButton('Узнать, кто такой мазда', callback_data='mazda')
#     rusikButton = types.InlineKeyboardButton('Узнать, кто такой русик', callback_data='rusik')
#     markup.row(mazdaButton, rusikButton)
#     sanyaButton = types.InlineKeyboardButton('Узнать, кто такой саня', callback_data='sanya')
#     yustusButton = types.InlineKeyboardButton('Узнать, кто такой владос', callback_data='yustus')
#     markup.row(sanyaButton, yustusButton)
#     bot.send_message(message.chat.id, f'Привет, {цmessage.from_user.first_name}', reply_markup=markup)

@bot.message_handler()
def on_click(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')
    elif message.text.lower() == 'иди нахуй':
        bot.reply_to(message, f'Сам иди, {message.from_user.first_name}!')
    elif message.text.lower() == 'узнать, кто такой мазда':
        bot.reply_to(message, 'Монобровь 2024')
        file = open('./mazda.jpg', 'rb')
        bot.send_photo(message.chat.id, file)
    elif message.text.lower() == 'узнать, кто такой русик':
        bot.reply_to(message, 'Черноголовка')
        file = open('./rusik.jpg', 'rb')
        bot.send_photo(message.chat.id, file)
    elif message.text.lower() == 'узнать, кто такой саня':
        bot.reply_to(message, 'Лысый пряник')
        file = open('./sanya.jpg', 'rb')
        bot.send_photo(message.chat.id, file)
    elif message.text.lower() == 'узнать, кто такой владос':
        bot.reply_to(message, 'Альфа утюг')
        file = open('./vlados.jpg', 'rb')
        bot.send_photo(message.chat.id, file)

@bot.message_handler(commands=['mazda'])
def main(message):
    bot.send_message(message.chat.id, '<b><em><u>Mazda pidor</u></em></b>', parse_mode='html')

@bot.message_handler(commands=['web'])
def main(message):
    bot.send_message(message.chat.id, 'https://github.com/Yustalius')


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Перейти на сайт', url='https://github.com/Yustalius'))
    markup.add(types.InlineKeyboardButton('Удалить фото', callback_data='delete'))
    markup.add(types.InlineKeyboardButton('Изменить фото', callback_data='edit'))
    bot.reply_to(message, 'Замечательное фото!', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == 'edit':
        bot.edit_message_text('Edit text', callback.message.chat.id, callback.message.message_id)


bot.infinity_polling()