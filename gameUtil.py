DEBUG = True
STARTING_PLAYER_MONEY = 0
SMALL_BLIND_BET_MONEY = 10
BIG_BLIND_BET_MONEY = 20
BET_LIMIT_CEILING = 1000
ROUND_NUMBER = 10
# hand comparison function
def checkHighCard(cards):
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
                        return True, bestHand
    return False, bestHand
def checkTwoPair(cards):
    bestHand = []
    used = [False for i in range(7)]
    paircount = 0
    for i in range(len(cards) - 1):
        if(cards[i][0] == cards[i + 1][0]):
            used[i] = True
            used[i + 1] = True
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
            return True, possibleHand[i : i + 5]
    return False, 0
def checkFlush(cards):
    suit_arr = [[],[],[],[]]
    for i in range(len(cards)):
        suit_arr[cards[i][1]].append(cards[i])
    for i in range(len(suit_arr)):
        if len(suit_arr[i]) >= 5:
            return True, suit_arr[i][0 : 5]
    return False, 0
def checkFullHouse(cards):
    bestHand = []
    used = [False for i in range(7)]
    count = 0
    for i in range(len(cards) - 2):
        if(cards[i][0] == cards[i + 1][0] == cards[i + 2][0]):
            used[i] = True
            used[i + 1] = True
            used[i + 2] = True
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            bestHand.append(cards[i + 2])
            break
    for i in range(len(cards) - 1):
        if((not used[i]) and cards[i][0] == cards[i + 1][0]):
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            break
    return len(bestHand) == 5, bestHand
def fourOfAKind(cards):
    bestHand = []
    used = [False for i in range(7)]
    for i in range(len(cards) - 3):
        if(cards[i][0] == cards[i + 1][0] == cards[i + 2][0] == cards[i + 3][0]):
            used[i] = True
            used[i + 1] = True
            used[i + 2] = True
            used[i + 3] = True
            bestHand.append(cards[i])
            bestHand.append(cards[i + 1])
            bestHand.append(cards[i + 2])
            bestHand.append(cards[i + 3])
            break
    for i in range(len(cards)):
        if(not used[i]):
            bestHand.append(cards[i])
            break
    return len(bestHand) == 5, bestHand
def checkRoyalFlush(cards):#strongest hand
    suit_arr = [[],[],[],[]]
    for i in range(len(cards)):
        suit_arr[cards[i][1]].append(cards[i])
    for i in range(len(suit_arr)):
        if len(suit_arr[i]) >= 5:
            for j in range(len(suit_arr[i]) - 4):
                if(suit_arr[i][j][0] == 
                    suit_arr[i][j + 1][0] + 1 == 
                    suit_arr[i][j + 2][0] + 2 == 
                    suit_arr[i][j + 3][0] + 3 == 
                    suit_arr[i][j + 4][0] + 4):
                    return True, suit_arr[i][j : j + 5]
    return False, []
def cardToNumberValue(cards):# compare two hand by card value
    return cards[0][0] * (13 ** 5) + cards[1][0] * (13 ** 4) + cards[2][0] * (13 ** 3) + cards[3][0] * (13 ** 2) + cards[4][0] * (13 ** 1)
def checkHand(player_card):# rank every players hand # every hand is sorted (playerindex, card) return the index of the player won
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
    player_won_value = max([cardToNumberValue(winningplayer[i][1]) for i in range(len(winningplayer))])
    for i in range(len(winningplayer)):
        if(cardToNumberValue(winningplayer[i][1]) >= player_won_value):
            player_won.append(winningplayer[i][0])
    return player_won