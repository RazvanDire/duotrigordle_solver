from typing import Tuple, List, Dict
from .base import Heuristic

import sys
sys.path.append('..')
from board_info import BoardInfo

class LetterEntropy(Heuristic):
	def __init__(self):
		pass

	def rank_letters(self, word_list: List[str]) -> List[Dict[str, int]]:
		"""
		Computes score of every letter on each of the five possible positions in
		the word.

		Returns a list of five dictionaries, each containing a map between a
		letter and its score.
    	""" 
		rankings = [{} for i in range(5)]

		for word in word_list:
			for index, letter in enumerate(word):
				rankings[index][letter] = rankings[index].get(letter, 0) + 1

		return rankings

	def rank_words(self, board_info: BoardInfo) -> Tuple[str, int]:
		"""
		Computes score for every possible guess, based on the information
		available on the board.

		Returns the guess with the highest score and the score.
		"""

		if board_info.won:
			return ("", -1)

		board_info.possible_guesses = [word for word in board_info.possible_guesses if board_info.is_valid(word)]
		board_info.letter_ranking = self.rank_letters(board_info.possible_guesses)

		if len(board_info.possible_guesses) == 1:
			return (board_info.possible_guesses[0], 12000)

		FACTOR = 1
		best_guess = ""
		max_score = -1
		for guess in board_info.possible_guesses:
			score = 0
			for (index, letter) in enumerate(guess):  
				score += board_info.letter_ranking[index].get(letter) * FACTOR

			if score > max_score:
				max_score = score
				best_guess = guess

		return (best_guess, max_score)