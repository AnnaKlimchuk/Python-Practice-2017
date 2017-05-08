import numpy as np
import PIL 
from PIL import Image

TOKEN = '353611790:AAG5VYHt7OhfghcUJ-nGkHYqyYUIbI-eNlI'
NUMBERS = np.array(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', \
                    'Q', 'K'])
NUMBERS_NUM = {'A': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, 
               '8': 7, '9': 8, '10': 9, 'J': 10, 'Q': 11, 'K': 12}
SPADE = u'\U00002660'
CLUB = u'\U00002663'
HEART = u'\U00002665'
DIAMOND = u'\U00002666'
NOTHING = u'\U00002611'
SUITS = np.array([SPADE, CLUB, HEART, DIAMOND])
SUITS_NUM = {SPADE: 0, CLUB: 1, HEART: 2, DIAMOND: 3}
SUITS_STR = np.array(['spade', 'club', 'heart', 'diamond'])
STANDARD_DECK = 52
CASCADES = 8
OPEN_CELLS = 4
FOUNDATIONS = 4
NO_ROW = -1
NO_COLUMN = -1
NO_CARD = -1

with Image.open("./cards/cell.png") as im_cell:
    x, y = im_cell.size
dx = x // 10
dy = y // 3

def card_position(i, shift):
    return i * (x + dx // 2) + dx + shift, dx

def card_position_at_home(i):
    return card_position(i, 0)

def card_position_at_field(i, j):
    return j * (x + dx) + dx, y + 2 * dx + i * dy

class Card:
    def __init__(self, i=NO_ROW, j=NO_COLUMN, figure=NO_CARD):
        self.row = i
        self.column = j
        self.figure = figure

def field_sides(max_cascade):
    return (x + dx) * 8 + dx, dy * (max_cascade - 1) + y * 2 + dx * 3

class Game:
    def __init__(self):
        playing_field = [i for i in range(STANDARD_DECK)]
        np.random.shuffle(playing_field)
        
        playing_field.extend([NO_CARD, NO_CARD, NO_CARD, NO_CARD])
        self.playing_field = list(np.array(playing_field).reshape((7, 8)))                
        self.home = [NO_CARD for i in range(FOUNDATIONS)]
        self.frees = [NO_CARD for i in range(OPEN_CELLS)]           
        
    def __str__(self):
        answer = ''
        for i in range(FOUNDATIONS):
            if self.home[i] == NO_CARD:
                answer += NOTHING
            else:
                answer += SUITS[i] + NUMBERS[self.home[i]]
        answer += '\t' + '\t' + '\t' + '\t' + '\t' + '\t'
        for elem in self.frees:
            if elem == NO_CARD:
                answer += NOTHING
            else:
                current_suit, current_number = divmod(elem, 13)
                answer += SUITS[current_suit] + NUMBERS[current_number]
        answer += '\n'
        answer += '1' + NOTHING + '2' + NOTHING + '3' + NOTHING + '4' + \
            NOTHING + '5' + NOTHING + '6' + NOTHING + '7' + NOTHING + '8' + \
            NOTHING + '\n'
        for i in range(len(self.playing_field)):
            for j in range(CASCADES):
                if self.playing_field[i][j] != NO_CARD:
                    current_suit, current_number = divmod(
                        self.playing_field[i][j], 13)
                    answer += SUITS[current_suit] + NUMBERS[current_number]
                else:
                    answer += NOTHING + '\t' + '\t'
            answer += '\n'
        return answer
        
    def take_photo(self, name):
        with Image.new('RGB', field_sides(len(self.playing_field)), 
                       (22, 132, 66)) as new_im:
            with Image.open("./cards/cell.png") as im_cell:
                for i in range(FOUNDATIONS):
                    if self.home[i] == NO_CARD:
                        new_im.paste(im_cell, card_position_at_home(i))
                    else:
                        with Image.open("./cards/{}_{}.png".format(
                            SUITS_STR[i], NUMBERS[self.home[i]])) as im:
                            new_im.paste(im, card_position_at_home(i))

                for i in range(OPEN_CELLS):
                    shift = 4 * x + 6 * dx - dx // 2
                    if self.frees[i] == NO_CARD:
                        new_im.paste(im_cell, card_position(i, shift))
                    else:
                        current_suit, current_number = divmod(self.frees[i], 13)
                        with Image.open("./cards/{}_{}.png".format(
                            SUITS_STR[current_suit], 
                            NUMBERS[current_number])) as im:
                            new_im.paste(im, card_position(i, shift))
                            
            last = [len(self.playing_field) for i in range(CASCADES)]
            for j in range(CASCADES): 
                for i in range(len(self.playing_field)):
                    if self.playing_field[i][j] != NO_CARD:
                        current_suit, current_number = divmod(
                            self.playing_field[i][j], 13)
                        with Image.open("./cards/{}_{}.png".format(
                            SUITS_STR[current_suit], 
                            NUMBERS[current_number])) as im:
                            new_im.paste(im.crop((0, 0, x, dy)), 
                                         card_position_at_field(i, j))
                    else:
                        last[j] = i
                        break
            for i in range(CASCADES):
                if last[i] != 0:
                    current_suit, current_number = divmod(
                        self.playing_field[last[i] - 1][i], 13)
                    with Image.open("./cards/{}_{}.png".format(
                        SUITS_STR[current_suit], 
                        NUMBERS[current_number])) as im:
                        new_im.paste(im.crop((0, dy, x, y)), 
                                     card_position_at_field(last[i], i))                        
            new_im.save("./cards/{}.png".format(name))
            return "./cards/{}.png".format(name)
        
    def is_there_free(self):
        for elem in self.frees:
            if elem == NO_CARD:
                return True
        return False
    
    def is_there_home(self, suit, number):
        if self.home[SUITS_NUM[suit]] == number - 1:
            return True
        return False
    
    def suitable_column(self, suit, number):
        answer = []
        for j in range(CASCADES):
            for i in range(len(self.playing_field) - 1, -1, -1):
                if self.playing_field[i][j] != NO_CARD:
                    current_suit, current_number = divmod(
                        self.playing_field[i][j], 13)
                    if is_opposite(suit, SUITS[current_suit]) & \
                       (current_number == number + 1):
                        answer.append(j + 1)
                    break
                if i == 0:
                    answer.append(j + 1)
        return answer        
    
    def moving_cards_in_field(self):
        answer = []
        for j in range(CASCADES):
            for i in range(len(self.playing_field) - 1, -1, -1):
                if self.playing_field[i][j] != NO_CARD:
                    answer.append(self.playing_field[i][j])
                    break
        return answer
                
    def moving_cards_in_frees(self):
        answer = []
        for elem in self.frees:
            if elem != NO_CARD:
                answer.append(elem)
        return answer
    
    def find_in_field(self, suit, number):
        figure = SUITS_NUM[suit] * 13 + number
        for j in range(CASCADES):
            for i in range(len(self.playing_field) - 1, -1, -1):
                if self.playing_field[i][j] != NO_CARD:
                    if self.playing_field[i][j] == figure:
                        return i, j, figure
        return -1, NO_COLUMN, NO_CARD
    
    def find_in_frees(self, suit, number):
        figure = SUITS_NUM[suit] * 13 + number
        for i in range(OPEN_CELLS):
            if self.frees[i] == figure:
                return i, figure
        return NO_COLUMN, NO_CARD
        
    
    def move_to_free(self, i, j, figure):
        for k in range(OPEN_CELLS):
            if self.frees[k] == NO_CARD:
                self.frees[k] = figure
                break
        if j == NO_COLUMN:
            self.frees[i] = NO_CARD
        else:
            self.playing_field[i][j] = NO_CARD
            
    def move_to_home(self, i, j, figure):
        suit, number = divmod(figure, 13)
        self.home[suit] = number
        if j == NO_COLUMN:
            self.frees[i] = NO_CARD
        else:
            self.playing_field[i][j] = NO_CARD
            
    def move_to_column(self, i, j, figure, new_column):
        if j == NO_COLUMN:
            self.frees[i] = NO_CARD
        else:
            self.playing_field[i][j] = NO_CARD 
        if self.playing_field[len(self.playing_field) - 1][new_column] != \
           NO_CARD:
            self.playing_field.append([NO_CARD for i in range(CASCADES)])
            self.playing_field[len(self.playing_field) - 1][new_column] = figure
            return
        for i in range(len(self.playing_field) - 1, -1, -1):
            if self.playing_field[i][new_column] != NO_CARD:
                self.playing_field[i + 1][new_column] = figure
                return  
        self.playing_field[0][new_column] = figure

def is_opposite(suit1, suit2):
    red = {DIAMOND, HEART}
    black = {SPADE, CLUB}
    if (suit1 in red) & (suit2 in black):
        return True
    elif (suit1 in black) & (suit2 in red):
        return True
    return False
