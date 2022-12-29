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

STRAIGHT_FLUSH = 8
FOUR_OF_A_KIND = 7
FULL_HOUSE = 6
FLUSH = 5
STRAIGHT = 4
THREE_OF_A_KIND = 3
TWO_PAIR = 2
ONE_PAIR = 1
HIGH_CARD = 0
def cnt2(v):
    return v * (v - 1) // 2

def encode_list(l, cnt = 1):
    l = l[: cnt]
    v = 0
    for x in l:
        v = v * 13 + x
    return v

def cnk(n, k):
    a = 1
    for i in range(k):
        a *= n - i
    for i in range(1, k + 1):
        a //= i
    return a

def pnk(n, k):
    a = 1
    for i in range(k):
        a *= n - i
    return a
class CompressedCardValueAnalyzer: # does not consider suits
    def __init__(self):
        pass

    def compressed_value_getter(self, full_hand):
        def get_sorted_remains(index):  # assumes distinct
            return sorted([j for j, count in sorted_by_counts[index + 1:]], reverse=True)

        for i in range(len(full_hand) - 1, 3, -1):
            if full_hand[i] == full_hand[i - 1] + 1 == full_hand[i - 2] + 2 == full_hand[i - 3] + 3 == full_hand[
                i - 4] + 4:
                return STRAIGHT, full_hand[i]

        counts = Counter(full_hand)
        sorted_by_counts = list(counts.most_common())
        for index_i, (i, count_i) in enumerate(sorted_by_counts):
            if count_i == 4:
                return FOUR_OF_A_KIND, encode_list([i] + get_sorted_remains(index_i), cnt=2)
            elif count_i == 3:
                for index_j in range(index_i + 1, len(sorted_by_counts)):
                    j, count_j = sorted_by_counts[index_j]
                    if count_j == 2:
                        return FULL_HOUSE, encode_list([i, j], cnt=2)
                return THREE_OF_A_KIND, encode_list([i] + get_sorted_remains(index_i), cnt=3)
            elif count_i == 2:
                for index_j in range(index_i + 1, len(sorted_by_counts)):
                    j, count_j = sorted_by_counts[index_j]
                    if count_j == 2:
                        return TWO_PAIR, encode_list([max(i, j), min(i, j)] + get_sorted_remains(index_j), cnt=3)
                return ONE_PAIR, encode_list([i] + get_sorted_remains(index_i), cnt=4)
        return HIGH_CARD, encode_list(get_sorted_remains(-1), cnt=5)

    def enumerate_next_card(self, existing_cards, cnt=1):
        if cnt == 1:
            for i in range(13):
                if existing_cards[i] != 4:
                    yield (i, 4 - existing_cards[i])
        elif cnt == 2:
            for i in range(13):
                for j in range(13):
                    if i == j:
                        if existing_cards[i] < 3:
                            yield (i, j, (4 - existing_cards[i]) * (3 - existing_cards[i]))
                    else:
                        if existing_cards[i] < 4 and existing_cards[j] < 4:
                            yield (i, j, (4 - existing_cards[i]) * (4 - existing_cards[j]))

    def number_hands_better_full_common(self, player, common):
        common = sorted(common)
        existing_cards = Counter(player + common)
        my_hand = sorted(player + common)
        my_hand_value = self.compressed_value_getter(my_hand)
        answer = 0
        better_than_flush = my_hand_value > (FLUSH, 0)
        # enumerate!
        for card_value_1, card_value_2, card_count in self.enumerate_next_card(existing_cards, cnt=2):
            other_hand = sorted(common + [card_value_1, card_value_2])
            other_hand_value = self.compressed_value_getter(other_hand)
            # print(my_hand_value, other_hand_value, other_hand_value <= my_hand_value, my_hand, other_hand)
            if other_hand_value > my_hand_value:
                answer += card_count
        return answer, better_than_flush

    def number_hands_better(self, player_cards, common_cards):
        player = sorted(player_cards)
        player = [card // 4 for card in player]
        common = sorted(common_cards)
        common = [card // 4 for card in common]
        existing_cards = Counter(player + common)
        answer = 0
        better_than_flush = 0
        if len(common) == 3:
            for card_value_1, card_value_2, card_count in self.enumerate_next_card(existing_cards, cnt=2):
                _answer, _better_than_flush = self.number_hands_better_full_common(player, common + [card_value_1, card_value_2])
                answer += card_count * _answer
                better_than_flush += card_count * _better_than_flush
        elif len(common) == 4:
            for card_value_1, card_count in self.enumerate_next_card(existing_cards):
                _answer, _better_than_flush = self.number_hands_better_full_common(player, common + [card_value_1])
                answer += card_count * _answer
                better_than_flush += card_count * _better_than_flush
        else:
            _answer, _better_than_flush = self.number_hands_better_full_common(player, common)
            answer = _answer
            better_than_flush += _better_than_flush
        total_possible_combinations = pnk(50 - len(common), 7 - len(common))
        total_common_combinations = pnk(50 - len(common), 5 - len(common))
        return answer, total_possible_combinations, better_than_flush, total_common_combinations


class MonteCarloCardValueAnalyzer: # does not consider suits
    def __init__(self):
        pass

    def value_getter(self, full_hand): # full_hand: only values
        def get_sorted_remains(index): # assumes distinct
            return sorted([j for j, count in sorted_by_counts[index + 1: ]], reverse=True)

        for i in range(len(full_hand) - 1, 3, -1):
            if full_hand[i] == full_hand[i - 1] + 1 == full_hand[i - 2] + 2 == full_hand[i - 3] + 3 == full_hand[i - 4] + 4:
                return STRAIGHT, full_hand[i]

        counts = Counter(full_hand)
        sorted_by_counts = list(counts.most_common())
        sorted_by_counts = sorted(sorted_by_counts, key=lambda x: (x[1], x[0]), reverse=True)
        for index_i, (i, count_i) in enumerate(sorted_by_counts):
            if count_i == 4:
                assert index_i == 0
                return FOUR_OF_A_KIND, encode_list([i] + get_sorted_remains(index_i), cnt=2)
            elif count_i == 3:
                assert index_i == 0
                for index_j in range(index_i + 1, len(sorted_by_counts)):
                    j, count_j = sorted_by_counts[index_j]
                    if count_j >= 2:
                        return FULL_HOUSE, encode_list([i, j], cnt=2)
                return THREE_OF_A_KIND, encode_list([i] + get_sorted_remains(index_i), cnt=3)
            elif count_i == 2:
                assert index_i == 0
                for index_j in range(index_i + 1, len(sorted_by_counts)):
                    j, count_j = sorted_by_counts[index_j]
                    if count_j == 2:
                        return TWO_PAIR, encode_list([i, j] + get_sorted_remains(index_j), cnt=3)
                return ONE_PAIR, encode_list([i] + get_sorted_remains(index_i), cnt=4)
        return HIGH_CARD, encode_list(get_sorted_remains(-1), cnt=5)

    def is_straight_flush(self, full_hand): # full hand, actual cards
        full_hand = sorted(full_hand)
        for i in range(len(full_hand) - 1, 3, -1):
            if full_hand[i] == full_hand[i - 1] + 4 == full_hand[i - 2] + 8 == full_hand[i - 3] + 12 == full_hand[
                i - 4] + 16:
                return STRAIGHT_FLUSH, full_hand[i] // 4
        return 0, 0

    def is_flush(self, full_hand):
        suits = [card % 4 for card in full_hand]
        suit, count = Counter(suits).most_common()[0]
        if count >= 5:
            hands_with_suit = [card // 4 for card in full_hand if card % 4 == suit]
            return FLUSH, encode_list(sorted(hands_with_suit, reverse=True)[: 5], 5)
        return 0, 0

    def get_strength(self, full_hand):
        strengths = []
        strengths.append(self.is_straight_flush(full_hand))
        strengths.append(self.is_flush(full_hand))
        strengths.append(self.value_getter([card // 4 for card in full_hand]))
        return max(strengths)

    def hand_value(self, player_cards, common_cards, num_opponents=1, exp_cnt=1000):
        next_cards_cnt = 2 * num_opponents + 5 - len(common_cards)
        assert num_opponents <= 4, "too many opponents will make the later loop slow"
        lose = 0
        for _ in range(exp_cnt):
            next_cards = []
            filter_existing_cards = set(player_cards + common_cards)
            while len(next_cards) < next_cards_cnt:
                card = random.randint(0, 51)
                if card in filter_existing_cards: continue
                next_cards.append(card)
                filter_existing_cards.add(card)
            community_cards = common_cards + next_cards[: -2 * num_opponents]
            opponent_cards = next_cards[-2 * num_opponents: ]
            mine_value = self.get_strength(player_cards + community_cards)
            opponent_values = [self.get_strength(community_cards + opponent_cards[i * 2: i * 2 + 2]) for i in range(num_opponents)]
            max_opponent_value = max(opponent_values)
            if max_opponent_value > mine_value:
                lose += 1

        return 1 - lose / exp_cnt

# if always fold at start, lose small_blind_value * 3 / number_of_players money per game
# call in first round
# call & raise to small_blind_value * k whenever confident.
def bet_strategy_basic(player_cards, common_cards, small_blind_value, previous_bet_value, number_of_players, number_of_players_playing):
    if len(common_cards) == 0:
        # special case
        (card_1_value, card_1_suit), (card_2_value, card_2_suit) = sorted(player_cards)
        if card_1_value == card_2_value:
            return previous_bet_value
        if card_1_suit == card_2_suit:
            if card_2_value == 13:
                return previous_bet_value
        if card_1_value == card_2_value - 1 and card_1_value >= 9:
            return previous_bet_value
        if card_1_value >= 11:
            return previous_bet_value
        return 0
    else:
        c = CompressedCardValueAnalyzer()
        answer, total_possible_combinations, better_than_flush, total_common_combinations = \
            c.number_hands_better([convert_card_to_value(x) for x in player_cards], [convert_card_to_value(x) for x in common_cards])
        if gameUtil.DEBUG:
            print("kibot basic", answer, total_possible_combinations, better_than_flush, total_common_combinations)
        would_bet = (1 - answer / total_possible_combinations) >= 0.8

        player_suit = Counter([x[1] for x in player_cards])
        common_suit = Counter([x[1] for x in common_cards])
        total_suit = Counter([x[1] for x in player_cards + common_cards])
        max_occurring_suit, max_occurring_suit_count = total_suit.most_common(1)[0]
        _, max_occurring_suit_count_in_common = common_suit.most_common(1)[0]


        # suit handling
        if max_occurring_suit_count >= 5:
            return previous_bet_value + 3 * small_blind_value
        if len(common_cards) == 3 and max_occurring_suit_count >= 4:
            return previous_bet_value
        if would_bet:
            if len(common_cards) == 3 and max_occurring_suit_count_in_common == 3:
                someone_with_two = 1 / 16
                someone_with_one = 7 / 16
                someone_with_flush = someone_with_two + someone_with_one * someone_with_one
                if better_than_flush / total_common_combinations >= someone_with_flush * number_of_players_playing:
                    return previous_bet_value
                else:
                    return 0
            if len(common_cards) == 4 and max_occurring_suit_count_in_common == 4:
                someone_with_two = 1 / 16
                someone_with_one = 7 / 16
                someone_with_flush = someone_with_two + someone_with_one
                if better_than_flush / total_common_combinations >= someone_with_flush * number_of_players_playing:
                    return previous_bet_value
                else:
                    return 0
            if len(common_cards) == 4 and max_occurring_suit_count_in_common == 3:
                someone_with_two = 1 / 16
                someone_with_one = 7 / 16
                someone_with_flush = someone_with_two + someone_with_one * 1 / 4
                if better_than_flush / total_common_combinations >= someone_with_flush * number_of_players_playing:
                    return previous_bet_value
                else:
                    return 0
            if len(common_cards) == 5 and max_occurring_suit_count_in_common == 4:
                someone_with_two = 1 / 16
                someone_with_one = 7 / 16
                someone_with_flush = someone_with_two + someone_with_one
                if better_than_flush / total_common_combinations >= someone_with_flush * number_of_players_playing:
                    return previous_bet_value
                else:
                    return 0
            return previous_bet_value + 3 * small_blind_value
        return 0

def bet_strategy_basicp(player_cards, common_cards, small_blind_value, previous_bet_value,
                        number_of_players, number_of_players_playing,
                        players_playing,
                        player_bet_values=None):
    # if len(common_cards) == 0:
    #     # special case
    #     (card_1_value, card_1_suit), (card_2_value, card_2_suit) = sorted(player_cards)
    #     if card_1_value == card_2_value:
    #         return previous_bet_value
    #     if card_1_suit == card_2_suit:
    #         if card_2_value == 13:
    #             return previous_bet_value
    #     if card_1_value == card_2_value - 1 and card_1_value >= 9:
    #         return previous_bet_value
    #     if card_1_value >= 11:
    #         return previous_bet_value
    #     return 0

    c = MonteCarloCardValueAnalyzer()
    hand_value = c.hand_value([convert_card_to_value(x) for x in player_cards],
                               [convert_card_to_value(x) for x in common_cards], 1) # always consider 1 opponent
    if len(common_cards) == 0 and hand_value > 0.66:
        return previous_bet_value + 3 * small_blind_value
    if len(common_cards) == 0 and hand_value > 0.5:
        return previous_bet_value + small_blind_value
    if len(common_cards) == 0:
        return 0
    if player_bet_values is not None:
        bet_values_history = [player_bet_values[i] for i, x in enumerate(players_playing) if x]
    else:
        bet_values_history = [[] for _ in range(number_of_players_playing)]

    default_val = 0.7
    ten_percent_low = default_val
    ten_percent_high = default_val
    can_bluff = True
    for opponent in bet_values_history:
        opponent = sorted(opponent)
        if len(opponent) != 0:
            ten_percent_low = min(ten_percent_low, opponent[int(len(opponent) * 0.1)])
            ten_percent_high = max(ten_percent_high, opponent[int(len(opponent) * 0.9)])
        if len(opponent) < 5:
            can_bluff = False
    if gameUtil.DEBUG:
        print("kibot basicp", hand_value, ten_percent_low, ten_percent_high, bet_values_history)
    if can_bluff and hand_value <= ten_percent_low and random.randint(1, 10) <= 5:
        if gameUtil.DEBUG:
            print("kibot basicp", "bluff")
        return previous_bet_value + small_blind_value
    if hand_value >= ten_percent_high:
        if gameUtil.DEBUG:
            print("kibot basicp", "bet")
        return previous_bet_value + 3 * small_blind_value
    if gameUtil.DEBUG:
        print("kibot basicp", "fold")
    return 0

def initial_hand_value(player_cards):
    return initial_hand_value_dict[(convert_card_to_value(player_cards[0]), convert_card_to_value(player_cards[1]))]

def bet_strategy_basicpp(player_cards,
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
    # analyzer = CompressedCardValueAnalyzer()
    # st = time.time()
    # print(analyzer.number_hands_better(
    #     [convert_card_to_value(x) for x in [(1, 0), (2, 1)]],
    #     [convert_card_to_value(x) for x in [(13, 2), (13, 1), (13, 0)]])
    # )
    # for _ in range(10):
    #     analyzer.number_hands_better(
    #         [convert_card_to_value(x) for x in [(1, 0), (1, 1)]],
    #         [convert_card_to_value(x) for x in [(1, 2), (12, 1), (13, 2)]])
    # print(time.time() - st)

    # analyzer = MonteCarloCardValueAnalyzer()
    # st = time.time()
    # print(analyzer.hand_value(
    #     [convert_card_to_value(x) for x in [(1, 0), (2, 1)]],
    #     [convert_card_to_value(x) for x in [(13, 2), (13, 1), (13, 0)]])
    # )
    # for _ in range(10):
    #     analyzer.hand_value(
    #         [convert_card_to_value(x) for x in [(1, 0), (1, 1)]],
    #         [convert_card_to_value(x) for x in [(1, 2), (12, 1), (13, 2)]])
    # print(time.time() - st)



class kiBot():
    def __init__(self, player_index, strategy="basicp"):
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
        previous_bet_value = max(data['player bets']) - data['player bets'][self.player_index]

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
            assert previous_bet_value == 0
            return 1
        if previous_bet_value == 0:
            return 0
        if self.strategy == "basic":

            return bet_strategy_basic(self.player_cards, common_cards, small_blind_value, previous_bet_value,
                                      number_of_players,
                                      number_of_players_playing)
        elif self.strategy == "basicp":
            player_bet_values = None
            if len(common_cards) == 3:
                player_bet_values = self.player_bet_values_round_1
            elif len(common_cards) == 4:
                player_bet_values = self.player_bet_values_round_2
            elif len(common_cards) == 5:
                player_bet_values = self.player_bet_values_round_3
            return bet_strategy_basicp(self.player_cards,
                                       common_cards,
                                       small_blind_value,
                                       previous_bet_value,
                                       number_of_players,
                                       number_of_players_playing,
                                       players_playing,
                                       player_bet_values
                                       )
        elif self.strategy == "basicpp":
            player_bet_values = None
            if len(common_cards) == 3:
                player_bet_values = self.player_bet_values_round_1
            elif len(common_cards) == 4:
                player_bet_values = self.player_bet_values_round_2
            elif len(common_cards) == 5:
                player_bet_values = self.player_bet_values_round_3

            return bet_strategy_basicpp(self.player_cards,
                                        common_cards,
                                        small_blind_value,
                                        previous_bet_value,
                                        data['player bets'][self.player_index],
                                        sum(data['player bets']),
                                        number_of_players,
                                        number_of_players_playing,
                                        players_playing,
                                        player_bet_values
                                        )
    def revealed_card(self, card_array):
        if self.strategy == "basicp":
            strategy = MonteCarloCardValueAnalyzer()
            for player_index, player_cards in card_array:
                player_cards = [player_card for player_card in player_cards if player_card not in self.common_cards]
                print("player_cards", player_cards)
                print("common_cards", self.common_cards)
                assert len(player_cards) == 2
                self.player_bet_values_round_1[player_index].append(
                    strategy.hand_value(
                        [convert_card_to_value(x) for x in player_cards],
                        [convert_card_to_value(x) for x in self.common_cards[:3]],
                        1,
                    )
                )
                self.player_bet_values_round_2[player_index].append(
                    strategy.hand_value(
                        [convert_card_to_value(x) for x in player_cards],
                        [convert_card_to_value(x) for x in self.common_cards[:4]],
                        1,
                    )
                )
                self.player_bet_values_round_3[player_index].append(
                    strategy.hand_value(
                        [convert_card_to_value(x) for x in player_cards],
                        [convert_card_to_value(x) for x in self.common_cards[:5]],
                        1,
                    )
                )
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