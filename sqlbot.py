import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot('7029750604:AAEh3Ozvv2BGmDY_VUvQBseulIiPQ-fKP60')

# name = None

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('database/sdb.db')
    cursor = conn.cursor()

    cursor.execute(
        'CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()

    cursor.close()
    conn.close()

    bot.send_message(message.chat.id, 'Hello!\nEnter your name')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    # global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Enter your password')
    bot.register_next_step_handler(message, user_password, name)

def user_password(message, name):
    password = message.text.strip()

    conn = sqlite3.connect('database/sdb.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO users (name, pass) VALUES (?, ?)', (name, password))
    conn.commit()

    cursor.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('List of users', callback_data = 'list'))
    bot.send_message(message.chat.id, "You're registered!", reply_markup = markup)
    bot.send_message(message.chat.id, message.from_user.id)

@bot.callback_query_handler(func=lambda callback: True)
def callback(call):
    conn = sqlite3.connect('database/sdb.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    info = ''
    for element in users:
        info += f'Имя: {element[1]}, пароль: {element[2]}\n'

    cursor.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)

bot.infinity_polling()
