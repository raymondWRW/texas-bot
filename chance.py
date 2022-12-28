import random

'''
Rank:
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Joker = 11
    Queen = 12
    King = 13
    Ace = 14 / (1)
Suit:
    Diamonds = 1
    Spades = 2
    Hearts = 3
    Clubs = 4
    Total P: 2598960
    Straight Flush: 5 in same suit, same seq order             P: 40
    Four of a kind: 4 numerically equivalent cards             P: 624
    Full House: 3 numerically equivalent, and a pair           P: 3744
    Flush: 5 in same suit                                      P: 5108
    Straight: 5 in seq order                                   P: 10200
    Three of a kind: 3 numerically equivalent                  P: 54912
    Two pair: two different pairs                              P: 123552
    One pair: A single pair                                    P: 1098240
    High card: Highest ranked card                             P: 1302540
    Checking logic:
    if is_flush:
        if is_straight_some:
------------Straight Flush
        else:
------------Flush
    else if is_straight:
--------Straight
    else if is_four:
--------Four of a kind
    else if is_three:
        if is_pair:
------------Full House
        else:
------------Three of a kind
    else if is_pair:
        if is_second_pair:
------------Two pair
        else:
------------One pair
    else:
--------High card
'''

'''
    The only functions that should be called outside are: input_card, get_cards_for_print, calculate_value
    calculate_value should be called after input_card.
'''


class GetPercentage:
    '''
        hands should be more than or equal to 5
        Does not allow hands more than or equal to 10. Since there might be two flushes.
    '''

    def __init__(self):
        self.layer_permutations = [40, 624, 3744, 5108, 10200, 54912, 123552, 1098240, 1302540]
        self.sum_permutations = [40, 664, 4408, 9516, 19716, 74628, 198180, 1296420, 2598960]
        self.rank_name_map = {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
                              9: "Nine", 10: "Ten", 11: "Joker", 12: "Queen", 13: "King", 14: "Ace"}
        self.suit_name_map = {1: "Diamond", 2: "Spades", 3: "Heart", 4: "Clubs"}
        self.db_rank_map = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11,'Q':12,'K':13,'A':14}
        self.db_suit_map = {'d':1, 's':2, 'h':3,'c':4}
        self.ranks = []
        self.suits = []
        self.size = 0
        self.rank_map = {}

    def input_card(self, arr_hand_rank, arr_hand_suit):
        self.ranks = map(lambda x: self.db_rank_map[x] if x in self.db_rank_map else x,arr_hand_rank)
        self.suits = map(lambda x: self.db_suit_map[x] if x in self.db_suit_map else x,arr_hand_suit)
        # self.ranks = arr_hand_rank
        # self.suits = arr_hand_suit
        self.size = len(self.ranks)
        if self.size != len(arr_hand_suit) or self.size >= 10:
            raise ValueError('Wrong input')
        self.rank_map = {}
        for x in self.ranks:
            if x == 14:
                if x in self.rank_map:
                    self.rank_map[1] += 1
                    self.rank_map[14] += 1
                else:
                    self.rank_map[1] = 1
                    self.rank_map[14] = 1
            else:
                if x in self.rank_map:
                    self.rank_map[x] += 1
                else:
                    self.rank_map[x] = 1
        return self


    def get_cards_for_print(self):
        res_str = ""
        for i in xrange(self.size):
            res_str += self.transform_rank(self.ranks[i]) + " of " + self.transform_suit(self.suits[i]) + ", "
        return res_str

    def transform_rank(self, rank):
        return self.rank_name_map[rank]

    def transform_suit(self, suit):
        return self.suit_name_map[suit]

    def calculate_value(self):
        return 1 - (self.better_hands() + 0.0) / self.sum_permutations[8]

    '''
        gets the number of hands better than this.
        Do not consider effect of hands to the deck: if i have a 5 of clubs, then others would not be able to make
        a four of 5s.
    '''

    def better_hands(self):
        flush_result = self.is_flush()
        if flush_result is not None:
            straight_result = self.is_straight_some(flush_result)
            if straight_result is not None:
                # return 1
                return (14 - straight_result) * 4
            else:
                # return 4
                res_0 = self.sum_permutations[2]
                hi, res_1 = self.hi_card_rank(flush_result)
                return res_0 + res_1 - (15 - hi)
        else:
            straight_result = self.is_straight()
            if straight_result is not None:
                # return 5
                res_0 = self.sum_permutations[3]
                res_1 = (14 - straight_result) * 1020  # (1020 = 10200 / 10  || 1020 = 2^10 - 4)
                return res_0 + res_1

        same_rank_result = self.has_same_cards()
        if same_rank_result is not None:
            if same_rank_result[0] == 4:
                # return 2
                hi_index = self.highest_rank_discard_rank([same_rank_result[1]])
                hi_rank = self.ranks[hi_index]
                res_0 = self.sum_permutations[0]
                res_1 = (14 - same_rank_result[1]) * 4 * 12
                res_2 = 52 - hi_rank * 4
                if hi_rank > same_rank_result[1]:
                    res_2 += 4
                return res_0 + res_1 + res_2
            elif same_rank_result[0] == 3:
                pair_result = self.is_pair(same_rank_result[1])
                if pair_result is not None:
                    # return 3
                    res_0 = self.sum_permutations[1]
                    res_1 = (14 - same_rank_result[1]) * 4 * 12 * 6
                    res_2 = (13 - pair_result) * 6 * 4
                    if pair_result > same_rank_result[1]:
                        res_2 += 24
                    return res_0 + res_1 + res_2
                else:
                    # return 6
                    res_0 = self.sum_permutations[4]
                    hi_card_1 = self.ranks[self.highest_rank_discard_rank([same_rank_result[1]])]
                    hi_card_2 = self.ranks[self.highest_rank_discard_rank([same_rank_result[1], hi_card_1])]
                    res_1 = (14 - same_rank_result[1]) * 4 * 48 * 44 / 2  # 54912 / 13
                    res_2 = (14 - hi_card_1) * (hi_card_1 + 11) / 2 + hi_card_1 - hi_card_2 - 1
                    res_3 = 0
                    if same_rank_result[1] > hi_card_1:
                        res_3 -= same_rank_result[1] - 2
                    else:
                        res_3 -= 14 - hi_card_1
                        if same_rank_result[1] < hi_card_2:
                            res_3 -= 1
                    return res_0 + res_1 + res_2 + res_3
            elif same_rank_result[0] == 2:
                other_pair_result = self.is_second_pair(same_rank_result[1])
                if other_pair_result is not None:
                    # return 7
                    res_0 = self.sum_permutations[5]
                    res_1 = self.hi_card_rank([same_rank_result[1], other_pair_result], True)[1] * 6 * 6 * 44
                    hi_rank = self.highest_rank_discard_rank([same_rank_result[1], other_pair_result])
                    res_2 = 14 - hi_rank
                    if hi_rank < other_pair_result:
                        res_2 -= 2
                    elif hi_rank < same_rank_result[1]:
                        res_2 -= 1
                    res_2 *= 4
                    return res_0 + res_1 + res_2
                else:
                    # return 8 not accurate
                    res_0 = self.sum_permutations[6]
                    res_1 = (14 - same_rank_result[1]) * 48 * 44 * 40  # ( * 6 / 6 )
                    hi_card_index_1 = self.highest_rank_discard_rank([same_rank_result[1]])
                    hi_card_index_2 = self.highest_rank_discard_rank([same_rank_result[1], self.ranks[hi_card_index_1]])
                    hi_card_index_3 = self.highest_rank_discard_rank(
                        [same_rank_result[1], self.ranks[hi_card_index_1], self.ranks[hi_card_index_2]])
                    res_2 = self.hi_card_rank([hi_card_index_1, hi_card_index_2, hi_card_index_3])[1] * 4 * 4 * 4
                    # res_3 = 0
                    # if self.ranks[hi_card_index_1] < same_rank_result[1]:
                    #     res_3 -= (same_rank_result[1] - 2) * (same_rank_result[1] - 3) / 2
                    # elif self.ranks[hi_card_index_2] < same_rank_result[1]:
                    #     res_3 -= (same_rank_result[1] - 2)
                    #     res_3 -=
                    return res_0 + res_1 + res_2
        else:
            res_0 = self.sum_permutations[7]
            max_single, res_1 = self.hi_card_rank(xrange(self.size))
            res_1 *= 4**5 - 4
            res_2 = -(15 - max_single) * (4**5 - 4)
            return res_0 + res_1 + res_2

    '''
        returns None if not straight,
        else returns the highest rank
        @return: None or 5 ~ 14
    '''

    def is_straight(self):
        for i in xrange(14, 4, -1):
            if i in self.rank_map and i - 1 in self.rank_map and i - 2 in self.rank_map and \
                                    i - 3 in self.rank_map and i - 4 in self.rank_map:
                return i
        return None

    '''
        given some cards >= 5
        returns None if not straight,
        else returns the highest rank
        @return: None or 5 ~ 14
    '''

    def is_straight_some(self, arr_hand_value_indexes):
        rank_map = {}
        for x in arr_hand_value_indexes:
            r = self.ranks[x]
            if r == 14:
                if r in rank_map:
                    rank_map[1] += 1
                    rank_map[14] += 1
                else:
                    rank_map[1] = 1
                    rank_map[14] = 1
            else:
                if r in rank_map:
                    rank_map[r] += 1
                else:
                    rank_map[r] = 1
        for i in xrange(14, 4, -1):
            if i in rank_map and i - 1 in rank_map and i - 2 in rank_map and \
                                    i - 3 in rank_map and i - 4 in rank_map:
                return i
        return None

    '''
        returns None if not flush,
        else returns an array indicating the indexes
        @return: None or [>=5]
    '''

    def is_flush(self):
        suit_arr = [0, 0, 0, 0]
        suit_index_arr = [[], [], [], []]
        for i in xrange(self.size):
            suit_arr[self.suits[i] - 1] += 1
            suit_index_arr[self.suits[i] - 1].append(i)
        for i in xrange(4):
            if suit_arr[i] >= 5:
                return suit_index_arr[i]
        return None

    '''
        returns None if no cards have same rank
        else returns (the highest number of same cards, the corresponding highest rank)
    '''

    def has_same_cards(self):
        max_same = 1
        max_same_rank = 0
        for rank, duplicate in self.rank_map.iteritems():
            if duplicate > max_same:
                max_same = duplicate
                max_same_rank = rank
            elif duplicate == max_same and rank > max_same_rank:
                max_same = duplicate
                max_same_rank = rank
        if max_same != 1:
            return (max_same, max_same_rank)
        else:
            return None

    '''
        returns None if no four same rank cards,
        else returns the highest rank
    '''

    def is_four(self, discard_rank):
        max_four = 0
        for key, value in self.rank_map.iteritems():
            if value >= 4 and key != discard_rank and key > max_four:
                max_four = key
        if max_four > 0:
            return max_four
        return None

    '''
        returns None if no three same rank cards,
        else returns the highest rank
    '''

    def is_three(self, discard_rank):
        max_three = 0
        for key, value in self.rank_map.iteritems():
            if value >= 3 and key != discard_rank and key > max_three:
                max_three = key
        if max_three > 0:
            return max_three
        return None

    '''
        returns None if no two same rank cards,
        else returns the highest rank
    '''
    def is_pair(self, discard_rank):
        max_pair = 0
        for key, value in self.rank_map.iteritems():
            if value >= 2 and key > max_pair and key != discard_rank:
                max_pair = key
        if max_pair > 0:
            return max_pair
        return None

    '''
        Given that a pair already exists,
        returns None if no other two same rank cards,
        else returns the highest rank
        @input exist_pair, the rank of the existing pair
    '''

    def is_second_pair(self, exist_pair):
        max_pair = 0
        for key, value in self.rank_map.iteritems():
            if value == 2 and key != exist_pair and key > max_pair:
                max_pair = key
        if max_pair > 0:
            return max_pair
        return None

    '''
        Given a rank to discard, return the highest rank left, considering its suit.
        @return returns its index
    '''

    def highest_rank_discard_rank(self, discard_rank):
        hi_r = 0
        hi_s = 0
        hi = -1
        for i in xrange(self.size):
            if self.ranks[i] not in discard_rank:
                if self.ranks[i] > hi_r:
                    hi_r = self.ranks[i]
                    hi_s = self.suits[i]
                    hi = i
                elif self.ranks[i] == hi_r and self.suits[i] > hi_s:
                    hi_r = self.ranks[i]
                    hi_s = self.suits[i]
                    hi = i
        if hi == -1:
            raise ValueError('Corrupted input')
        return hi

    def hi_card_rank(self, index, by_rank=False):
        ranks = []
        if by_rank:
            ranks = index
        else:
            ranks = sorted([self.ranks[i] for i in index], reverse=True)
        ret = 0
        for i in xrange(min(5, ranks.__len__())):
            hi = 14
            if i >= 1:
                hi = ranks[i - 1] - 1
            ret += self.n_different_card_choose_k1_k2(min(5, ranks.__len__()) - 1 - i, ranks[i] - 1, hi - 2)
        return ranks[0], ret

    def n_different_card_choose_k1_k2(self, n, k1, k2):
        if not n < k1 <= k2:
            return 0
        ret = 0
        for k in xrange(k1, k2 + 1, 1):
            ret += self.combine_count(k, n)
        return ret

    @staticmethod
    def combine_count(total, take):
        res_u = 1
        res_d = 1
        for x in xrange(total, total - take, -1):
            res_u *= x
            res_d *= (total + 1 - x)
        return res_u / res_d