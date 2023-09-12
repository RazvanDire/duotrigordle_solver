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

    async def __send_word__(self, word: str, page: Page) -> None:
        await page.keyboard.type(word)
        await page.keyboard.press("Enter")

    async def __update_board__(self, board: Locator, board_index: int) -> None:
        print("Start" , time.time() * 1000)
        last_guess = await board.locator(".word").all()
        last_guess = last_guess[-2]

        print("First find", time.time() * 1000)
        letters = await last_guess.locator(".letter").all()
        print("2nd find", time.time() * 1000)

        for index, letter in enumerate(letters):
            classes = await letter.get_attribute("class")
            text = await letter.all_inner_texts()
            text = text[0]
            print(3, time.time() * 1000)
            if self.GREEN in classes:
                self.boards[board_index].greens[index] = text
            if self.YELLOW in classes:
                self.boards[board_index].yellows.add((text, index))

        print(4, time.time() * 1000)

        for index, letter in enumerate(letters):
            classes = await letter.get_attribute("class")
            print(5, time.time() * 1000)

            if self.GRAY in classes:
                text = await letter.all_inner_texts()
                text = text[0]

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

        print(6, time.time() * 1000)

    async def __scan_boards__(self) -> None:
        for index, board in enumerate(self.web_boards):
            if "opacity-25" in await board.get_attribute("class"):
                self.boards[index].won = True
            if (
                not self.boards[index].won
                and len(self.boards[index].possible_guesses) > 1
            ):
                await self.__update_board__(board, index)

    def __choose_word__(self) -> str:
        guesses = [
            guess
            for guess in [
                self.heuristic.rank_words(board.possible_guesses, board.letter_ranking)
                for board in self.boards
                if not board.won
            ]
        ]
        return max(guesses, key=lambda elem: elem[1])[0]

    async def solve(self) -> None:
        browser = await self.driver.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(self.url)
        self.web_boards = await page.locator(".board").all()

        while len(await page.locator(".mantine-Overlay-root").all()) == 0:
            print(8, time.time() * 1000)
            guess = self.__choose_word__()
            await self.__send_word__(guess, page)
            await self.__scan_boards__()
            print(7, time.time() * 1000)
