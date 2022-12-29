import random
import time
from collections import Counter
import gameUtil

### c++ lib import
import ctypes
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
handle = ctypes.CDLL(dir_path + "/kibot.so")

handle.My_PokerHandEval.argtypes = [ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int,
                                    ctypes.c_int]
handle.My_PokerHandEval.restype = ctypes.c_double

handle.My_PokerHandEvalOnlyValue.argtypes = [   ctypes.c_int,
                                                ctypes.c_int,
                                                ctypes.c_int,
                                                ctypes.c_int,
                                                ctypes.c_int,
                                                ctypes.c_int,
                                                ctypes.c_int]
handle.My_PokerHandEvalOnlyValue.restype = ctypes.c_double

initial_hand_value_dict = {}
max_rank_values = {
    12: 10,
    11: 8,
    10: 7,
    9: 6,
    8: 5,
    7: 4.5,
    6: 4,
    5: 3.5,
    4: 3,
    3: 2.5,
    2: 2,
    1: 1.5,
    0: 1
}
gap_values = {
    0: 0,
    1: 1,
    2: 2,
    3: 4,
    4: 5,
}
for i in range(0, 52):
    for j in range(i + 1, 52):
        rank_i, suit_i = i // 4, i % 4
        rank_j, suit_j = j // 4, j % 4
        points = max_rank_values[max(rank_i, rank_j)]
        if rank_i == rank_j:
            points *= 2
            points = max(points, 5)
        if suit_i == suit_j:
            points += 2
        gap = max(rank_i, rank_j) - min(rank_i, rank_j) - 1
        if gap > 0:
            points -= gap_values[min(4, gap)]
        if gap == 0 or (gap == 1 and max(rank_i, rank_j) >= 10):
            points += 1
        initial_hand_value_dict[(i, j)] = points
initial_hand_value_list = sorted(initial_hand_value_dict.items(), key = lambda x: x[1], reverse = True)
initial_hand_value_dict = {}
t = len(initial_hand_value_list)
for hand, value in initial_hand_value_list:
    initial_hand_value_dict[hand] = (t - len(initial_hand_value_dict)) / t
    initial_hand_value_dict[(hand[1], hand[0])] = initial_hand_value_dict[hand]

def My_PokerHandEval(m0, m1, c1, c2, c3, c4, c5):
    return handle.My_PokerHandEval(m0, m1, c1, c2, c3, c4, c5)
def My_PokerHandEvalOnlyValue(m0, m1, c1, c2, c3, c4, c5):
    return handle.My_PokerHandEvalOnlyValue(m0, m1, c1, c2, c3, c4, c5)
# round_information = {
#     'stage' : 0,
#     'player money' : [STARTING_PLAYER_MONEY for i in range(NUM_PLAYER)],
#     'player bets' : [0 for i in range(NUM_PLAYER)],
#     'player playing' : [True for i in range(NUM_PLAYER)],
#     'community card' : copy.copy(deck[0: 3])
# }
# cards: [(1-13, 0-3) ...]

def convert_card_to_value(card):
    return 4 * (card[0] - 1) + card[1]

def initial_hand_value(player_cards):
    return initial_hand_value_dict[(convert_card_to_value(player_cards[0]), convert_card_to_value(player_cards[1]))]

def bet_strategy_basic(player_cards,
                       common_cards,
                       small_blind_value,
                        need_bet_value,
                        already_bet_value,
                        current_pot_value,
                        number_of_players,
                        number_of_players_playing,
                        players_playing,
                        player_bet_values=None):
    assert need_bet_value > 0


    potential_win = current_pot_value - already_bet_value
    average_lose = small_blind_value * 3 / number_of_players
    if len(common_cards) == 0:
        # special case
        hand_value = initial_hand_value(player_cards)
    else:
        hand_value = My_PokerHandEvalOnlyValue(*[convert_card_to_value(x) // 4 for x in player_cards],
                                               *[convert_card_to_value(x) // 4 for x in common_cards])
    if gameUtil.DEBUG:
        print("kiBot: hand_value = ", hand_value, "stage = ", len(common_cards))
    if hand_value > 0.66:
        return 1000
    return 0
    # if len(common_cards) == 0 and hand_value > 0.66:
    #     return previous_bet_value + 3 * small_blind_value
    # if len(common_cards) == 0 and hand_value > 0.5:
    #     return previous_bet_value + small_blind_value
    # if len(common_cards) == 0:
    #     return 0
    # if player_bet_values is not None:
    #     bet_values_history = [player_bet_values[i] for i, x in enumerate(players_playing) if x]
    # else:
    #     bet_values_history = [[] for _ in range(number_of_players_playing)]
    #
    # default_val = 0.7
    # ten_percent_low = default_val
    # ten_percent_high = default_val
    # can_bluff = True
    # for opponent in bet_values_history:
    #     opponent = sorted(opponent)
    #     if len(opponent) != 0:
    #         ten_percent_low = min(ten_percent_low, opponent[int(len(opponent) * 0.1)])
    #         ten_percent_high = max(ten_percent_high, opponent[int(len(opponent) * 0.9)])
    #     if len(opponent) < 5:
    #         can_bluff = False
    # if gameUtil.DEBUG:
    #     print("kibot basicp", hand_value, ten_percent_low, ten_percent_high, bet_values_history)
    # if can_bluff and hand_value <= ten_percent_low and random.randint(1, 10) <= 5:
    #     if gameUtil.DEBUG:
    #         print("kibot basicp", "bluff")
    #     return previous_bet_value + small_blind_value
    # if hand_value >= ten_percent_high:
    #     if gameUtil.DEBUG:
    #         print("kibot basicp", "bet")
    #     return previous_bet_value + 3 * small_blind_value
    # if gameUtil.DEBUG:
    #     print("kibot basicp", "fold")
    # return 0



if __name__ == '__main__':
    st = time.time()
    print(My_PokerHandEvalOnlyValue(36 // 4, 40 // 4, 44 // 4, 48 // 4, 52 // 4, 13 // 4, -1))
    print(My_PokerHandEvalOnlyValue(36 // 4, 40 // 4, 44 // 4, 48 // 4, 52 // 4, -1, -1))
    print(My_PokerHandEval(36, 40, 44, 48, 52, -1, -1))
    print(time.time() - st)

class kiBot():
    def __init__(self, player_index, strategy="basic"):
        self.player_index = player_index
        self.strategy = strategy

        # not used
        self.player_bet_values_round_1 = []
        self.player_bet_values_round_2 = []
        self.player_bet_values_round_3 = []

        self.player_cards = []
        self.common_cards = []
        self.number_of_players = -1

    def starting_hand(self, cards):
        self.player_cards = cards
        return 0
    def bet(self, data):
        common_cards = data['community card']
        self.common_cards = common_cards
        small_blind_value = gameUtil.SMALL_BLIND_BET_MONEY
        need_bet_value = max(data['player bets']) - data['player bets'][self.player_index]

        number_of_players = len(data['player money'])
        if self.number_of_players == -1:
            self.number_of_players = number_of_players
            self.player_bet_values_round_1 = [[] for _ in range(number_of_players)]
            self.player_bet_values_round_2 = [[] for _ in range(number_of_players)]
            self.player_bet_values_round_3 = [[] for _ in range(number_of_players)]
        number_of_players_playing = sum(data['player playing'])
        players_playing = data['player playing']
        if number_of_players_playing == 0:
            assert False, "number_of_players_playing should not be 0"
        if number_of_players_playing == 1:
            assert need_bet_value == 0
            return 1
        if need_bet_value == 0:
            return 0
        if self.strategy == "basic":
            player_bet_values = None
            if len(common_cards) == 3:
                player_bet_values = self.player_bet_values_round_1
            elif len(common_cards) == 4:
                player_bet_values = self.player_bet_values_round_2
            elif len(common_cards) == 5:
                player_bet_values = self.player_bet_values_round_3

            return bet_strategy_basic(self.player_cards,
                                        common_cards,
                                        small_blind_value,
                                        need_bet_value,
                                        data['player bets'][self.player_index],
                                        sum(data['player bets']),
                                        number_of_players,
                                        number_of_players_playing,
                                        players_playing,
                                        player_bet_values
                                        )
    def revealed_card(self, card_array):
        # if self.strategy == "basicp":
        #     strategy = MonteCarloCardValueAnalyzer()
        #     for player_index, player_cards in card_array:
        #         player_cards = [player_card for player_card in player_cards if player_card not in self.common_cards]
        #         print("player_cards", player_cards)
        #         print("common_cards", self.common_cards)
        #         assert len(player_cards) == 2
        #         self.player_bet_values_round_1[player_index].append(
        #             strategy.hand_value(
        #                 [convert_card_to_value(x) for x in player_cards],
        #                 [convert_card_to_value(x) for x in self.common_cards[:3]],
        #                 1,
        #             )
        #         )
        #         self.player_bet_values_round_2[player_index].append(
        #             strategy.hand_value(
        #                 [convert_card_to_value(x) for x in player_cards],
        #                 [convert_card_to_value(x) for x in self.common_cards[:4]],
        #                 1,
        #             )
        #         )
        #         self.player_bet_values_round_3[player_index].append(
        #             strategy.hand_value(
        #                 [convert_card_to_value(x) for x in player_cards],
        #                 [convert_card_to_value(x) for x in self.common_cards[:5]],
        #                 1,
        #             )
        #         )
        return 0
    def watch_bet(self, data):
        common_cards = data['community card']
        self.common_cards = common_cards
        number_of_players = len(data['player money'])
        if self.number_of_players == -1:
            self.number_of_players = number_of_players
            self.player_bet_values_round_1 = [[] for _ in range(number_of_players)]
            self.player_bet_values_round_2 = [[] for _ in range(number_of_players)]
            self.player_bet_values_round_3 = [[] for _ in range(number_of_players)]
        return 0
    def end_round(self):
        return