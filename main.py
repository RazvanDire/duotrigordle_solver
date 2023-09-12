import time
from solver import Solver
from heuristics.letter_entropy import LetterEntropy
import asyncio
from playwright.async_api import async_playwright

async def main():
	async with async_playwright() as p:
		solver = Solver("https://duotrigordle-kappa.vercel.app/", p, LetterEntropy())
		await solver.solve()
		time.sleep(10)

if __name__ == "__main__":
	asyncio.run(main())	