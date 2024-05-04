import telebot
import sqlite3

bot = telebot.TeleBot('7029750604:AAEh3Ozvv2BGmDY_VUvQBseulIiPQ-fKP60')

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    tg_id = message.from_user.id

    conn = sqlite3.connect('database/sdb.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT( * ) FROM users WHERE telegram_id = ?', (tg_id,))
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute('INSERT INTO users (name, telegram_id) VALUES (?, ?)', (name, tg_id))
        bot.send_message(message.chat.id, 'Ты добавлен в базу данных')
    else:
        bot.send_message(message.chat.id, 'Ты уже есть в базе данных')
    conn.commit()
    cursor.close()
    conn.close()
    # cursor.execute('INSERT INTO users (name, pass, telegram_id) VALUES (?, ?, ?)', (name, password, tg_id))

bot.infinity_polling()