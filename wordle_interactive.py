#!/usr/bin/env python3
from wordle_solver import Solver
import argparse

parser = argparse.ArgumentParser(description='Use -s to get suggestions')
parser.add_argument('-s', '--suggest', action="store_true", dest="suggest", help="Get suggestions")
should_suggest = parser.parse_args().suggest

def suggest(guess):
    if should_suggest:
        print(f'Your next guess should be: {guess}')

WORD_LENGTH = 5
def has_duplicate_letters(word):
    letters = set([letter for letter in word])
    return len(letters) < WORD_LENGTH

def get_green():
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
    return green.upper()

solver = Solver()
word = input('What is your first word guess? (press ENTER for SLATE) \n> ')
if len(word) < 5:
    word = "SLATE"
is_solved = False
while not is_solved:
    word = word.strip().upper()
    print(f'You entered: {word}')
    green = get_green()

    if green == word:
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

    print(f'{solver.answer_count()} possible answers')
    suggest(guess)
    hint = f' (press Enter for {guess}' if should_suggest else ''
    word = input(f'What is your next guess?{hint}\n> ')
    if len(word) < 5:
        word = guess
    is_solved = solver.is_solved()

print(f'You won in {len(solver.guesses())} guesses! 🎉')
