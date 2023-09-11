import time
from solver import Solver
from heuristics.letter_entropy import LetterEntropy

if __name__ == "__main__":
	solver = Solver("http://localhost:3000/", LetterEntropy())
	solver.solve()
	time.sleep(10)