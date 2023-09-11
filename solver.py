from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeService
from selenium.webdriver.remote.webelement import WebElement
from wordlist import WORDS_TARGET
from typing import List, Dict, Tuple
from heuristics.base import Heuristic
from board_info import BoardInfo
import time

class Solver():
	GREEN = "bg-[#49d088]"
	YELLOW = "bg-[#eabf3e]"
	GRAY = "bg-[#73738c]"

	def __init__(self, url: str, heuristic: Heuristic) -> None:
		PATH = "./chromedriver"
		self.driver = webdriver.Chrome(service=ChromeService(executable_path=PATH))
		self.driver.get(url)
		self.body = self.driver.find_element(By.TAG_NAME, "body")
		self.boards = [BoardInfo(heuristic) for i in range(32)]
		self.web_boards = []
		self.heuristic = heuristic

	def __send_word__(self, word) -> None:
		self.body.send_keys(word, Keys.ENTER)

	def __update_board__(self, board: WebElement, board_index: int) -> None:
		print("Start")
		print(time.time() * 1000)
		last_guess = board.find_elements(By.CLASS_NAME, "word")[-2]
		print("First find",time.time() * 1000)
		letters = last_guess.find_elements(By.CLASS_NAME, "letter")
		print("2nd find", time.time() * 1000)

		for index, letter in enumerate(letters):
			classes = letter.get_dom_attribute("class")
			print(3, time.time() * 1000)
			if self.GREEN in classes:
				self.boards[board_index].greens[index] = letter.text
			if self.YELLOW in classes:
				self.boards[board_index].yellows.add((letter.text, index))

		print(4, time.time() * 1000)
		
		for index, letter in enumerate(letters):
			classes = letter.get_dom_attribute("class")
			print(5, time.time() * 1000)
			if self.GRAY in classes:
				if letter.text in [yellow[0] for yellow in self.boards[board_index].yellows]:
					self.boards[board_index].yellows.add((letter.text, index))
				elif letter.text in [green[1] for green in self.boards[board_index].greens.items()]:
					self.boards[board_index].yellows.add((letter.text, index))
				else:
					self.boards[board_index].grays.add(letter.text)
			
		print(6, time.time() * 1000)
			
	def __scan_boards__(self) -> None:
		for index, board in enumerate(self.web_boards):
			if "opacity-25" in board.get_attribute("class"):
				self.boards[index].won = True
			if not self.boards[index].won and len(self.boards[index].possible_guesses) > 1:
				self.__update_board__(board, index)
		

	def __choose_word__(self) -> str:
		guesses = [guess for guess in [self.heuristic.rank_words(board) for board in self.boards]]
		print(guesses)
		return max(guesses, key = lambda elem: elem[1])[0]

	def solve(self) -> None:
		self.web_boards = self.driver.find_elements(By.CLASS_NAME, "board")

		while True:
			guess = self.__choose_word__()
			print("Guess" + guess)
			self.__send_word__(guess)
			self.__scan_boards__()


