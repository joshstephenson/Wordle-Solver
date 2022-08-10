import pytest
from wordle_solver import Solver
from wordle_solver import Dictionary

# riper was a problem
def test_riper():
    solver = Solver('RIPER')
    solution = solver.solve('EARST')
    assert solution.guess_count <= 6

def test_all():
    starting_word = "EARST"
    dictionary = "nyt-answers.txt"
    count = 0
    scores = dict()
    guess_count = 0
    maximum = 0
    hardest_words = list()
    avg = 0
    for word in Dictionary().answers:
        count += 1
        solution = Solver(word).solve(starting_word)
        assert solution.guess_count <= 6
