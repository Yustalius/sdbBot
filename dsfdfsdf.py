import telebot
import sqlite3
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

bot = telebot.TeleBot('7029750604:AAEh3Ozvv2BGmDY_VUvQBseulIiPQ-fKP60')
paymentToken = '381764678:TEST:83709'

@bot.message_handler(commands=['start'])
def first(message):
    service = types.ReplyKeyboardMarkup(True, True)
    service.row('Удалить клаву нахуй')
    bot.send_message(message.chat.id, 'Что будем делать?', reply_markup=service)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'Удалить клаву нахуй':
        a = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'как хош', reply_markup=a)

bot.infinity_polling()
