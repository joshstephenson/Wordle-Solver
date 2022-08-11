#!/usr/bin/env python3
from wordle_solver import Solver
from wordle_solver import Dictionary

def sort_results(results):
    return dict(sorted(results.items(), key = lambda item: item[1]['avg']))

def print_best(results):
    results = sort_results(results)
    words = list(results.keys())
    avgs = list(results.values())
    print(f'THE BEST STARTING WORD IS {words[0]}: {avgs[0]}')

dictionary = Dictionary()

results = dict()
for starting_word in dictionary.answers:
    avg = 0
    count = 0
    score = 0
    results[starting_word] = dict()
    for answer in dictionary.answers:
        solution = Solver(answer).solve(starting_word)
        count += 1
        score += solution.guess_count
        result = results[starting_word]
        if solution.guess_count not in result.keys():
            result[solution.guess_count] = 0
        result[solution.guess_count] += 1

    avg = score / count
    print(f'{starting_word} avg: {avg}')
    results[starting_word]['avg'] = avg
    print_best(results)

print(results)

print_best(results)
