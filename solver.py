import asyncio
from playwright.async_api import Playwright, Locator, Page
from typing import List, Tuple
from heuristics.base import Heuristic
from board_info import BoardInfo


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

    async def __get_letters_info__(self, board_count) -> List[List[Locator]]:
        last_guesses = await asyncio.gather(
            *[board.locator(".word").all() for board in self.web_boards]
        )
        last_guesses = [guess[-2] for guess in last_guesses]

        letters = await asyncio.gather(
            *[Locator(guess).locator(".letter").all() for guess in last_guesses]
        )

        return letters

    async def __update_board__(self, letters: List[Locator], board_index: int) -> None:
        letters_info = await asyncio.gather(
            *[letter.all_inner_texts() for letter in letters],
            *[letter.get_attribute("class") for letter in letters]
        )

        letter_text = letters_info[:5]
        letter_class_attributes = letters_info[5:]

        for index in range(5):
            text = letter_text[index][0]
            classes = letter_class_attributes[index]

            if self.GREEN in classes:
                self.boards[board_index].greens[index] = text
            if self.YELLOW in classes:
                self.boards[board_index].yellows.add((text, index))

        for index in range(5):
            text = letter_text[index][0]
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

    async def __scan_boards__(self, page: Page) -> None:
        one_word_list = []
        pop_list = []

        for index in range(len(self.boards)):
            if "opacity-25" in await self.web_boards[index].get_attribute("class"):
                pop_list.append(index)
            elif len(self.boards[index].possible_guesses) == 1:
                pop_list.append(index)
                one_word_list.append(self.boards[index].possible_guesses[0])

        pop_list.reverse()
        for i in pop_list:
            self.boards.pop(i)
            self.web_boards.pop(i)

        board_count = len(self.boards)
        letters = await self.__get_letters_info__(board_count)

        for index in range(board_count):
            await self.__update_board__(
                letters[index], index
            )

        for guess in one_word_list:
            await self.__send_word__(guess, page)

            letters = await self.__get_letters_info__(board_count)
            for index in range(board_count):
                await self.__update_board__(
                    letters[index], index
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
            await self.__scan_boards__(page)
