import random
import gameUtil

NUM_MCS =1000

class teddyBot():
    def __init__(self, player_index):
        self.player_index = player_index
        self.deck=[]
    def starting_hand(self, cards):
        self.mycards=cards
        self.numcards=2
        self.value=0
        self.deck.clear()
        # 生成一副牌，去掉自己的两张手牌，用于蒙特卡洛模拟
        for i in range(52):
            self.deck.append(i)
        for i in range(52):
            num = self.deck[i]
            self.deck[i] = ((num // 4 + 1) , num % 4)
        random.shuffle(self.deck)
        self.deck.remove(cards[0])
        self.deck.remove(cards[1])
        return 0

    def bet(self, data):
        if data['stage']==0:  # call if 只有手牌
            return max(data['player bets']) - data['player bets'][self.player_index]

        elif data['stage']==1:  # 三张牌:
            if data['community card'][0] in self.deck:
                self.deck.remove(data['community card'][0])
                self.deck.remove(data['community card'][1])
                self.deck.remove(data['community card'][2])
            cards = data['community card'] + self.mycards
            self.value=self.Valuecards(cards)
            won=0
            for i in range(NUM_MCS):
                random.shuffle(self.deck)
                cards[3]=self.deck[0]
                cards[4]=self.deck[1]
                if self.value>self.Valuecards(cards):
                    won=won+1

#            print(f"value won：{self.value} {won}")
            if won>NUM_MCS*0.8:     # raise
                return 2*max(data['player bets']) - data['player bets'][self.player_index]
            elif won>NUM_MCS*0.4:   # call
                return max(data['player bets']) - data['player bets'][self.player_index]
            return 0                # fold

        elif data['stage']==2:  # turn:
            self.deck.remove(data['community card'][3])
            cards = data['community card'] + self.mycards
            self.value=self.Valuecards(cards)
            won=0
            for i in range(NUM_MCS):
                random.shuffle(self.deck)
                cards[4]=self.deck[0]
                cards[5]=self.deck[1]
                if self.value>self.Valuecards(cards):
                    won=won+1

 #           print(f"value won：{self.value} {won}")
            if won>NUM_MCS*0.8:     # raise
                return 2*max(data['player bets']) - data['player bets'][self.player_index]
            elif won>NUM_MCS*0.5:   # call
                return max(data['player bets']) - data['player bets'][self.player_index]
            return 0                # fold

        elif data['stage']==3:  # river:
            self.deck.remove(data['community card'][4])
            cards = data['community card'] + self.mycards
            self.value=self.Valuecards(cards)
            won=0
            for i in range(NUM_MCS):
                random.shuffle(self.deck)
                cards[5]=self.deck[0]
                cards[6]=self.deck[1]
                if self.value>self.Valuecards(cards):
                    won=won+1

  #          print(f"value won：{self.value} {won}")
            if won>NUM_MCS*0.8:     # raise
                return 2*max(data['player bets']) - data['player bets'][self.player_index]
            elif won>NUM_MCS*0.6:   # call
                return max(data['player bets']) - data['player bets'][self.player_index]
            return 0                # fold
        return 0        # 不应该有这种情况

    def watch_bet(self, data):
        return 0
    def revealed_card(self, card_array):
        return 0
    def end_round(self):
        return

    def Valuecards(self,cards):# rank every players hand # every hand is sorted (playerindex, card) return the index of the player won
        cards = sorted(cards, key=lambda x: x[0], reverse=True)

        a,b = gameUtil.checkRoyalFlush(cards)
        if a:
            return 1800+b[0][0]
        a,b = gameUtil.fourOfAKind(cards)
        if a:
            return 1400+b[0][0]
        a,b = gameUtil.checkFullHouse(cards)
        if a:
            return 1200+b[0][0]
        a,b = gameUtil.checkFlush(cards)
        if a:
            return 1000+b[0][0]
        a,b = gameUtil.checkStraight(cards)
        if a:
            return 800+b[0][0]
        a,b = gameUtil.checkThreeOfAKind(cards)
        if a:
            return 600+b[0][0]*14+b[3][0]
        a,b = gameUtil.checkTwoPair(cards)
        if a:
            return 400+b[0][0]*14+b[4][0]
        a,b = gameUtil.checkPair(cards)
        if a:
            return 200+b[0][0]*14+b[2][0]
        a,b = gameUtil.checkHighCard(cards)
        if a:
            return b[0][0]
