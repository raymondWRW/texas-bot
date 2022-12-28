import random
class allInBot():
    def __init__(self, player_index):
        self.player_index = player_index
    def starting_hand(self, cards):
        # print(cards)
        return 0
    def bet(self, data):
        return max(max(data['player bets']) - data['player bets'][self.player_index], 1000)
    def revealed_card(self, card_array):
        return 0
    def watch_bet(self, data):
        return 0
    def end_round(self):
        return