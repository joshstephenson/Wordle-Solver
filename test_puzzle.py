import pytest
from puzzle import Puzzle
from puzzle import Word

LETTER_COUNT = 26
LETTER_A = 65
EXPECTED_MISSES = [['X'],[],[],['Q'],['J','Q','V']]

def test_allows_returns_true_for_a_z_by_default():
    puzzle = Puzzle()
    for j in range(0,LETTER_COUNT):
        letter = chr(j+LETTER_A)
        for i in range(0,5):
            if letter not in EXPECTED_MISSES[i]:
                assert puzzle.allows(i, letter)
    for index, pos in enumerate(EXPECTED_MISSES):
        for letter in pos:
            assert not puzzle.allows(index, letter)

def test_adding_green_turns_off_all_other_letters_in_pos():
    puzzle = Puzzle()
    target = 'D'
    puzzle.set_green(0, target)
    assert puzzle.allows(0, target)
    for j in range(0,LETTER_COUNT):
        letter = chr(j+LETTER_A)
        if letter is not target:
            assert not puzzle.allows(0, letter)

def test_adding_yellow_turns_off_only_that_letter_in_that_position():
    puzzle = Puzzle()
    target = 'A'
    assert puzzle.allows(0, target)
    assert puzzle.allows(1, target)
    assert puzzle.allows(2, target)
    assert puzzle.allows(3, target)
    assert puzzle.allows(4, target)
    puzzle.set_yellow(0, target)
    assert not puzzle.allows(0, target)
    assert puzzle.allows(1, target)
    assert puzzle.allows(2, target)
    assert puzzle.allows(3, target)
    assert puzzle.allows(4, target)
    for j in range(0,LETTER_COUNT):
        letter = chr(j+LETTER_A)
        if letter is not target and letter not in EXPECTED_MISSES[0]:
            assert puzzle.allows(0, letter)

def test_adding_gray_turns_off_in_all_positions():
    puzzle = Puzzle()
    target = 'T'
    assert puzzle.allows(0, target)
    assert puzzle.allows(1, target)
    assert puzzle.allows(2, target)
    assert puzzle.allows(3, target)
    assert puzzle.allows(4, target)
    puzzle.set_gray(target)
    assert not puzzle.allows(0, target)
    assert not puzzle.allows(1, target)
    assert not puzzle.allows(2, target)
    assert not puzzle.allows(3, target)
    assert not puzzle.allows(4, target)

def test_word():
    word = Word('REBAR')
    print([bin(x) for x in word.positions])

