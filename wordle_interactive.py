#!/usr/bin/env python3
from wordle_solver import Solver

WORD_LENGTH = 5
def has_duplicate_letters(word):
    letters = set([letter for letter in word])
    return len(letters) < WORD_LENGTH

solver = Solver()
word = input('What is your first word guess? (press ENTER for EARST) \n> ')
if len(word) < 5:
    word = "EARST"
is_solved = False
while not is_solved:
    word = word.strip().upper()
    print(f'You entered: {word}')
    green = ""
    if has_duplicate_letters(word):
        green = input('Please enter green letters in a string like \'__A__\' (press ENTER for none)\n> ')
        while len(green) != 0 and len(green) != WORD_LENGTH:
            green = input("Please exactly five characters using '_' for non-green letters. Example: __A__\n> ")
    else:
        green = input('Please enter green letters (press ENTER for none)\n> ')
        green_string = ""
        green_letters = [letter for letter in green.upper()]
        for index, letter in enumerate(word):
            green_string += letter if letter in green_letters else "_"
        green = green_string

    if green.upper() == word:
        is_solved = True
        solver.guess(word, word, None)
        break
    if len(green) == 0:
        green = None
    yellow = input('Please enter yellow letters (press ENTER for none)\n> ')
    if len(yellow) == 0:
        yellow = None
    solver.guess(word, green, yellow)
    guess = solver.next_guess()
    print(f'Your next guess should be: {guess}')
    word = input(f'What is your next guess? (press ENTER for {guess})\n> ')
    if len(word) < 5:
        word = guess
    is_solved = solver.is_solved()

if is_solved:
    print(f'You won 😉 in {len(solver.guesses())} guesses!')