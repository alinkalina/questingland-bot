import telebot
from hidden_file import token
from quest_bot_info import users

bot = telebot.TeleBot(token)

for u in users.keys():
    bot.send_message(u, 'Бот временно находится на доработке')


bot.polling()
