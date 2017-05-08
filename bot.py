import telebot
from telebot import types
import config
import logging

bot = telebot.TeleBot(config.TOKEN)

logger = logging.getLogger(__name__)
handler = logging.FileHandler("my_logger.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - \
%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

game_fields = {}
RULES = "\
    C���������� ������ ���� �������������� � 8 �������, ������ ������� �� 7 \
���� � ������ � �� 6. ����� ����� ������� �������� �����.\n\
������ ����� 4 ������, ��� ���������� ������, ������ �� ��� 4 ����������� \
������. �� ������ ������ ���� ��� ��� �����.\n\
� ���� ��������� ������������ ������� ����� �� ������� ��� ��������� ������\n\
    � ����� ������ ������� �� ��������� �� ����������� ����� ������� �����;\n\
    � ����� �������������� �������;\n\
    � ����� ������ \"���������\" ������;\n\
    � \"���\", ������� � ���� � ���������� ������ ��� �� �����.\n\
������� ��������, ���� ������ ����������� ��� ������ � ����."

def get_name(message):
    name = message.from_user.first_name
    if hasattr(message.from_user, "last_name") \
       and message.from_user.last_name is not None:
        name += u" {}".format(message.from_user.last_name)
    if hasattr(message.from_user, "username") \
       and message.from_user.username is not None:
        name += u" (@{})".format(message.from_user.username)
    return name

def logg_info_record(message, text, level):    
    logger.setLevel(level)
    handler.setLevel(level)    
    logger.info("In the chat {} user {} {}".format(
        message.chat.id, get_name(message), text))  
    
def logg_error_record(message, text, level):   
    logger.setLevel(level)
    handler.setLevel(level)    
    logger.error("In the chat {} user {} {}".format(
        message.chat.id, get_name(message), text))      
    

@bot.message_handler(commands=["start"])
def start(message):   
    logg_info_record(message, "joins the game", logging.INFO)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("����� ����", "������ ������� ����")
    msg = bot.send_message(message.chat.id, 
                           text="����� ���������� � ����, {}".format(
                               get_name(message)), reply_markup=markup)
    bot.register_next_step_handler(msg, steps)

def steps(message):
    if (message.text=="����� ����") | (message.text=="������ ����"):
        new_game(message)
    elif message.text=="������ ������� ����":
        first_rules(message)
    elif message.text=="������� ����":
        rules(message)
    elif (message.text=="�����"):
        start(message)
    elif (message.text=="������� ������ �����") | (message.text=="�����"):
        step(message)
    elif ((message.text[0]==config.SPADE) | (message.text[0]==config.CLUB) | 
          (message.text[0]==config.HEART) | (message.text[0]==config.DIAMOND)):
        #�������� ����� �������� ��� ��������
        moving(message)
    elif (message.text=="��������� ������"):
        move_to_free(message)
    elif (message.text=="���"):
        move_to_home(message)
    elif (message.text[1:9]==" �������"):
        move_to_column(message)
    elif (message.text == "/start"):
        nothing = 0
    else:
        error(message)
        
def error(message):
    chat_id = message.chat.id
    logg_error_record(message, "requests incorrect command", logging.ERROR)
    msg = bot.send_message(chat_id, text="�����-�� ������")
    bot.register_next_step_handler(msg, steps)  

def first_rules(message):
    chat_id = message.chat.id
    logg_info_record(message, "asks about the rules", logging.INFO)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("������ ����", "�����")
    msg = bot.send_message(chat_id, text=RULES, reply_markup=markup)
    bot.register_next_step_handler(msg, steps)    
        
def rules(message):
    chat_id = message.chat.id
    logg_info_record(message, "asked about the rules", logging.INFO)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("�����")
    msg = bot.send_message(chat_id, text=RULES, reply_markup=markup)
    bot.register_next_step_handler(msg, steps)
    
def step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    with open(game_fields[chat_id, user_id][0].take_photo(
        "{} {}".format(str(chat_id), str(user_id))), "rb") as f:
        bot.send_photo(chat_id, photo=f)  
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)   
    end_of_game = True
    
    moving_cards = game_fields[chat_id, user_id][0].moving_cards_in_frees()
    keyboards = []
    for elem in moving_cards:
        end_of_game = False
        suit, number = divmod(elem, 13)
        keyboards.append("{}{}".format(config.SUITS[suit], 
                                       config.NUMBERS[number]))
    markup.row(*[types.KeyboardButton(name) for name in keyboards])
    
    moving_cards = game_fields[chat_id, user_id][0].moving_cards_in_field()
    keyboards = []
    for elem in moving_cards:
        end_of_game = False
        suit, number = divmod(elem, 13)
        keyboards.append("{}{}".format(config.SUITS[suit], 
                                       config.NUMBERS[number]))
    if len(keyboards) <= 4:
        markup.row(*[types.KeyboardButton(name) for name in keyboards]) 
    else:
        markup.row(*[types.KeyboardButton(name) 
                     for name in keyboards[:len(keyboards) // 2]]) 
        markup.row(*[types.KeyboardButton(name) 
                     for name in keyboards[len(keyboards) // 2:]])     
    
    if(end_of_game):
        finish(message)
    else:    
        markup.row("����� ����")
        markup.row("�����", "������� ����")
        msg = bot.send_message(chat_id, 
                               text="����� ����� �� ������ ����������?", 
                               reply_markup=markup)
        bot.register_next_step_handler(msg, steps)
    
def finish(message):
    chat_id = message.chat.id
    logg_info_record(message, "wins the game", logging.INFO)   
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("����� ����", "�����")
    msg = bot.send_message(chat_id, text="����������, �� ����������!", 
                           reply_markup=markup)
    bot.send_sticker(chat_id, data="CAADAgAD-QsAAiMhBQAB9_KHkFe4N40C") 
    bot.register_next_step_handler(msg, steps)

def new_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    logg_info_record(message, "starts new game", logging.INFO) 
    game_fields[chat_id, user_id] = [config.Game(), config.Card()]
    step(message)
    
def moving(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    logg_info_record(message, "choses card {} {}".format(
        config.SUITS_STR[config.SUITS_NUM[message.text[0]]], 
        message.text[1:]), logging.INFO)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    suit = message.text[0]
    number = config.NUMBERS_NUM[message.text[1:]]
    
    i, j, figure = game_fields[chat_id, user_id][0].find_in_field(suit, number)
    if j == -1:
        i, figure = game_fields[chat_id, user_id][0].find_in_frees(suit, number)
        game_fields[chat_id, user_id][1] = config.Card(i, -1, figure)
    else:
        game_fields[chat_id, user_id][1] = config.Card(i, j, figure)
        
    keyboards = []
    if game_fields[chat_id, user_id][0].is_there_home(suit, number):
        keyboards.append("���")
    if game_fields[chat_id, user_id][0].is_there_free():
        keyboards.append("��������� ������")
    markup.row(*[types.KeyboardButton(name) for name in keyboards])
    
    column = game_fields[chat_id, user_id][0].suitable_column(suit, number)
    keyboards = []
    for elem in column:
        keyboards.append("{} �������".format(str(elem)))
    markup.row(*[types.KeyboardButton(name) for name in keyboards])
    
    markup.row("������� ������ �����")
    markup.row("�����", "������� ����")
    msg = bot.send_message(chat_id, 
                           text="���� �� ������ ���������� ��� �����?\n", 
                           reply_markup=markup)
    bot.register_next_step_handler(msg, steps)
    
def move_to_free(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_suit, current_number = divmod(
        game_fields[chat_id, user_id][1].figure, 13)
    logg_info_record(message, "moves card {} {} to the open cells".format(
        config.SUITS_STR[current_suit], config.NUMBERS[current_number]), 
                logging.INFO)    
    game_fields[chat_id, user_id][0].move_to_free(
        game_fields[chat_id, user_id][1].row, 
        game_fields[chat_id, user_id][1].column, 
        game_fields[chat_id, user_id][1].figure)
    step(message)    
 
def move_to_home(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_suit, current_number = divmod(
        game_fields[chat_id, user_id][1].figure, 13)   
    logg_info_record(message, "moves card {} {} to foundations".format(
        config.SUITS_STR[current_suit], config.NUMBERS[current_number]), 
                logging.INFO)      
    game_fields[chat_id, user_id][0].move_to_home(
        game_fields[chat_id, user_id][1].row, 
        game_fields[chat_id, user_id][1].column, 
        game_fields[chat_id, user_id][1].figure)
    step(message) 
 
def move_to_column(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_suit, current_number = divmod(
        game_fields[chat_id, user_id][1].figure, 13)    
    new_column = int(message.text[0]) - 1
    logg_info_record(message, "moves card {} {} to {} column".format(
        config.SUITS_STR[current_suit], config.NUMBERS[current_number], 
        message.text[0]), logging.INFO)     
    game_fields[chat_id, user_id][0].move_to_column(
        game_fields[chat_id, user_id][1].row, 
        game_fields[chat_id, user_id][1].column, 
        game_fields[chat_id, user_id][1].figure, new_column)
    step(message) 

bot.polling()
