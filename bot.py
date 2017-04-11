import telebot
from telebot import types
import numpy as np
import config
import PIL 
from PIL import Image, ImageDraw

bot = telebot.TeleBot(config.TOKEN)
Games = {}
RULES = '\
    C���������� ������ ���� �������������� � 8 �������, ������ ������� �� 7 \
���� � ������ � �� 6. ����� ����� ������� �������� �����.\n\
������ ����� 4 ������, ��� ���������� ������, ������ �� ��� 4 ����������� \
������. �� ������ ������ ���� ��� ��� �����.\n\
� ���� ��������� ������������ ������� ����� �� ������� ��� ��������� ������\n\
    � ����� ������ ������� �� ��������� �� ����������� ����� ������� �����;\n\
    � ����� �������������� �������;\n\
    � ����� ������ "���������" ������;\n\
    � "���", ������� � ���� � ���������� ������ ��� �� �����.\n\
������� ��������, ���� ������ ����������� ��� ������ � ����.'

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    if hasattr(message.from_user, 'last_name') and message.from_user.last_name is not None:
        name += u" {}".format(message.from_user.last_name)
    if hasattr(message.from_user, 'username') and message.from_user.username is not None:
        name += u" (@{})".format(message.from_user.username)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row('����� ����', '������ ������� ����')
    msg = bot.send_message(message.chat.id, text='����� ���������� � ����, ' + name, 
                           reply_markup=markup)
    bot.register_next_step_handler(msg, steps)

def steps(message):
    if (message.text=='����� ����') | (message.text=='������ ����'):
        new_game(message.chat.id)
    elif message.text=='������ ������� ����':
        first_rules(message.chat.id)
    elif message.text=='������� ����':
        rules(message.chat.id)
    elif (message.text=='�����'):
        start(message)
    elif (message.text=='������� ������ �����') | (message.text=='�����'):
        step(message.chat.id)
    elif ((message.text[0]==config.SPADE) | (message.text[0]==config.CLUB) | 
          (message.text[0]==config.HEART) | (message.text[0]==config.DIAMOND)):
        #�������� ����� �������� ��� ��������
        moving(message)
    elif (message.text=='��������� ������'):
        move_to_free(message.chat.id)
    elif (message.text=='���'):
        move_to_home(message.chat.id)
    elif (message.text[1:9]==' �������'):
        move_to_column(message)
    else:
        bot.send_message(message.chat.id, text='�����-�� ������')
        #start(message)
    
def first_rules(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row('������ ����', '�����')
    msg = bot.send_message(chat_id, text=RULES, reply_markup=markup)
    bot.register_next_step_handler(msg, steps)    
        
def rules(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row('�����')
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
        markup.row('�����', '����� ����', '������� ����')
        msg = bot.send_message(chat_id, text='����� ����� �� ������ ����������?', 
                               reply_markup=markup)
        bot.register_next_step_handler(msg, steps)
    
def finish(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) 
    markup.row('����� ����', '�����')
    msg = bot.send_message(chat_id, text='����������, �� ����������!', 
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
        keyboards.append('���')
    if Games[message.chat.id][0].is_there_free():
        keyboards.append('��������� ������')
    markup.row(*[types.KeyboardButton(name) for name in keyboards])
    
    column = Games[message.chat.id][0].suitable_column(suit, number)
    keyboards = []
    for elem in column:
        keyboards.append(str(elem) + ' �������')
    markup.row(*[types.KeyboardButton(name) for name in keyboards])
    
    markup.row('�����', '������� ����', '������� ������ �����')
    msg = bot.send_message(message.chat.id, text='���� �� ������ ���������� ��� �����?\n', 
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