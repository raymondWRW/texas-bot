import random
import gameUtil as gu

class sunnyBot():
    
    def __init__(self, player_index):
        self.player_index = player_index
    def starting_hand(self, cards):
        self.myCards=cards
        return 0
    def bet(self, data):
        level =0
        self.curCards=self.myCards+data['community card']
        self.curCards = sorted(self.curCards, key=lambda x: x[0], reverse=True)
        ifTrue,c = gu.checkRoyalFlush(self.curCards) 
        if ifTrue:
            level=20
        else:
            ifTrue,c = gu.fourOfAKind(self.curCards)
            if ifTrue:
                level = 20
            else:
                ifTrue,c = gu.checkFullHouse(self.curCards)
                if ifTrue:
                    level = 20
                else:
                    ifTrue,c = gu.checkFlush(self.curCards)
                    if ifTrue:
                        level =16
                    else:
                        ifTrue,c = gu.checkStraight(self.curCards)
                        if ifTrue:
                            if c[0][0]>10:
                                level =10
                            else:
                                level=9
                        else:
                            ifTrue,c = gu.checkThreeOfAKind(self.curCards)
                            if ifTrue:
                                if c[0][0]> 10:
                                    level = 8
                                else:
                                    level=7
                            else:
                                ifTrue,c = gu.checkTwoPair(self.curCards)
                                if ifTrue:
                                    if c[0][0]> 10:
                                        level =6
                                    else:
                                        level =5
                                else:
                                    ifTrue,c = gu.checkPair(self.curCards)
                                    if ifTrue:
                                        if c[0][0]> 10:
                                            level =4
                                        else:
                                            level =3
                                    else:
                                        ifTrue,c = gu.checkHighCard(self.curCards)
                                        if c[0][0]> 10:
                                            level =2
                                        else:
                                            level =0
       # return max(max(data['player bets']) - data['player bets'][self.player_index], 1000)
        if (level < 3):
            return 0
        if level >8:
            return 10000
        return max(level*50 - data['player bets'][self.player_index],max(data['player bets']))
      #  return max((max(data['player bets']) - data['player bets'][self.player_index]),level*50)
        
     
    def revealed_card(self, card_array):
        return 0
    def watch_bet(self, data):
        return 0
    def end_round(self):
        return

 