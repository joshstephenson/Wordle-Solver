# Python Wordle Solver

## What is Wordle?
This is a Python script to solve the [NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html) in least possible guesses. Wordle is a 5-letter word guessing game where the player must guess a word in six guesses. For each guess, the player enters a 5-letter word and receives feedback. Feedback includes:
- letters in the word but not in correct position (yellow)
- letters in the word and in the correct position (green)
- letters not in the word at all (gray)

## Usage
The current version can be used in 2 different ways:
First, by running the script directly it will parse a list of recent Wordle words and solve them, printing out the words it used to guess and total number of guesses

```
solved: CRUST in 3 guesses: ['AROSE', 'CUBIT', 'CRUST']
solved: STOOL in 7 guesses: ['AROSE', 'CLIPT', 'BUGGY', 'SMOLT', 'SLOTH', 'SLOTS', 'STOOL']
solved: COLON in 4 guesses: ['AROSE', 'INDOL', 'GUTTY', 'COLON']
solved: ABASE in 4 guesses: ['AROSE', 'MINTY', 'ABUSE', 'ABASE']
solved: MARRY in 5 guesses: ['AROSE', 'DICTY', 'GLARY', 'AMBRY', 'MARRY']
solved: REACT in 5 guesses: ['AROSE', 'DICTY', 'PLUNK', 'CARET', 'REACT']
solved: BATTY in 6 guesses: ['AROSE', 'PLANT', 'CHIMB', 'FUZZY', 'BAWTY', 'BATTY']
solved: PRIDE in 3 guesses: ['AROSE', 'CUPID', 'PRIDE']
solved: FLOSS in 3 guesses: ['AROSE', 'LIGHT', 'FLOSS']
solved: HELIX in 5 guesses: ['AROSE', 'LINED', 'THUMB', 'CHIEL', 'HELIX']
solved: CROAK in 3 guesses: ['AROSE', 'THINK', 'CROAK']
solved: STAFF in 5 guesses: ['AROSE', 'SLANT', 'CHIMP', 'FUGGY', 'STAFF']
solved: PAPER in 7 guesses: ['AROSE', 'DICTY', 'ARGLE', 'AMBER', 'PAWER', 'PAVER', 'PAPER']
solved: UNFED in 6 guesses: ['AROSE', 'LINED', 'THUMP', 'NUKED', 'UNWED', 'UNFED']
solved: WHELP in 6 guesses: ['AROSE', 'LINED', 'BLUEY', 'LETCH', 'WHELK', 'WHELP']
solved: TRAWL in 3 guesses: ['AROSE', 'GLINT', 'TRAWL']
...
```

Second, by loading the Solver class into the python shell or another python script, the user can play world receiving advice on which word to guess next. After each guess the user must provide the feedback from the Wordle game (green, yellow and gray letters).

```
from WordleSolver import Solver
 
 solver = Solver()
 solver.guess("irate")
 solver.miss("irae")
 solver.hit("t", 4)
 solver.guess("clots")
 solver.hit("o")
 solver.miss("cls")
 solver.guess("punto")
 solver.hit("o", 5)
 solver.miss("pun")
```

Output from July 27th Wordle would be:
```
joshuastephenson@~/Projects/Wordle-Solver$ ./wordle-sample.py 
YOUR NEXT GUESS SHOULD BE: PUNTO
```

## The Algorithm
The algorithm has two distinct word lists:
1. First it attempts to make exclusive guesses. These are guesses that don't use any of the letters used in previous guesses. As each guess is made (and the algorithm receives or generates feedback on the hits/misses from that guess) the possible exclusive guesses are trimmed.
2. As soon as there are fewer inclusive guesses than exclusive guesses to be made (takes roughly 3 guesses) the algorithm switches to using inclusive guesses. A list of exclusive words is continually pruned to only include those with letters that have been matched so far.

As the inclusive word list is updated, the frequency of letters is continually updated and then both word lists are resorted based on the composition of the new letter frequency. This ensures that each guess cuts the word list down maximally.

The potential words that populate both of these lists initially is built from a list of 5 letter words passed in from either  `/usr/share/dict/words` on OSX systems or `wordle-dictionary.txt` included in this repository ([originally found here](https://github.com/redbo/scrabble/blob/master/dictionary.txt)). The words will be sorted in decreasing order by the frequency of their letters in the English language. That frequency is "EARIOTNSLCUDPMHGBFYWKVXZJQ" [found here](https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html) and then given a score. Duplicate letters are intrinsically detrimental to the score of guesses. This ensures that whenever we have multiple options we pick the one with the highest likelihood of being the target word.

## Performance
![WordleSolverResults](https://user-images.githubusercontent.com/11002/181620483-e959c8c4-8916-4e9e-bbe5-46bfe5462a85.png)

Out of 926 previous Wordle puzzles (included in "wordle-answers.txt" file), this algorithm solved 93.6% in 6 guesses or fewer with 80% in 3-5 guesses.
|Guesses|%|Count|Words|
|----|-------------------|---------|-----|
| 2  | 0.6%  | 6   | ISLET, PLANT, UNLIT, ARISE, ARSON, PROSE |
| 3  | 14.9% | 138 | |
| 4  | 39%   | 360 | |
| 5  | 26.5% | 245 | |
| 6  | 13%   | 118 | |
| 7  | 4.1%  | 38  | |
| 8  | 1.8%  | 17  | BOOBY, OFFAL, SURER, SHAME, COYLY, TAUNT, PARER, STEIN, SAFER, EAGLE, RESET, QUELL, REHAB, ROVER, JOLLY, JOKER, BOSOM |
| 9  | 0.3%  | 3   | ESSAY, USURP, VISTA |
| 10 | 0.1%  | 1   | USHER |
