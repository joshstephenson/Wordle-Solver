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
<<<<<<< Updated upstream
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
=======
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
                scores[solution.guess_count] = {'count':1, 'words':[]}
                scores[solution.guess_count]['words'].append(solution.word)
            else:
                scores[solution.guess_count]['count'] += 1
                scores[solution.guess_count]['words'].append(solution.word)
>>>>>>> Stashed changes

    sorted_scores = dict(sorted(scores.items(), key = lambda x: x[0]))
    names = list(sorted_scores.keys())
    values = list(map(lambda x: x['count'], sorted_scores.values()))
    words = list(map(lambda x: x['words'] if len(x['words']) < 20 else len(x['words']), sorted_scores.values()))
    for index, name in enumerate(names):
        print(str(name) + ": " + str(words[index]))

    plt.barh(range(len(sorted_scores)), values, tick_label=names)
    plt.show()

