#!/usr/bin/env python3
from wordle_solver import Solver
from wordle_solver import Dictionary
import pandas as pd
import numpy as np

def sort_results(results):
    return dict(sorted(results.items(), key = lambda item: item[1]['avg']))

def print_best(results):
    results = sort_results(results)
    words = list(results.keys())
    avgs = list(results.values())
    print(f'THE BEST STARTING WORD IS {words[0]}: {avgs[0]}')

dictionary = Dictionary()

words = []
avg = []
best = []
best_word = []
worst = []
worst_word = []
total_answer_count = len(dictionary.answers)
for index, starting_word in enumerate(dictionary.guesses):
    after_guess_count = 0
    starting_count = 0
    words.append(starting_word)

    this_avg = 0
    this_best = total_answer_count
    this_best_word = None
    this_worst = 0
    this_worst_word = None
    for answer in dictionary.answers:
        if starting_word == answer:
            continue
        # Guess the word
        solver = Solver(answer)
        solver.puzzle.add_guess(starting_word)
        solver._process_guess(starting_word)
        _ = solver.puzzle.next_guess()

        starting_count += total_answer_count # should be 2315
        after_guess_count += solver.answer_count()
        partition_amount = solver.answer_count() / total_answer_count

        this_avg = after_guess_count / starting_count

        if partition_amount < this_best:
            this_best = partition_amount
            this_best_word = answer
        if partition_amount > this_worst:
            this_worst = partition_amount
            this_worst_word = answer

#        print(f'{starting_word},{answer},{solver.answer_count()},{solver.answer_count() / total_answer_count}')

    avg.append(this_avg)
    best.append(this_best)
    best_word.append(this_best_word)
    worst.append(this_worst)
    worst_word.append(this_worst_word)
    print(f'{starting_word},{this_avg},{this_best},{this_best_word},{this_worst},{this_worst_word}')


