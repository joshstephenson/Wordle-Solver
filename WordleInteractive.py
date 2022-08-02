#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
from WordleSolver import Solver

WORD_LENGTH = 5
def has_duplicate_letters(word):
    letters = set([letter for letter in word])
    return len(letters) < WORD_LENGTH

solver = Solver()
word = input('What is your first word guess? May I recommend OATER?\n> ')
is_solved = False
while not is_solved:
    word = word.strip().upper()
    print(f'You entered: {word}')
    green = ""
    if has_duplicate_letters(word):
        green = input('Please enter green letters in a string like \'__A__\' (or ENTER for none)\n> ')
        while len(green) != 0 and len(green) != WORD_LENGTH:
            green = input("Please exactly five characters using '_' for non-green letters. Example: __A__\n> ")
    else:
        green = input('Please enter green letters (or ENTER for none)\n> ')
        green_string = ""
        for index, letter in enumerate(green.upper()):
            green_string += letter if word[index] == letter else "_"

    if green.upper() == word:
        is_solved = True
        solver.guess(word, word, None)
        break
    if len(green) == 0:
        green = None
    yellow = input('Please enter yellow letters (or ENTER for none)\n> ')
    if len(yellow) == 0:
        yellow = None
    solver.guess(word, green, yellow)
    print("Your next guess should be: " + solver.next_guess())
    word = input('What is your next guess?\n> ')
    is_solved = solver.is_solved()

if is_solved:
    print(f'You won 😉 in {len(solver.guesses())} guesses!')
