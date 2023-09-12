
from typing import List, Dict, Tuple


class Heuristic():
	def __init__(self):
		pass

	def rank_letters(self, word_list: List[str]) -> List[Dict[str, int]]:
		"""
		Computes score of every letter on each of the five possible positions in
		the word.

		Returns a list of five dictionaries, each containing a map between a
		letter and its score.
    	""" 
		pass

	def rank_words(
        self, possible_guesses: List[str], letter_ranking: List[Dict[str, int]]
    ) -> Tuple[str, int]:
		"""
		Computes score for every possible guess, based on the information
		available on the board.

		Returns the guess with the highest score and the score.
		"""
		pass
