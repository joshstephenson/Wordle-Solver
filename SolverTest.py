#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Use --all to test all wordle answers')
parser.add_argument('-w', '--word', action="store", dest="word", help="Test one word")
args = parser.parse_args()
if args.word:
    solution = Solver(args.word.upper()).solve()
    print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses: ")
    print(solution.guesses)

else:
    count = 0
    scores = dict()
    answers = dict()
    score = 0
    maximum = 0
    with open("nyt-answers.txt", 'r') as words:
        for word in words:
            count += 1
#            try:
            solution = Solver(word.strip()).solve()
#            except BaseException:
#                print("Exception occurred here")
#            else:
            score += solution.guess_count
            if solution.guess_count > maximum:
                maximum = solution.guess_count
            avg = round(score / count, 4)
            print(str(avg).ljust(6) + " " + solution.word + " " + str(solution.guess_count) + ": " + str(solution.guesses))
            if solution.guess_count not in scores:
                scores[solution.guess_count] = 1
                answers[solution.guess_count] = [solution.word]
            else:
                scores[solution.guess_count] += 1
                answers[solution.guess_count].append(solution.word)

    print(answers)
    print(scores)

    sorted_scores = dict(sorted(scores.items(), key = lambda x: x[0]))
    names = list(sorted_scores.keys())
    values = list(sorted_scores.values())

    plt.bar(range(len(sorted_scores)), values, tick_label=names)
    plt.show()

