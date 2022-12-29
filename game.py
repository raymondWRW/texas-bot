import os

import allInBot
import easyBot
import sunnyBot
import kiBot
import functools
import random
import copy
import gameUtil
import sys
from gameUtil import DEBUG, STARTING_PLAYER_MONEY, SMALL_BLIND_BET_MONEY, BIG_BLIND_BET_MONEY, BET_LIMIT_CEILING, ROUND_NUMBER

if os.environ["USE_COMMAND_LINE"] == "True":
    ROUND_NUMBER = int(sys.argv[1])
    player_names = sys.argv[2: ]
    player_maps = {
        'easyBot': easyBot.easyBot,
        'allInBot': allInBot.allInBot,
        'sunnyBot': sunnyBot.sunnyBot,
        'kiBot-basic': functools.partial(kiBot.kiBot, strategy='basic'),
        'kiBot-basicp': functools.partial(kiBot.kiBot, strategy='basicp'),
        'kiBot-basicpp': functools.partial(kiBot.kiBot, strategy='basicpp'),
    }
    players = [player_maps[name](index) for index, name in enumerate(player_names)]
else:
    players = [easyBot.easyBot(0),
               easyBot.easyBot(1),
               allInBot.allInBot(2),
               allInBot.allInBot(3)]
SUIT_DICT = {
    0 : "♤",
    1 : "♡",
    2 : "♢",
    3 : "♧"
}
NUMBER_DICT = {
    1 : "2",
    2 : "3",
    3 : "4",
    4 : "5",
    5 : "6",
    6 : "7",
    7 : "8",
    8 : "9",
    9 : "10",
    10 : "J",
    11 : "Q",
    12 : "K",
    13 : "A"
}
NUM_PLAYER = len(players)
small_blind_index = 0
deck = []
community_card = []
def init_deck():
    global deck
    for i in range(52):
        deck.append(i)
    for i in range(52):
        num = deck[i]
        deck[i] = ((num // 4 + 1) , num % 4)
init_deck()
if DEBUG:
    print("DECK INITIALIZED")
round_information = {
    'stage' : 0, # 0 = preflop 1 = flop 2 = turn 3 = river
    'player money' : [STARTING_PLAYER_MONEY for i in range(NUM_PLAYER)],
    'player bets' : [0 for i in range(NUM_PLAYER)],
    'player playing' : [True for i in range(NUM_PLAYER)],
    'community card' : copy.copy(deck[0: 3])
}
def ifAdvance():
    for i in range(NUM_PLAYER):
        if(round_information['player playing'][i]):
            if(round_information['player bets'][i] != max(round_information['player bets'])):
                return False
    return True
def cards_to_player_cards(cards):# convert the card format to what the human see
    temp = []
    for i in cards:
        temp.append(NUMBER_DICT[i[0]] + SUIT_DICT[i[1]])
    return temp
def round_information_to_player_information(): 
    return  {
        'stage' : copy.deepcopy(round_information['stage']), # 0 = flop 1 = turn 2 = river
        'player money' : copy.deepcopy(round_information['player money']),
        'player bets' : copy.deepcopy(round_information['player bets']),
        'player playing' : copy.deepcopy(round_information['player playing']),
        'community card' : copy.deepcopy(round_information['community card'])
    }
#still need to get all in
for round_number in range(ROUND_NUMBER):
    player_betting_index = (small_blind_index + 2) % NUM_PLAYER
    # card
    random.shuffle(deck)
    for i in range(NUM_PLAYER):
        players[i].starting_hand([deck[i * 2], deck[i * 2 + 1]])
    community_card = copy.copy(deck[NUM_PLAYER * 2: NUM_PLAYER * 2 + 5])
    #round_information
    round_information['stage'] = 0
    round_information['player bets'] = [0 for i in range(NUM_PLAYER)]
    round_information['player playing'] = [True for i in range(NUM_PLAYER)] 
    round_information['community card'] = []
    #debug
    if DEBUG:
        print(f"ROUND {round_number + 1} STARTING")
        print(f"player's money: {round_information['player money']}")
        for i in range(NUM_PLAYER):
            print(f"Player {i + 1} cards are ", cards_to_player_cards([deck[i * 2], deck[i * 2 + 1]]))
        print("the community cards are", cards_to_player_cards(community_card))
        print(f"Player {small_blind_index + 1} card is the small blind")
    #starting money
    round_information['player money'][small_blind_index] -= SMALL_BLIND_BET_MONEY
    round_information['player money'][(small_blind_index + 1) % NUM_PLAYER] -= BIG_BLIND_BET_MONEY
    round_information['player bets'][small_blind_index] += SMALL_BLIND_BET_MONEY
    round_information['player bets'][(small_blind_index + 1) % NUM_PLAYER] += BIG_BLIND_BET_MONEY
    roundonce = 0
    while(round_information['stage'] != 4): # simulatinng rounds
        if (ifAdvance() and roundonce >= NUM_PLAYER):
            if DEBUG:
                print(f"the current community card revealed is {cards_to_player_cards(round_information['community card'])}")
            if sum(round_information['player playing']) == 1: # only one player playing
                winner = 0
                for i in range(len(round_information['player playing'])):
                    if round_information['player playing'][i]:
                        winner = i
                round_information['player money'][winner] += sum(round_information['player bets'])
                if DEBUG:
                    print(f"player {winner + 1} wins as everyone else folds")
                break
            else: # round advance as normal
                roundonce = 0
                round_information['stage'] += 1
                player_betting_index = small_blind_index
                if round_information['stage'] == 4:
                    break
                round_information['community card'] = copy.copy(community_card[0: 2 + round_information['stage']])
                if DEBUG:
                    print(f"advances to round {round_information['stage']}")
                continue
        elif round_information['player playing'][player_betting_index]:
            amount = players[player_betting_index].bet(round_information_to_player_information())
            amount = max(amount, 0)
            if DEBUG:
                if amount + round_information['player bets'][player_betting_index] < max(round_information['player bets']):
                    print(f"player {player_betting_index + 1} folds")
                elif amount + round_information['player bets'][player_betting_index] == max(round_information['player bets']):
                    print(f"player {player_betting_index + 1} calls")
                else:
                    print(f"player {player_betting_index + 1} raises to {min(amount + round_information['player bets'][player_betting_index], BET_LIMIT_CEILING)}")
            round_information['player money'][player_betting_index] -= min(amount, BET_LIMIT_CEILING - round_information['player bets'][player_betting_index])
            round_information['player bets'][player_betting_index] += min(amount, BET_LIMIT_CEILING - round_information['player bets'][player_betting_index])
            if round_information['player bets'][player_betting_index] != max(round_information['player bets']):
                round_information['player playing'][player_betting_index] = False
        else:
            players[player_betting_index].watch_bet(round_information_to_player_information())
        roundonce += 1
        player_betting_index = (player_betting_index + 1) % NUM_PLAYER
    if(round_information['stage'] == 4): #after the river
        player_card_combination = []
        for i in range(len(round_information['player playing'])):
            if round_information['player playing'][i]:
                card_combine = [deck[i * 2]] + [deck[i * 2 + 1]] + community_card
                card_combine = sorted(card_combine, key=lambda x: x[0], reverse=True)
                player_card_combination.append((i, card_combine))
        winner = gameUtil.checkHand(player_card_combination)
        for i in range(len(winner)):
            round_information['player money'][winner[i]] += sum(round_information['player bets']) // len(winner)
        for i in range(len(players)):
            players[i].revealed_card(player_card_combination)
        if DEBUG:
            print("player", end = '')
            for i in (winner):
                print(i + 1, end = ' ')
            print("wins")
    small_blind_index = (small_blind_index + 1) % NUM_PLAYER
    for i in range(len(players)):
        players[i].end_round()
    if DEBUG:
        print("########################################################################")
print("final money", round_information['player money'])
        
            