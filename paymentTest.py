import telebot
from telebot.types import LabeledPrice, ShippingOption

bot = telebot.TeleBot('7029750604:AAEh3Ozvv2BGmDY_VUvQBseulIiPQ-fKP60')
paymentToken = '381764678:TEST:83709'

ticketPrice = [LabeledPrice('Билет на SDB PARTY', 35000)]
trackPrice = [LabeledPrice('Заказать трек', 30000)]

@bot.message_handler(commands=['start'])
def command_start(message):
    bot.send_message(message.chat.id, 'Привет! Напиши /buy чтобы приобрести билет')

@bot.message_handler(commands=['ticket'])
def command_pay(message):
    bot.send_message(message.chat.id, 'бла бла бла', parse_mode='Markdown')
    bot.send_invoice(
        message.chat.id,
        'Билет',
        'Билет на SDB PARTY',
        'Хуй знает что это',
        paymentToken,
        'RUB',
        ticketPrice,
        photo_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpZa6jHJ1z_tK5mRf2zEUcP3EKl7wL7wDhTv7AYfweEQ&s',
        photo_height=1024,  # !=0/None or picture won't be shown
        photo_width=1024,
        photo_size=1024)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id,
                     'Hoooooray! Thanks for payment! We will proceed your order for `{} {}` as fast as possible! '
                     'Stay in touch.\n\nUse /buy again to get a Time Machine for your friend!'.format(
                         message.successful_payment.total_amount / 100, message.successful_payment.currency),
                     parse_mode='Markdown')

bot.infinity_polling(skip_pending = True)
