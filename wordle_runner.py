#!/usr/bin/env python3
from termcolor import colored

from wordle_solver import Solver
from wordle_solver import Dictionary
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Use -d to test a dictionary')
parser.add_argument('-w', '--word', action="store", dest="word", help="Test one word")
parser.add_argument('-r', '--rank', action="store", dest="rank", help="Get word rank")
parser.add_argument('-s', '--score', action="store", dest="score", help="Get word score")
parser.add_argument('-d', '--dictionary', action="store", dest="dictionary", help="Run a dictionary file")
parser.add_argument('-di','--disable-intersecting', action="store_true", dest="disable_intersecting", help="Disable intersecting guesses")
args = parser.parse_args()
use_intersecting = not args.disable_intersecting
if args.rank:
    print(Dictionary().rank_of(args.rank))
elif args.score:
    print(Dictionary().score_of(args.score))
elif args.word:
    solution = Solver(args.word.strip().upper(), use_intersecting).solve('SLATE')
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
        solution = Solver(word, use_intersecting).solve(starting_word)
        guess_count += solution.guess_count
        if solution.guess_count > 6:
            hardest_words.append(word)
        if solution.guess_count > maximum:
            maximum = solution.guess_count
        avg = round(guess_count / count, 4)
        color = 'red'
        if solution.guess_count < 4:
            color = 'green'
        elif solution.guess_count < 5:
            color = 'yellow'
        output = str(avg).ljust(6) + " " + solution.word + "(" + str(solution.guess_count) + "): " + str(', '.join(solution.guesses))
        print(colored(output, color))

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

    # Write the results to a txt file
    filename = f'results-{starting_word}-{avg}'
    f = open(f'{filename}.txt', "w")
    for index, name in enumerate(names):
        f.write(f'{str(name)}: {words[index]}\n')
    f.close()

    # Draw a "histogram", actually just a bar chart in this case
    fig, ax = plt.subplots(1,1)
    plt.bar(range(len(sorted_scores)), values, tick_label=names, color=(96.0/255.0, 160.0/255.0, 94.0/255.0, 1.0))
    ax.set_xlabel('Guesses per answer')
    ax.set_ylabel('Words solved')

    # Get rid of the border and tick marks which look cheap
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
#ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
#    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])

    rects = ax.patches
    for rect, label in zip(rects, values):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height+0.01, label,
                ha='center', va='bottom')

    plt.savefig(f'{filename}.png')
