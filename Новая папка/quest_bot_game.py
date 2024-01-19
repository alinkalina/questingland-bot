from quest_bot_info import games, users
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InputFile, ReplyKeyboardRemove


def menu_generation():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for game in games:
        buttons.append(KeyboardButton(text=game['name']))
    for i in range(len(buttons)):
        if i % 2 == 0:
            try:
                markup.row(buttons[i], buttons[i + 1])
            except IndexError:
                markup.row(buttons[i])
    return markup


def send_next_question(message, bot):
    user_id = message.chat.id
    level = users[user_id]['current_level']
    if level['variants']:
        try:
            with open(level['photo'], 'rb') as file:
                bot.send_photo(user_id, InputFile(file))
            file.close()
        except FileNotFoundError:
            bot.send_message(user_id, '_Здесь должно было быть фото, но, к сожалению, оно не загрузилось 😢_',
                             parse_mode='Markdown')
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = []
        for variant in level['variants'].keys():
            buttons.append(KeyboardButton(text=variant))
        for i in range(len(buttons)):
            if i % 2 == 0:
                try:
                    markup.row(buttons[i], buttons[i + 1])
                except IndexError:
                    markup.row(buttons[i])
        bot.send_message(user_id, level['text'], reply_markup=markup)
    else:
        try:
            with open(level['photo'], 'rb') as file:
                bot.send_photo(user_id, InputFile(file), reply_markup=ReplyKeyboardRemove())
            file.close()
        except FileNotFoundError:
            bot.send_message(user_id, '_Здесь должно было быть фото, но, к сожалению, оно не загрузилось 😢_',
                             parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        bot.send_message(user_id, level['text'])
        if level['win']:
            bot.send_message(user_id, users[user_id]['current_game']['win'])
            users[message.chat.id]['results'][users[message.chat.id]['current_game']['name']]['win'] += 1
        else:
            bot.send_message(user_id, users[user_id]['current_game']['lose'])
