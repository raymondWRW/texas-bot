import random
class easyBot():
    def __init__(self, player_index):
        self.player_index = player_index
    def starting_hand(self, cards):
        # print(cards)
        return 0
    def bet(self, data):
        # print(data)
        if (random.random() > 0.5):
            return 0 # fold
        else: # call
            return max(data['player bets']) - data['player bets'][self.player_index]
    def revealed_card(self, card_array):
        return 0
    def end_round(self):
        return