#!/usr/bin/env python3

from WordleSolver import Solver
from WordleSolver import Dictionary
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Use -d to test a dictionary')
parser.add_argument('-w', '--word', action="store", dest="word", help="Test one word")
parser.add_argument('-r', '--rank', action="store", dest="rank", help="Get word rank")
parser.add_argument('-s', '--score', action="store", dest="score", help="Get word score")
parser.add_argument('-d', '--dictionary', action="store", dest="dictionary", help="Run a dictionary file")
args = parser.parse_args()
if args.rank:
    print(Dictionary().rank_of(args.rank))
elif args.score:
    print(Dictionary().score_of(args.score))
elif args.word:
    solution = Solver(args.word.strip().upper()).solve("SLATE")
    print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses: ")
    print(', '.join(solution.guesses))
else:
    starting_word = "SLATE"
    dictionary = (args.dictionary if args.dictionary else "nyt-answers.txt")
    count = 0
    scores = dict()
    guess_count = 0
    maximum = 0
    hardest_words = list()
    avg = 0
    for word in Dictionary().answers:
        count += 1
        solution = Solver(word).solve(starting_word)
        guess_count += solution.guess_count
        if solution.guess_count > 6:
            hardest_words.append(word)
        if solution.guess_count > maximum:
            maximum = solution.guess_count
        avg = round(guess_count / count, 4)
        print(str(avg).ljust(6) + " " + solution.word + "(" + str(solution.guess_count) + "): " + str(', '.join(solution.guesses)))

        if solution.guess_count not in scores:
            scores[solution.guess_count] = {'count':1, 'words':[]}
            scores[solution.guess_count]['words'].append(solution.word)
        else:
            scores[solution.guess_count]['count'] += 1
            scores[solution.guess_count]['words'].append(solution.word)

    sorted_scores = dict(sorted(scores.items(), key = lambda x: x[0]))
    names = list(sorted_scores.keys())
    values = list(map(lambda x: x['count'], sorted_scores.values()))
    words = list(map(lambda x: ', '.join(x[1]['words']) if x[0] > 6 else str(len(x[1]['words'])), sorted_scores.items()))
    for index, name in enumerate(names):
        print(str(name) + ": " + words[index])
    print(f'Total Words: {count}, Total Guesses: {guess_count}')


    filename = f'results-{starting_word}-{avg}'
    f = open(f'{filename}.txt', "w")
    for index, name in enumerate(names):
        f.write(f'{str(name)}: {words[index]}\n')
    f.close()

    plt.barh(range(len(sorted_scores)), values, tick_label=names, color=(228.0/256.0, 88.0/256.0, 151.0/256.0, 1.0))
    plt.savefig(f'{filename}.png')
