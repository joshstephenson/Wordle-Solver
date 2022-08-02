#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver

solver = Solver()
word = input('What is your first word guess? May I recommend OATER? ')
is_solved = False
while not is_solved:
    word = word.strip().upper()
    print(f'You entered: {word}')
    green = input('Please enter green letters in a string like \'__A__\' (or ENTER for none) ')
    while len(green) != 0 and len(green) != 5:
        green = input("Please exactly five characters using '_' for non-green letters. Example: __A__: ")

    if green.upper() == word:
        is_solved = True
        solver.guess(word, word, None)
        break
    if len(green) == 0:
        green = None
    yellow = input('Please enter yellow letters (or ENTER for none) ')
    if len(yellow) == 0:
        yellow = None
    solver.guess(word, green, yellow)
    print("Your next guess should be: " + solver.next_guess())
    word = input('What is your next guess? ')
    is_solved = solver.is_solved()

if is_solved:
    print(f'We won in {len(solver.guesses())} guesses!')
