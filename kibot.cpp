#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

const int STRAIGHT_FLUSH = 8;
const int FOUR_OF_A_KIND = 7;
const int FULL_HOUSE = 6;
const int FLUSH = 5;
const int STRAIGHT = 4;
const int THREE_OF_A_KIND = 3;
const int TWO_PAIR = 2;
const int ONE_PAIR = 1;
const int HIGH_CARD = 0;

static unsigned long x=123456789, y=362436069, z=521288629;

unsigned long xorshf96(void) {          //period 2^96-1
    unsigned long t;
    x ^= x << 16;
    x ^= x >> 5;
    x ^= x << 1;

    t = x;
    x = y;
    y = z;
    z = t ^ x ^ y;
    return z;
}

template <typename T,typename U>
std::pair<T,U> operator+(const std::pair<T,U> & l,const std::pair<T,U> & r) {
    return {l.first+r.first,l.second+r.second};
}

int encode_list(const vector<int> & list, int max_cnt) {
    int result = 0;
    for (int i = 0; i < max_cnt; i++) {
        result = result * 13 + list[i];
    }
    return result;
}

pair<int, int> get_rank_of_hand_only_values(vector<int> hand) {
    sort(hand.begin(), hand.end());
    int n = 7;
    for (int i = n - 1; i > 1; i--) {
        if (hand[i] == hand[i - 1] + 1 && hand[i] == hand[i - 2] + 2 && hand[i] == hand[i - 3] + 3 && hand[i] == hand[i - 4] + 4) {
            return {STRAIGHT, hand[i]};
        }
    }
    int cnt[13] = {0};
    for (int i = 0; i < n; i++) {
        cnt[hand[i]]++;
    }
    for (int i = 0; i < 13; i++) {
        if (cnt[i] == 4) {
            for (int j = 12; j >= 0; j--) {
                if (i != j && cnt[j] >= 1) {
                    return {FOUR_OF_A_KIND, encode_list({i, j}, 2)};
                }
            }
        }
    }
    for (int i = 12; i >= 0; i--) {
        if (cnt[i] == 3) {
            for (int j = 12; j >= 0; j--) {
                if (i != j && cnt[j] >= 2) {
                    return {FULL_HOUSE, encode_list({i, j}, 2)};
                }
            }
            for (int j = 12; j >= 0; j--) {
                if (i != j && cnt[j] >= 1) {
                    for (int k = j - 1; k >= 0; k--) {
                        if (i != k && cnt[k] >= 1) {
                            return {THREE_OF_A_KIND, encode_list({i, j, k}, 3)};
                        }
                    }
                }
            }
        }
    }
    for (int i = 12; i >= 0; i--) {
        if (cnt[i] == 2) {
            for (int j = i - 1; j >= 0; j--) {
                if (cnt[j] >= 2) {
                    for (int k = 12; k >= 0; k--) {
                        if (i != k && j != k && cnt[k] >= 1) {
                            return {TWO_PAIR, encode_list({i, j, k}, 3)};
                        }
                    }
                }
            }
            for (int j = 12; j >= 0; j--) {
                if (i != j && cnt[j] >= 1) {
                    for (int k = j - 1; k >= 0; k--) {
                        if (i != k && cnt[k] >= 1) {
                            for (int l = k - 1; l >= 0; l--) {
                                if (i != l && cnt[l] >= 1) {
                                    return {ONE_PAIR, encode_list({i, j, k, l}, 4)};
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    reverse(hand.begin(), hand.end());
    return {HIGH_CARD, encode_list(hand, 5)};
}

pair<int, int> get_rank_of_hand(vector<int> hand) {
    int n = 7;
    sort(hand.begin(), hand.end());
    for (int i = n - 1; i > 3; i--) {
        if (hand[i] == hand[i - 1] + 4 && hand[i] == hand[i - 2] + 8 && hand[i] == hand[i - 3] + 12 && hand[i] == hand[i - 4] + 16) {
            return {STRAIGHT_FLUSH, hand[i]};
        }
    }
    vector<int> suit_count = {0, 0, 0, 0};
    for (int h: hand) {
        suit_count[h % 4]++;
    }
    for (int i = 0; i < 4; i++) {
        if (suit_count[i] >= 5) {
            vector<int> values;
            for (int h: hand) {
                if (h % 4 == i) {
                    values.push_back(h / 4);
                }
            }
            sort(values.begin(), values.end());
            reverse(values.begin(), values.end());
            return {FLUSH, encode_list(values, 5)};
        }
    }
    vector<int> only_values;
    for (int h: hand) {
        only_values.push_back(h / 4);
    }
    return get_rank_of_hand_only_values(only_values);
}

pair<int, int> CompareHandsDeterministic(int m0, int m1, int c1, int c2, int c3, int c4, int c5, int o0, int o1) {
    if (c4 == -1) {
        pair<int, int> answer = {0, 0};
        for (int i = 0; i < 52; i++) {
            if (i == m0) continue;
            if (i == m1) continue;
            if (i == c1) continue;
            if (i == c2) continue;
            if (i == c3) continue;
            if (i == o0) continue;
            if (i == o1) continue;
            answer = answer + CompareHandsDeterministic(m0, m1, c1, c2, c3, i, c5, o0, o1);
        }
        return answer;
    } else if (c5 == -1) {
        pair<int, int> answer = {0, 0};
        for (int i = 0; i < 52; i++) {
            if (i == m0) continue;
            if (i == m1) continue;
            if (i == c1) continue;
            if (i == c2) continue;
            if (i == c3) continue;
            if (i == c4) continue;
            if (i == o0) continue;
            if (i == o1) continue;
            answer = answer + CompareHandsDeterministic(m0, m1, c1, c2, c3, c4, i, o0, o1);
        }
        return answer;
    }
    pair<int, int> answer = {0, 1};
    pair<int, int> m = get_rank_of_hand({m0, m1, c1, c2, c3, c4, c5});
    pair<int, int> o = get_rank_of_hand({o0, o1, c1, c2, c3, c4, c5});
    if (m >= o) {
        answer.first++;
    }
    return answer;
}

double PokerHandEval(int m0, int m1, int c1, int c2, int c3, int c4, int c5) {
    pair<int, int> answer = {0, 0};
    for (int o0 = 0; o0 < 52; o0++) {
        if (o0 == m0) continue;
        if (o0 == m1) continue;
        if (o0 == c1) continue;
        if (o0 == c2) continue;
        if (o0 == c3) continue;
        if (o0 == c4) continue;
        if (o0 == c5) continue;
        for (int o1 = o0 + 1; o1 < 52; o1++) {
            if (o1 == m0) continue;
            if (o1 == m1) continue;
            if (o1 == c1) continue;
            if (o1 == c2) continue;
            if (o1 == c3) continue;
            if (o1 == c4) continue;
            if (o1 == c5) continue;
            pair<int, int> not_lose_amount = CompareHandsDeterministic(m0, m1, c1, c2, c3, c4, c5, o0, o1);
            if (not_lose_amount.first * 2 > not_lose_amount.second) {
                answer.first += 1;
            } else if (not_lose_amount.first * 2 < not_lose_amount.second) {
                answer.second += 1;
            }
        }
    }
    double ans = answer.first * 1.0 / (answer.first + answer.second);
    return ans;
}

pair<int, int> CompareHandsDeterministicOnlyValue(int m0, int m1, int c1, int c2, int c3, int c4, int c5, int o0, int o1) {
    int cnt[13] = {0};
    cnt[m0]++; cnt[m1]++; cnt[c1]++; cnt[c2]++; cnt[c3]++; cnt[o0]++; cnt[o1]++;
    if (c4 >= 0) cnt[c4]++;
    if (c5 >= 0) cnt[c5]++;
    if (c4 == -1) {
        pair<int, int> answer = {0, 0};
        for (int i = 0; i < 13; i++) {
            if (cnt[i] == 4) continue;
            pair<int, int> ans = CompareHandsDeterministicOnlyValue(m0, m1, c1, c2, c3, i, c5, o0, o1);
            answer.first += ans.first * (4 - cnt[i]);
            answer.second += ans.second * (4 - cnt[i]);
        }
        return answer;
    } else if (c5 == -1) {
        pair<int, int> answer = {0, 0};
        for (int i = 0; i < 13; i++) {
            if (cnt[i] == 4) continue;
            pair<int, int> ans = CompareHandsDeterministicOnlyValue(m0, m1, c1, c2, c3, c4, i, o0, o1);
            answer.first += ans.first * (4 - cnt[i]);
            answer.second += ans.second * (4 - cnt[i]);
        }
        return answer;
    }
    pair<int, int> answer = {0, 1};
    pair<int, int> m = get_rank_of_hand_only_values({m0, m1, c1, c2, c3, c4, c5});
    pair<int, int> o = get_rank_of_hand_only_values({o0, o1, c1, c2, c3, c4, c5});
    if (m >= o) {
        answer.first++;
    }
    return answer;
}

double PokerHandEvalOnlyValue(int m0, int m1, int c1, int c2, int c3, int c4, int c5) {
    pair<int, int> answer = {0, 0};
    int cnt[13] = {0};
    cnt[m0]++; cnt[m1]++; cnt[c1]++; cnt[c2]++; cnt[c3]++;
    if (c4 >= 0) cnt[c4]++;
    if (c5 >= 0) cnt[c5]++;
    for (int o0 = 0; o0 < 13; o0++) {
        for (int o1 = o0; o1 < 13; o1++) {
            int c = 0;
            if (o0 == o1) c = (4 - cnt[o0]) * (3 - cnt[o0]) / 2;
            else c = (4 - cnt[o0]) * (4 - cnt[o1]);
            pair<int, int> not_lose_amount = CompareHandsDeterministicOnlyValue(m0, m1, c1, c2, c3, c4, c5, o0, o1);
            if (not_lose_amount.first * 2 > not_lose_amount.second) {
                answer.first += c;
            } else if (not_lose_amount.first * 2 < not_lose_amount.second) {
                answer.second += c;
            }
        }
    }
    double ans = answer.first * 1.0 / (answer.first + answer.second);
    return ans;
}

extern "C" {
    double My_PokerHandEval(int m0, int m1, int c1, int c2, int c3, int c4, int c5)
    {
        return PokerHandEval(m0, m1, c1, c2, c3, c4, c5);
    }
    double My_PokerHandEvalOnlyValue(int m0, int m1, int c1, int c2, int c3, int c4, int c5)
    {
        return PokerHandEvalOnlyValue(m0, m1, c1, c2, c3, c4, c5);
    }
}