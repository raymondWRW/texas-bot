import random
import gameUtil
import statistics
# 'stage' : 0, # 0 = preflop 1 = flop 2 = turn 3 = river
# 'player money' : [STARTING_PLAYER_MONEY for i in range(NUM_PLAYER)],
# 'player bets' : [0 for i in range(NUM_PLAYER)],
# 'player playing' : [True for i in range(NUM_PLAYER)],
# 'community card' : copy.copy(deck[0: 3])
REPITITION = 1000
suit = [(12, 5), (8,7),(9,7), (13, 7), (10,7),(12, 6), (11, 7), (13, 4),(12, 7), (13 ,5), (9, 8), (10, 8),(13 ,6), (11, 8), (14, 2), (12, 7), (13, 7)]
unsuited = [(14, 3),(13, 8),(14, 4), (14, 6), (10 ,9),(11, 9), (14 , 5), (12, 9), (14 , 7), (13, 9),(14, 8)]
pair = [(4,4), (5,5)]
class raymondBot():
    def __init__(self, player_index):
        self.player_index = player_index
        self.hand = [(1,0),(2,0)]
        self.deck = []
        self.community_cards = [] # what the community card is
        self.bettinghistory = []
        for i in range(4):
            self.bettinghistory.append([[],[],[]]) #power for flop turn and river
        self.round_number = 0
        self.fold = [0, 0, 0, 0]
    def checkHand(self, player_card):# without suits
        winningplayer = []
        if(len(winningplayer) == 0):
            for i in player_card:
                a,b = gameUtil.fourOfAKind(i[1])
                if a:
                    winningplayer.append((i[0], b))
        if(len(winningplayer) == 0):
            for i in player_card:
                a,b = gameUtil.checkFullHouse(i[1])
                if a:
                    winningplayer.append((i[0], b))
        if(len(winningplayer) == 0):
            for i in player_card:
                a,b = gameUtil.checkStraight(i[1])
                if a:
                    winningplayer.append((i[0], b))
        if(len(winningplayer) == 0):
            for i in player_card:
                a,b = gameUtil.checkThreeOfAKind(i[1])
                if a:
                    winningplayer.append((i[0], b))
        if(len(winningplayer) == 0):
            for i in player_card:
                a,b = gameUtil.checkTwoPair(i[1])
                if a:
                    winningplayer.append((i[0], b))
        if(len(winningplayer) == 0):
            for i in player_card:
                a,b = gameUtil.checkPair(i[1])
                if a:
                    winningplayer.append((i[0], b))
        if(len(winningplayer) == 0):
            for i in player_card:
                a,b = gameUtil.checkHighCard(i[1])
                if a:
                    winningplayer.append((i[0], b))
        player_won = []
        player_won_value = max([gameUtil.cardToNumberValue(winningplayer[i][1]) for i in range(len(winningplayer))])
        for i in range(len(winningplayer)):
            if(gameUtil.cardToNumberValue(winningplayer[i][1]) >= player_won_value):
                player_won.append(winningplayer[i][0])
        return player_won
    def init_deck(self):
        self.deck = []
        for i in range(52):
            self.deck.append(i)
        for i in range(52):
            self.deck[i] = ((self.deck[i] // 4 + 1) , self.deck[i] % 4)
    def evaluate_preflop_hand(self):#false to fold true to call
        number_hand_value = sorted([self.hand[0][0], self.hand[0][1]])
        if(self.hand[0][0] == self.hand[1][0]):# pair
            if(self.hand[0][0] >= 4):
                return True
        if(self.hand[0][1] == self.hand[1][1]):# suited
            for i in suit:
                if(number_hand_value[0] >= i[0] and number_hand_value[1] > i[1]):
                    return True
        if(self.hand[0][1] != self.hand[1][1]):# suited
            for i in unsuited:
                if(number_hand_value[0] >= i[0] and number_hand_value[1] > i[1]):
                    return True
        return True
    def stage01(self, mycard, community):#flop return loss and total
        loss = 0
        for i in range(1, 14):
            for j in range(1, 14):
                for k in range(1, 14):
                    my_card = sorted(mycard + community + [(k, 4)], key=lambda x: x[0], reverse=True)
                    opponent = sorted(community + [(i,4), (j, 4), (k, 4)], key=lambda x: x[0], reverse=True)
                    loss += self.checkHand([(0, my_card), (1, opponent)])[0] == 1
        return loss
    def evalStage2(self, mycard, community):#river
        loss = 0
        for i in range(len(self.deck)):
            for j in range(len(self.deck)):
                if i != j:
                    my_card = sorted(mycard+ community, key=lambda x: x[0], reverse=True)
                    opponent = sorted(community + [self.deck[i], self.deck[j]], key=lambda x: x[0], reverse=True)
                    loss += gameUtil.checkHand([(0, my_card),(1, opponent)])[0] == 1
        return loss
    def starting_hand(self, cards):
        self.round_number += 1
        self.hand = cards
        return 0
    def bet(self, data):
        #store the community cards
        self.init_deck()
        self.community_cards = data['community card']
        for i in self.hand + self.community_cards:
            if i in self.deck:
                self.deck.remove(i)
        if(data['stage'] == 0):
            if(data['player bets'][self.player_index] <= 20):
                if(self.evaluate_preflop_hand()):
                    return max(data['player bets']) - data['player bets'][self.player_index]
                else:
                    return 0
            else:
                return max(data['player bets']) - data['player bets'][self.player_index]
        if(data['stage'] == 1 or data['stage'] == 2):
            value = self.stage01(self.hand, self.community_cards)
            conitnuebetting = True
            double = True
            for i in range(len(data['player playing'])):
                if data['player playing'][i]:
                    if len(self.bettinghistory[i][data['stage'] - 1]) != 0:
                        mean_value = statistics.mean(self.bettinghistory[i][data['stage'] - 1])
                        if(value * 0.9 > mean_value ):
                            conitnuebetting = False
                        if(value * 2 < mean_value):
                            double = False
                    else:
                        return max(data['player bets']) - data['player bets'][self.player_index]
            if conitnuebetting:
                if double:
                    return sum(data['player bets']) - data['player bets'][self.player_index]
                return max(data['player bets']) - data['player bets'][self.player_index]
            else:
                return 0
        else:
            value = self.evalStage2(self.hand, self.community_cards)
            conitnuebetting = True
            for i in range(len(data['player playing'])):
                if data['player playing'][i]:
                    if len(self.bettinghistory[i][data['stage'] - 1]) != 0:
                        mean_value = statistics.mean(self.bettinghistory[i][data['stage'] - 1])
                        if(value * 0.9 > mean_value ):
                            conitnuebetting = False
                    else:
                        return max(data['player bets']) - data['player bets'][self.player_index]
            if conitnuebetting:
                return max(data['player bets']) - data['player bets'][self.player_index]
            else:
                return 0
    def watch_bet(self, data):
        self.community_cards = data['community card']
        return 0
    def revealed_card(self, card_array):
        #review
        for i in range(len(card_array)):
            self.init_deck()
            opponent_hand = card_array[i][1]
            opponent_index = card_array[i][0]
            for j in self.community_cards:
                opponent_hand.remove(j)
            self.bettinghistory[opponent_index][0].append(self.stage01(opponent_hand , self.community_cards[0 : 3]))
            self.bettinghistory[opponent_index][1].append(self.stage01(opponent_hand , self.community_cards[0 : 4]))
            self.bettinghistory[opponent_index][2].append(self.evalStage2(opponent_hand , self.community_cards))
            #     opponent_power = self.chancePower(opponent_hand)
            #     opponent_hand.remove(self.community_cards[4 - j])
            #     self.bettinghistory[opponent_index][2 - j].append(opponent_power)
        return 0
    def end_round(self):
        return