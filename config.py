import numpy as np
import PIL 
from PIL import Image

TOKEN = '353611790:AAG5VYHt7OhfghcUJ-nGkHYqyYUIbI-eNlI'
NUMBERS = np.array(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'])
NUMBERS_NUM = {'A': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, 
               '8': 7, '9': 8, '10': 9, 'J': 10, 'Q': 11, 'K': 12}
SPADE = u'\U00002660'
CLUB = u'\U00002663'
HEART = u'\U00002665'
DIAMOND = u'\U00002666'
SUITS = np.array([SPADE, CLUB, HEART, DIAMOND])
SUITS_NUM = {SPADE: 0, CLUB: 1, HEART: 2, DIAMOND: 3}
SUITS_STR = np.array(['spade', 'club', 'heart', 'diamond'])

im_cell = Image.open("cell.png")
x, y = im_cell.size
dx = x // 10
dy = y // 3

class Card:
    def __init__(self, i=-1, j=-1, figure=-1):
        self.row = i
        self.column = j
        self.figure = figure

class Game:
    def __init__(self):
        playing_field = [i for i in range(52)]
        np.random.shuffle(playing_field)
        
        playing_field.extend([-1, -1, -1, -1])
        self.playing_field = list(np.array(playing_field).reshape((7, 8)))                
        self.home = [-1, -1, -1, -1]
        self.frees = [-1 for i in range(4)]           
        
    def __str__(self):
        answer = ''
        for i in range(4):
            if self.home[i] == -1:
                answer += u'\U00002611'
            else:
                answer += SUITS[i] + NUMBERS[self.home[i]]
        answer += '\t' + '\t' + '\t' + '\t' + '\t' + '\t'
        for elem in self.frees:
            if elem == -1:
                answer += u'\U00002611'
            else:
                current_suit, current_number = divmod(elem, 13)
                answer += SUITS[current_suit] + NUMBERS[current_number]
        answer += '\n'
        answer += '1' + u'\U00002796' + '2' + u'\U00002796' + '3' + \
            u'\U00002796' + '4' + u'\U00002796' + '5' + u'\U00002796' + '6' + \
            u'\U00002796' + '7' + u'\U00002796' + '8' + u'\U00002796' + '\n'
        for i in range(len(self.playing_field)):
            for j in range(8):
                if self.playing_field[i][j] != -1:
                    current_suit, current_number = divmod(self.playing_field[i][j], 13)
                    answer += SUITS[current_suit] + NUMBERS[current_number]
                else:
                    answer += u'\U00002796' + '\t' + '\t'
            answer += '\n'
        return answer
        
    def take_photo(self, name):
        new_im = Image.new('RGB', ((x + dx) * 8 + dx, 
                                   dy * (len(self.playing_field) - 1) + y * 2 + dx * 3), 
                           (22, 132, 66))       
        for i in range(4):
            if self.home[i] == -1:
                new_im.paste(im_cell, (i * (x + dx // 2) + dx, dx))
            else:
                im = Image.open(SUITS_STR[i] + "_" + NUMBERS[self.home[i]] + ".png")
                new_im.paste(im, (i * (x + dx // 2) + dx, dx))

        for i in range(4):
            if self.frees[i] == -1:
                new_im.paste(im_cell, (i * (x + dx // 2) + 4 * x + 7 * dx - dx // 2, dx))
            else:
                current_suit, current_number = divmod(self.frees[i], 13)
                im = Image.open(SUITS_STR[current_suit] + "_" + 
                                NUMBERS[current_number] + ".png")
                new_im.paste(im, (i * (x + dx // 2) + 4 * x + 7 * dx - dx // 2, dx))
        
        last = [len(self.playing_field) for i in range(8)]
        for j in range(8): 
            for i in range(len(self.playing_field)):
                if self.playing_field[i][j] != -1:
                    current_suit, current_number = divmod(self.playing_field[i][j], 13)
                    im = Image.open(SUITS_STR[current_suit] + "_" + 
                                    NUMBERS[current_number] + ".png")
                    new_im.paste(im.crop((0, 0, x, dy)), 
                                 (j * (x + dx) + dx, y + 2 * dx + i * dy))
                else:
                    last[j] = i
                    break
        for i in range(8):
            if last[i] != 0:
                current_suit, current_number = divmod(self.playing_field[last[i] - 1][i], 13)
                im = Image.open(SUITS_STR[current_suit] + "_" + 
                                NUMBERS[current_number] + ".png")
                new_im.paste(im.crop((0, dy, x, y)), 
                             (i * (x + dx) + dx, y + 2 * dx + last[i] * dy))
        new_im.save(name + ".png")
        return name + ".png"
        
    def is_there_free(self):
        for elem in self.frees:
            if elem == -1:
                return True
        return False
    
    def is_there_home(self, suit, number):
        if self.home[SUITS_NUM[suit]] == number - 1:
            return True
        return False
    
    def suitable_column(self, suit, number):
        answer = []
        for j in range(8):
            for i in range(len(self.playing_field) - 1, -1, -1):
                if self.playing_field[i][j] != -1:
                    current_suit, current_number = divmod(self.playing_field[i][j], 13)
                    if is_opposite(suit, SUITS[current_suit]) & (current_number == number + 1):
                        answer.append(j + 1)
                    break
                if i == 0:
                    answer.append(j + 1)
        return answer        
    
    def moving_cards_in_field(self):
        answer = []
        for j in range(8):
            for i in range(len(self.playing_field) - 1, -1, -1):
                if self.playing_field[i][j] != -1:
                    answer.append(self.playing_field[i][j])
                    break
        return answer
                
    def moving_cards_in_frees(self):
        answer = []
        for elem in self.frees:
            if elem != -1:
                answer.append(elem)
        return answer
    
    def find_in_field(self, suit, number):
        figure = SUITS_NUM[suit] * 13 + number
        for j in range(8):
            for i in range(len(self.playing_field) - 1, -1, -1):
                if self.playing_field[i][j] != -1:
                    if self.playing_field[i][j] == figure:
                        return i, j, figure
        return -1, -1, -1
    
    def find_in_frees(self, suit, number):
        figure = SUITS_NUM[suit] * 13 + number
        for i in range(4):
            if self.frees[i] == figure:
                return i, figure
        return -1, -1
        
    
    def move_to_free(self, i, j, figure):
        for k in range(4):
            if self.frees[k] == -1:
                self.frees[k] = figure
                break
        if j == -1:
            self.frees[i] = -1
        else:
            self.playing_field[i][j] = -1
            
    def move_to_home(self, i, j, figure):
        suit, number = divmod(figure, 13)
        self.home[suit] = number
        if j == -1:
            self.frees[i] = -1
        else:
            self.playing_field[i][j] = -1 
            
    def move_to_column(self, i, j, figure, new_column):
        if j == -1:
            self.frees[i] = -1
        else:
            self.playing_field[i][j] = -1 
        if self.playing_field[len(self.playing_field) - 1][new_column] != -1:
            self.playing_field.append([-1, -1, -1, -1, -1, -1, -1, -1])
            self.playing_field[len(self.playing_field) - 1][new_column] = figure
            return
        for i in range(len(self.playing_field) - 1, -1, -1):
            if self.playing_field[i][new_column] != -1:
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