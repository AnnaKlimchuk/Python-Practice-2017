import telebot
from telebot import types
import numpy as np
import config
import PIL 
from PIL import Image, ImageDraw

bot = telebot.TeleBot(config.TOKEN)
Games = {}
RULES = '\
    Cтандартная колода карт раскладывается в 8 колонок, четыре колонки по 7 \
карт и четыре — по 6. Карты лежат лицевой стороной вверх.\n\
Вверху слева 4 ячейки, они называются «домом», справа от них 4 «свободных» \
ячейки. На момент начала игры все они пусты.\n\
В игре разрешено перекладывть верхнюю карту из колонки или свободной ячейки\n\
    в любую другую колонку на следующую по старшинству карту другого цвета;\n\
    в любую освободивщуюся колонку;\n\
    в любую пустую "свободную" ячейку;\n\
    в "дом", начиная с туза и заканчивая королём той же масти.\n\
Пасьянс сходится, если удаётся переместить всю колоду в «дом».'

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    if hasattr(message.from_user, 'last_name') and message.from_user.last_name is not None:
        name += u" {}".format(message.from_user.last_name)
    if hasattr(message.from_user, 'username') and message.from_user.username is not None:
        name += u" (@{})".format(message.from_user.username)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row('Новая игра', 'Узнать правила игры')
    msg = bot.send_message(message.chat.id, text='Добро пожаловать в игру, ' + name, 
                           reply_markup=markup)
    bot.register_next_step_handler(msg, steps)

def steps(message):
    if (message.text=='Новая игра') | (message.text=='Начать игру'):
        new_game(message.chat.id)
    elif message.text=='Узнать правила игры':
        first_rules(message.chat.id)
    elif message.text=='Правила игры':
        rules(message.chat.id)
    elif (message.text=='Выход'):
        start(message)
    elif (message.text=='Выбрать другую карту') | (message.text=='Назад'):
        step(message.chat.id)
    elif ((message.text[0]==config.SPADE) | (message.text[0]==config.CLUB) | 
          (message.text[0]==config.HEART) | (message.text[0]==config.DIAMOND)):
        #возможно можно улучщить эту проверку
        moving(message)
    elif (message.text=='Свободная ячейка'):
        move_to_free(message.chat.id)
    elif (message.text=='Дом'):
        move_to_home(message.chat.id)
    elif (message.text[1:9]==' Колонка'):
        move_to_column(message)
    else:
        bot.send_message(message.chat.id, text='Какая-то ошибка')
        #start(message)
    
def first_rules(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row('Начать игру', 'Выход')
    msg = bot.send_message(chat_id, text=RULES, reply_markup=markup)
    bot.register_next_step_handler(msg, steps)    
        
def rules(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row('Назад')
    msg = bot.send_message(chat_id, text=RULES, reply_markup=markup)
    bot.register_next_step_handler(msg, steps)
    
def step(chat_id):
    f = open(Games[chat_id][0].take_photo(str(chat_id)), 'rb')
    bot.send_photo(str(chat_id), photo=f)    

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)    
    
    end_of_game = True
    
    moving_cards = Games[chat_id][0].moving_cards_in_frees()
    keyboards = []
    for elem in moving_cards:
        end_of_game = False
        suit, number = divmod(elem, 13)
        keyboards.append(config.SUITS[suit] + config.NUMBERS[number])
    markup.row(*[types.KeyboardButton(name) for name in keyboards]) 
    
    moving_cards = Games[chat_id][0].moving_cards_in_field()
    keyboards = []
    for elem in moving_cards:
        end_of_game = False
        suit, number = divmod(elem, 13)
        keyboards.append(config.SUITS[suit] + config.NUMBERS[number])
    markup.row(*[types.KeyboardButton(name) for name in keyboards])
    
    if(end_of_game):
        finish(chat_id)
    else:    
        markup.row('Выход', 'Новая игра', 'Правила игры')
        msg = bot.send_message(chat_id, text='Какую карту вы хотите переложить?', 
                               reply_markup=markup)
        bot.register_next_step_handler(msg, steps)
    
def finish(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) 
    markup.row('Новая игра', 'Выход')
    msg = bot.send_message(chat_id, text='Поздравляю, вы победитель!', 
                           reply_markup=markup)
    bot.send_sticker(chat_id, data='CAADAgAD-QsAAiMhBQAB9_KHkFe4N40C') 
    bot.register_next_step_handler(msg, steps)

def new_game(chat_id):
    Games[chat_id] = [config.Game(), config.Card()]
    step(chat_id)
    
def moving(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    suit = message.text[0]
    number = config.NUMBERS_NUM[message.text[1:]]
    
    i, j, figure = Games[message.chat.id][0].find_in_field(suit, number)
    if j == -1:
        i, figure = Games[message.chat.id][0].find_in_frees(suit, number)
        Games[message.chat.id][1] = config.Card(i, -1, figure)
    else:
        Games[message.chat.id][1] = config.Card(i, j, figure)
        
    keyboards = []
    if Games[message.chat.id][0].is_there_home(suit, number):
        keyboards.append('Дом')
    if Games[message.chat.id][0].is_there_free():
        keyboards.append('Свободная ячейка')
    markup.row(*[types.KeyboardButton(name) for name in keyboards])
    
    column = Games[message.chat.id][0].suitable_column(suit, number)
    keyboards = []
    for elem in column:
        keyboards.append(str(elem) + ' Колонка')
    markup.row(*[types.KeyboardButton(name) for name in keyboards])
    
    markup.row('Выход', 'Правила игры', 'Выбрать другую карту')
    msg = bot.send_message(message.chat.id, text='Куда вы хотите переложить эту карту?\n', 
                           reply_markup=markup)
    bot.register_next_step_handler(msg, steps)
    
def move_to_free(chat_id):
    Games[chat_id][0].move_to_free(Games[chat_id][1].row, Games[chat_id][1].column, 
                                   Games[chat_id][1].figure)
    step(chat_id)    
 
def move_to_home(chat_id):
    Games[chat_id][0].move_to_home(Games[chat_id][1].row, Games[chat_id][1].column, 
                                   Games[chat_id][1].figure)
    step(chat_id) 
 
def move_to_column(message):
    chat_id = message.chat.id
    new_column = int(message.text[0]) - 1
    Games[chat_id][0].move_to_column(Games[chat_id][1].row, Games[chat_id][1].column, 
                                     Games[chat_id][1].figure, new_column)
    step(chat_id) 

bot.polling()