#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver
import matplotlib.pyplot as plt

test_one = False

if test_one:
    solution = Solver("EAGLE").solve()
    print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses: ")
    print(solution.guesses)
else:
    count = 0
    scores = dict()
    answers = dict()
    with open("wordle-answers.txt", 'r') as words:
        for word in words:
            count += 1
            try:
                solution = Solver(word.strip()).solve()
            except TypeError:
                print("Exception occurred here")
            else:
                print("solved: " + solution.word + " in " + str(solution.guess_count) + " guesses: " + str(solution.guesses))
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

