import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputFile
from quest_bot_game import menu_generation, send_next_question
from quest_bot_info import users, names_list, get_dict
from hidden_file import my_id, token
import shelve


bot = telebot.TeleBot(token)


def check_game_name(message):
    return message.text in names_list()


def check_start(message):
    return message.text == '🎮 Играть'


def check_answer(message):
    user_id = message.chat.id
    return message.text in users[user_id]['current_level']['variants'].keys()


@bot.message_handler(commands=['start'])
def send_start_message(message):
    if message.chat.id not in users.keys():
        users[message.chat.id] = {}
        users[message.chat.id]['results'] = {}
        for name in names_list():
            users[message.chat.id]['results'][name] = {'attempts': 0,
                                                       'win': 0}
    bot.send_message(message.chat.id, 'Добро пожаловать! 🖐️ Выбери игру из /menu и окунись в мир загадок и испытаний!',
                     reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['help'])
def send_help_message(message):
    bot.send_message(message.chat.id, '/start - получить приветственное сообщение 🖐️\n'
                                      '/help - получить сообщение о всех командах, которое ты сейчас читаешь 📖\n'
                                      '/menu - выбрать игру 🧐\n'
                                      '/again - начать игру заново 🔄\n'
                                      '/mystatistics - посмотреть мои достижения 📊\n'
                                      '/support - написать в техподдержку, если что-то не работает, оправить '
                                      'отзыв или предложение ⚙\nЕсли вдруг бот сразу не отвечает (мало ли что 🙃), '
                                      'пожалуйста, подожди несколько секунд и не путай его множеством сообщений',
                     reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['menu'])
def send_menu(message):
    if message.chat.id not in users.keys():
        users[message.chat.id] = {}
        users[message.chat.id]['results'] = {}
        for name in names_list():
            users[message.chat.id]['results'][name] = {'attempts': 0,
                                                       'win': 0}
    users[message.chat.id]['current_game'] = {}
    bot.send_message(message.chat.id, 'Выбери игру', reply_markup=menu_generation())


@bot.message_handler(commands=['again'])
def start_again(message):
    try:
        users[message.chat.id]['current_level'] = users[message.chat.id]['current_game']['game']
        users[message.chat.id]['results'][users[message.chat.id]['current_game']['name']]['attempts'] += 1
        bot.send_message(message.chat.id, 'Начинаем игру! 🔥')
        send_next_question(message, bot)
    except KeyError:
        bot.send_message(message.chat.id, '❗ Сначала выбери игру из /menu, пожалуйста',
                         reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['mystatistics'])
def send_statistics(message):
    if message.chat.id not in users.keys():
        users[message.chat.id] = {}
        users[message.chat.id]['results'] = {}
        for name in names_list():
            users[message.chat.id]['results'][name] = {'attempts': 0,
                                                       'win': 0}
    s = '*Твои результаты:*\n'
    for game in users[message.chat.id]['results'].keys():
        s += f"\n{game}\nПопыток: {users[message.chat.id]['results'][game]['attempts']}\nПобед: " \
             f"{users[message.chat.id]['results'][game]['win']}\n"
    bot.send_message(message.chat.id, s, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['support'])
def send_support(message):
    def get_feedback(feedback):
        if not feedback.text.startswith('/'):
            bot.send_message(my_id, f'Пользователь @{feedback.from_user.username} написал_а в техподдержку!\n\n'
                                    f'{feedback.text}')
            bot.send_message(message.chat.id, 'Спасибо! Тебе ответят в ближайшее время 🩵')

    msg = bot.send_message(message.chat.id, 'Опиши свою проблему, если что-то не работает, или оставь отзыв (мы также '
                                            'рады предложениям по поводу интерфейса, сюжетов игр и т. д.)',
                           reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_feedback)


@bot.message_handler(func=check_game_name)
def game_name_choosen(message):
    game = get_dict(message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text='🎮 Играть'))
    users[message.chat.id]['current_game'] = game
    users[message.chat.id]['current_level'] = game['game']
    try:
        with open(game['description-photo'], 'rb') as file:
            bot.send_photo(message.chat.id, InputFile(file))
        file.close()
    except FileNotFoundError:
        bot.send_message(message.chat.id, '_Здесь должно было быть фото, но, к сожалению, оно не загрузилось 😢_',
                         parse_mode='Markdown')
    bot.send_message(message.chat.id, f"*{game['name']}*\n{game['description']}", parse_mode='Markdown',
                     reply_markup=markup)


@bot.message_handler(func=check_start)
def start_game(message):
    users[message.chat.id]['results'][users[message.chat.id]['current_game']['name']]['attempts'] += 1
    bot.send_message(message.chat.id, 'Начинаем игру! 🔥')
    send_next_question(message, bot)


@bot.message_handler(func=check_answer)
def next_question(message):
    users[message.chat.id]['current_level'] = users[message.chat.id]['current_level']['variants'][message.text]
    send_next_question(message, bot)


@bot.message_handler(content_types=['text'])
def send_error_text_message(message):
    bot.send_message(message.chat.id, '⛔ Пожалуйста, общайся с ботом с помощью кнопок и команд')


@bot.message_handler(content_types=['photo', 'audio', 'video', 'document', 'sticker', 'voice'])
def send_error_type_message(message):
    bot.send_message(message.chat.id, '🚫 Прости, бот разбирается только в текстовых сообщениях')


bot.polling()

with shelve.open('users.mdb') as db:
    db['users'] = users
