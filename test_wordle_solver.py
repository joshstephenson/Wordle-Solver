import pytest
from wordle_solver import Solver
from wordle_solver import Dictionary

# riper was a problem
def test_riper():
    solver = Solver('RIPER')
    solution = solver.solve('SALET')
    assert solution.guess_count <= 6

def test_all():
    starting_word = "SLATE"
    dictionary = "nyt-answers.txt"
    count = 0
    scores = dict()
    guess_count = 0
    hardest_words = list()
    for word in Dictionary().answers:
        count += 1
        solution = Solver(word).solve(starting_word)
        guess_count += solution.guess_count
        assert solution.guess_count <= 6

    assert round(guess_count / count, 4) < 3.68
