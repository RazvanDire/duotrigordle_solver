from typing import List, Dict, Tuple
from .base import Heuristic
import math


class InformationTheory(Heuristic):
    def __init__(self):
        pass

    def __get_expected_info__(
        self, guess: str, pattern: List[int], word_list: List[str]
    ) -> float:
        possible_guesses = word_list.copy()

        for index, color in enumerate(pattern):
            if color == 0:
                possible_guesses = [
                    word for word in possible_guesses if word[index] == guess[index]
                ]

        for index, color in enumerate(pattern):
            if color == 1:
                possible_guesses = [
                    word
                    for word in possible_guesses
                    if word[index] != guess[index] and guess[index] in word
                ]

        for index, color in enumerate(pattern):
            if color == 2:
                possible_guesses = [
                    word for word in possible_guesses if guess[index] not in word
                ]

        p = len(possible_guesses) / len(word_list)

        if p == 0:
            return 0
        else:
            return p * math.log(1 / p, 2)

    def rank_words(self, possible_guesses: List[str]) -> Tuple[str, float]:
        """
        Computes score for every possible guess, based on the information
        available on the board.

        Returns the guess with the highest score and the score.
        """
        best_guess = ""
        max_info = -1

        for guess in possible_guesses:
            expected_info = 0

            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        for l in range(3):
                            for m in range(3):
                                expected_info += self.__get_expected_info__(
                                    guess, [i, j, k, l, m], possible_guesses
                                )

            if expected_info > max_info:
                max_info = expected_info
                best_guess = guess

        #print(best_guess, max_info)
        return (best_guess, max_info)
