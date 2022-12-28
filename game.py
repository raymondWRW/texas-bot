import allInBot
import random
import copy
STARTING_PLAYER_MONEY = 100
SMALL_BLIND_BET_MONEY = 10
BIG_BLIND_BET_MONEY = 20
DEBUG = True
players = [allInBot.allInBot(0), 
           allInBot.allInBot(1),
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
money = [STARTING_PLAYER_MONEY, STARTING_PLAYER_MONEY, STARTING_PLAYER_MONEY, STARTING_PLAYER_MONEY]
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
    'stage' : 0, # 0 = flop 1 = turn 2 = river
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

def checkHighCard(cards):
    if DEBUG:
        print("high card")
    return True, cards[0: 5]
def checkPair(cards):
    bestHand = []
    for i in range(len(cards) - 1):
        if(cards[i][0] == cards[i + 1][0]):
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            countHand = 2
            for j in range(len(cards)):
                if(j != i and j != i + 1):
                    bestHand.append(cards[j])
                    countHand += 1
                    if(countHand == 5):
                        if DEBUG:
                            print("pair")
                        return True, bestHand
    return False, bestHand
def checkTwoPair(cards):
    bestHand = []
    used = [False for i in range(7)]
    paircount = 0
    for i in range(len(cards) - 1):
        if(cards[i][0] == cards[i + 1][0]):
            used[i] == True
            used[i + 1] == True
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            paircount += 1
            i += 1
            if(paircount == 2):
                break
    for i in range(len(cards)):
        if(not used[i]):
            bestHand.append(cards[i])
            break
    if(len(bestHand) == 5):
        print("two pairs")
    return len(bestHand) == 5, bestHand
def checkThreeOfAKind(cards):
    bestHand = []
    used = [False for i in range(7)]
    count = 0
    for i in range(len(cards) - 2):
        if(cards[i][0] == cards[i + 1][0] == cards[i + 2][0]):
            used[i] == True
            used[i + 1] == True
            used[i + 2] == True
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            bestHand.append(cards[i + 2])
            break
    for i in range(len(cards)):
        if(not used[i]):
            bestHand.append(cards[i])
            count += 1
            if(count == 2):
                break
    if(len(bestHand) == 5):
        print("three of a kind")
    return len(bestHand) == 5, bestHand
def checkStraight(cards):
    possibleHand = []
    lastCardNum = 0
    for i in range(len(cards)):
        if(cards[i][0] != lastCardNum):
            possibleHand.append(cards[i])
            lastCardNum = cards[i][0]
    for i in range(len(possibleHand) - 4):
        if(possibleHand[i][0] == 
           possibleHand[i + 1][0] + 1 == 
           possibleHand[i + 2][0] + 2 == 
           possibleHand[i + 3][0] + 3 == 
           possibleHand[i + 4][0] + 4):
            if DEBUG:
                print("straight")
            return True, possibleHand[i : i + 5]
    return False, 0
def checkFlush(cards):
    suit_arr = [[],[],[],[]]
    for i in range(len(cards)):
        suit_arr[cards[i][1]].append(cards[i])
    for i in range(len(suit_arr)):
        if len(suit_arr[i]) >= 5:
            if DEBUG:
                print("flush")
            return True, suit_arr[i][0 : 5]
    return False, 0
def checkFullHouse(cards):
    bestHand = []
    used = [False for i in range(7)]
    count = 0
    for i in range(len(cards) - 2):
        if(cards[i][0] == cards[i + 1][0] == cards[i + 2][0]):
            used[i] == True
            used[i + 1] == True
            used[i + 2] == True
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            bestHand.append(cards[i + 2])
            break
    for i in range(len(cards) - 1):
        if((not used[i]) and cards[i][0] == cards[i + 1][0]):
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            break
    if DEBUG:
        if len(bestHand) == 5:
            print("full house")
    return len(bestHand) == 5, bestHand
def fourOfAKind(cards):
    bestHand = []
    used = [False for i in range(7)]
    for i in range(len(cards) - 3):
        if(cards[i][0] == cards[i + 1][0] == cards[i + 2][0] == cards[i + 3][0]):
            used[i] == True
            used[i + 1] == True
            used[i + 2] == True
            used[i + 3] == True
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            bestHand.append(cards[i + 2])
            bestHand.append(cards[i + 3])
            break
    for i in range(len(cards)):
        if(not used[i]):
            bestHand.append(cards[i])
            break
    if DEBUG:
        if len(bestHand) == 5:
            print("four of a kind")
    return len(bestHand) == 5, bestHand
def checkRoyalFlush(cards):#strongest hand
    suit_arr = [[],[],[],[]]
    for i in range(len(cards)):
        suit_arr[cards[i][1]].append(cards[i])
    for i in range(len(suit_arr)):
        if len(suit_arr[i]) >= 5:
            for i in range(len(suit_arr[i]) - 4):
                if(suit_arr[i][i][0] == 
                    suit_arr[i][i + 1][0] + 1 == 
                    suit_arr[i][i + 2][0] + 2 == 
                    suit_arr[i][i + 3][0] + 3 == 
                    suit_arr[i][i + 4][0] + 4):
                    if DEBUG:
                        print("straight flush")
                    return True, suit_arr[i][i : i + 5]
    return False, []
def cardToNumberValue(cards):
    return cards[0][0] * (13 ** 5) + cards[1][0] * (13 ** 5) + cards[2][0] * (13 ** 5) + cards[3][0] * (13 ** 5) + cards[4][0] * (13 ** 5)
def checkHand(player_card):# rank every players hand # every hand is sorted (playerindex, card)
    winningplayer = []
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = checkRoyalFlush(i[1])
            if a:
                winningplayer.append((i[0], b))
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = fourOfAKind(i[1])
            if a:
                winningplayer.append((i[0], b))
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = checkFullHouse(i[1])
            if a:
                winningplayer.append((i[0], b))
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = checkFlush(i[1])
            if a:
                winningplayer.append((i[0], b))
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = checkStraight(i[1])
            if a:
                winningplayer.append((i[0], b))
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = checkThreeOfAKind(i[1])
            if a:
                winningplayer.append((i[0], b))
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = checkTwoPair(i[1])
            if a:
                winningplayer.append((i[0], b))
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = checkPair(i[1])
            if a:
                winningplayer.append((i[0], b))
    if(len(winningplayer) == 0):
        for i in player_card:
            a,b = checkHighCard(i[1])
            if a:
                winningplayer.append((i[0], b))
    player_won = []
    player_won_value = 0
    for i in range(len(winningplayer)):
        if(cardToNumberValue(winningplayer[i][1]) > player_won_value):
            player_won_value = cardToNumberValue(winningplayer[i][1])
            player_won = []
            player_won.append(winningplayer[i][0])
    return player_won
def cards_to_player_cards(cards):
    temp = []
    for i in cards:
        temp.append(NUMBER_DICT[i[0]] + SUIT_DICT[i[1]])
    return temp
def round_information_to_player_information(): 
    return  {
        'stage' : 0, # 0 = flop 1 = turn 2 = river
        'player money' : copy.copy(round_information['player money']),
        'player bets' : copy.copy(round_information['player bets']),
        'player playing' : copy.copy(round_information['player playing']),
        'community card' : cards_to_player_cards(round_information['community card'])
    }
#still need to get all in
for round_number in range(10):
    player_betting_index = (small_blind_index + 2) % NUM_PLAYER
    # card
    random.shuffle(deck)
    for i in range(NUM_PLAYER):
        players[i].starting_hand(cards_to_player_cards([deck[i * 2], deck[i * 2 + 1]]))
    community_card = copy.copy(deck[NUM_PLAYER * 2: NUM_PLAYER * 2 + 5])
    #round_information
    round_information
    round_information['stage'] = 0
    round_information['player bets'] = [0 for i in range(NUM_PLAYER)]
    round_information['player playing'] = [True for i in range(NUM_PLAYER)] 
    round_information['community card'] = copy.copy(community_card[0: 3])
    #debug
    if DEBUG:
        print(f"ROUND {round_number + 1} STARTING")
        print(f"player's money: {round_information['player money']}")
        for i in range(NUM_PLAYER):
            print(f"Player {i + 1} cards are ", cards_to_player_cards([deck[i * 2], deck[i * 2 + 1]]))
        print("the community cards are", cards_to_player_cards(community_card))
        print(f"Player {small_blind_index + 1} card is the small blind")
    #starting money
    round_information['player money'][small_blind_index] -= 10
    round_information['player money'][(small_blind_index + 1) % NUM_PLAYER] -= 20
    round_information['player bets'][small_blind_index] += 10
    round_information['player bets'][(small_blind_index + 1) % NUM_PLAYER] += 20
    roundonce = 0
    while(round_information['stage'] != 3): # simulatinng rounds
        if (ifAdvance() and roundonce >= NUM_PLAYER):
            if sum(round_information['player playing']) == 1:
                winner = 0
                for i in round_information['player playing']:
                    if round_information['player playing'][i]:
                        winner = i
                round_information['player money'][i] += sum(round_information['player bets'])
                if DEBUG:
                    print(f"player {winner + 1} wins as every one else folds")
                break
            else:
                roundonce = 0
                round_information['stage'] += 1
                player_betting_index = small_blind_index
                community_card = copy.copy(community_card[0: 3 + round_information['stage']])
                if DEBUG:
                    print(f"advances to round {round_information['stage']}")
                continue
        elif round_information['player playing'][player_betting_index]:
            amount = players[player_betting_index].bet(round_information_to_player_information())
            if DEBUG:
                if amount + round_information['player bets'][player_betting_index] < max(round_information['player bets']):
                    print(f"player {player_betting_index + 1} folds")
                elif amount + round_information['player bets'][player_betting_index] == max(round_information['player bets']):
                    print(f"player {player_betting_index + 1} calls")
                else:
                    print(f"player {player_betting_index + 1} raises to {amount + round_information['player bets'][player_betting_index]}")
            round_information['player money'][player_betting_index] -= amount
            round_information['player bets'][player_betting_index] += amount
            if round_information['player bets'][player_betting_index] != max(round_information['player bets']):
                round_information['player playing'][player_betting_index] = False
        roundonce += 1
        player_betting_index = (player_betting_index + 1) % NUM_PLAYER
    if(round_information['stage'] == 3): #after the river
        player_card_combination = []
        for i in range(len(round_information['player playing'])):
            if round_information['player playing'][i]:
                card_combine = [deck[i * 2]] + [deck[i * 2 + 1]] + community_card
                card_combine = sorted(card_combine, key=lambda x: x[0], reverse=True)
                player_card_combination.append((i, card_combine))
        winner = checkHand(player_card_combination)
        for i in range(len(winner)):
            round_information['player money'][winner[i]] += sum(round_information['player bets']) // len(winner)
        for i in range(len(players)):
            players[i].revealed_card(player_card_combination)
        if DEBUG:
            print("player", end = '')
            for i in (winner):
                print(i, end = ' ')
            print("wins")
    small_blind_index = (small_blind_index + 1) % NUM_PLAYER
    for i in range(len(players)):
        players[i].end_round()
    if DEBUG:
        for i in range(5):
            print()
print("final money", round_information['player money'])
        
            