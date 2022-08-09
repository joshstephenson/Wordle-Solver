#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver
from WordleSolver import Dictionary

def sort_results(results):
    return dict(sorted(results.items(), key = lambda item: item[1]))

def print_best(results):
    results = sort_results(results)
    words = list(results.keys())
    avgs = list(results.values())
    print(f'THE BEST STARTING WORD IS {words[0]}: {avgs[0]}')

dictionary = Dictionary()

results = dict()
for starting_word in dictionary.all_words:
    avg = 0
    count = 0
    score = 0
    for answer in dictionary.answers:
        solution = Solver(answer).solve(starting_word)
        count += 1
        score += solution.guess_count

    avg = score / count
    print(f'{starting_word} avg: {avg}')
    results[starting_word] = avg
    print_best(results)

print(results)

print_best(results)