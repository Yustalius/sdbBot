import telebot
import requests
import json

bot = telebot.TeleBot('7029750604:AAEh3Ozvv2BGmDY_VUvQBseulIiPQ-fKP60')
API = '34d773541633ad11d6316220acef7129'

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Укажи название города: ')

@bot.message_handler(content_types=['text'])
def get_weather(message):
    city = message.text.strip()
    res = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=100&appid={API}')
    print(res)
    data = json.loads(res.text)
    print(data)
    bot.send_message(message.chat.id, f'Город:{data["local_names"]["ru"]}')



bot.infinity_polling()