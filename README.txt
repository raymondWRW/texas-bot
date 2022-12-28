format for cards
	one card
	(the number value 1- 13, the suit 0 - 3) <-- tuple
	multiple
	[(card), (card)] <--- list of tuple\




format for data (same as round_information)
data {
	'stage' : 0,                                                         <---- 0 = preflop 1 = flop 2 = turn 3 = river
    'player money' : [STARTING_PLAYER_MONEY for i in range(NUM_PLAYER)], <---- money each bot have
    'player bets' : [0 for i in range(NUM_PLAYER)],                      <---- the amount of money each play have put in
    'player playing' : [True for i in range(NUM_PLAYER)],                <---- number of player playing True = playing False = not playing
    'community card' : copy.copy(deck[0: 3])                             <---- the community card that is currently revealed (format is card)
}




format for card_array - this is for the reveal of the player's card that reaches the end
	[(player_index, card), (player_index, card)]



