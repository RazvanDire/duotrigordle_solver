from typing import List, Dict, Tuple
from .base import Heuristic


class ScaledEntropy(Heuristic):
    def __init__(self):
        pass

    def rank_letters(self, word_list: List[str]) -> List[Dict[str, float]]:
        """
        Computes score of every letter on each of the five possible positions in
        the word.

        Returns a list of five dictionaries, each containing a map between a
        letter and its score.
        """
        rankings = [{} for i in range(5)]
        overall = {}

        for word in word_list:
            for letter in word:
                overall[letter] = overall.get(letter, 0) + 1

        for word in word_list:
            for index, letter in enumerate(word):
                rankings[index][letter] = rankings[index].get(letter, 0) + overall.get(
                    letter
                )

        return rankings

    def rank_words(
        self, possible_guesses: List[str], letter_ranking: List[Dict[str, float]]
    ) -> Tuple[str, float]:
        """
        Computes score for every possible guess, based on the information
        available on the board.

        Returns the guess with the highest score and the score.
        """
        if len(possible_guesses) == 1:
            return (possible_guesses[0], 12000)

        FACTOR = 1 / 3
        best_guess = ""
        max_score = -1
        for guess in possible_guesses:
            parsed = ""
            score = 0
            for index, letter in enumerate(guess):
                if letter in parsed:
                    score += letter_ranking[index].get(letter) * FACTOR
                else:
                    score += letter_ranking[index].get(letter)
                    parsed += letter

            if score > max_score:
                max_score = score
                best_guess = guess

        return (best_guess, max_score)
