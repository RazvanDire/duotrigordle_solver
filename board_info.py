from wordlist import WORDS_TARGET
from typing import Dict, List, Tuple, Set
from heuristics.base import Heuristic


class BoardInfo:
    def __init__(self, heuristic: Heuristic) -> None:
        self.greens: Dict[int, str] = {}
        self.yellows: Set[Tuple[str, int]] = set()
        self.grays: Set[str] = set()
        self.won = False
        self.possible_guesses = WORDS_TARGET.copy()
        self.letter_ranking = heuristic.rank_letters(self.possible_guesses)

    def is_valid(self, word: str) -> bool:
        for index, letter in enumerate(word):
            if self.greens.get(index) != None and self.greens.get(index) != letter:
                return False

        for letter in word:
            if letter in self.grays:
                return False

        for letter, index in self.yellows:
            if letter not in word:
                return False
            if word[index] == letter:
                return False

        return True
