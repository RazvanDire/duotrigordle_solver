import asyncio
from playwright.async_api import async_playwright, Playwright, Locator, Page
from wordlist import WORDS_TARGET
from typing import List, Dict, Tuple
from heuristics.base import Heuristic
from board_info import BoardInfo
import time


class Solver:
    GREEN = "bg-[#49d088]"
    YELLOW = "bg-[#eabf3e]"
    GRAY = "bg-[#73738c]"

    def __init__(self, url: str, driver: Playwright, heuristic: Heuristic) -> None:
        self.url = url
        self.driver = driver
        self.boards = [BoardInfo(heuristic) for i in range(32)]
        self.web_boards = []
        self.heuristic = heuristic
        self.guess_count = 0

    async def __send_word__(self, word: str, page: Page) -> None:
        await page.keyboard.type(word)
        await page.keyboard.press("Enter")
        self.guess_count += 1

    async def __update_board__(
        self, letter_class_attributes, letter_text, board_index: int
    ) -> None:
        for index in range(5):
            text = letter_text[index]
            classes = letter_class_attributes[index]

            if self.GREEN in classes:
                self.boards[board_index].greens[index] = text
            if self.YELLOW in classes:
                self.boards[board_index].yellows.add((text, index))

        for index in range(5):
            text = letter_text[index]
            classes = letter_class_attributes[index]

            if self.GRAY in classes:
                if text in [yellow[0] for yellow in self.boards[board_index].yellows]:
                    self.boards[board_index].yellows.add((text, index))
                elif text in [
                    green[1] for green in self.boards[board_index].greens.items()
                ]:
                    self.boards[board_index].yellows.add((text, index))
                else:
                    self.boards[board_index].grays.add(text)

        for board_info in self.boards:
            board_info.possible_guesses = [
                word
                for word in board_info.possible_guesses
                if board_info.is_valid(word)
            ]
            board_info.letter_ranking = self.heuristic.rank_letters(
                board_info.possible_guesses
            )

    async def __scan_boards__(self) -> None:
        pop_list = [
            index
            for index in range(len(self.boards))
            if "opacity-25" in await self.web_boards[index].get_attribute("class")
        ]

        for i in pop_list:
            self.boards.pop(i)
            self.web_boards.pop(i)

        board_count = len(self.boards)

        last_guesses = await asyncio.gather(
            *[board.locator(".word").all() for board in self.web_boards]
        )
        last_guesses = [guess[-2] for guess in last_guesses]

        letters = await asyncio.gather(
            *[Locator(guess).locator(".letter").all() for guess in last_guesses]
        )

        letters_info = await asyncio.gather(
            *[Locator(letter[0]).get_attribute("class") for letter in letters],
            *[Locator(letter[1]).get_attribute("class") for letter in letters],
            *[Locator(letter[2]).get_attribute("class") for letter in letters],
            *[Locator(letter[3]).get_attribute("class") for letter in letters],
            *[Locator(letter[4]).get_attribute("class") for letter in letters],
            *[Locator(letter[0]).all_inner_texts() for letter in letters],
            *[Locator(letter[1]).all_inner_texts() for letter in letters],
            *[Locator(letter[2]).all_inner_texts() for letter in letters],
            *[Locator(letter[3]).all_inner_texts() for letter in letters],
            *[Locator(letter[4]).all_inner_texts() for letter in letters]
        )

        letters_class_attributes = [
            [letters_info[i + j * board_count] for j in range(5)]
            for i in range(board_count)
        ]
        letters_text = [
            [letters_info[i + (j + 5) * board_count][0] for j in range(5)]
            for i in range(board_count)
        ]

        for index in range(board_count):
            if len(self.boards[index].possible_guesses) > 1:
                await self.__update_board__(
                    letters_class_attributes[index], letters_text[index], index
                )

    def __choose_word__(self) -> str:
        guesses = [
            guess
            for guess in [
                self.heuristic.rank_words(board.possible_guesses, board.letter_ranking)
                for board in self.boards
            ]
        ]
        return max(guesses, key=lambda elem: elem[1])[0]

    async def solve(self) -> None:
        browser = await self.driver.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(self.url)
        self.web_boards = await page.locator(".board").all()

        while len(await page.locator(".mantine-Overlay-root").all()) == 0:
            guess = self.__choose_word__()
            await self.__send_word__(guess, page)
            await self.__scan_boards__()