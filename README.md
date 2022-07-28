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
solved: CIGAR in 4 guesses: ['AROSE', 'DICTY', 'JUGUM', 'CIGAR']
solved: REBUT in 6 guesses: ['AROSE', 'TUMID', 'LYNCH', 'BRUTE', 'BURET', 'REBUT']
solved: SISSY in 6 guesses: ['AROSE', 'WHITY', 'PLUMB', 'CISSY', 'KISSY', 'SISSY']
solved: HUMPH in 5 guesses: ['AROSE', 'UNLIT', 'PYGMY', 'BUMPH', 'HUMPH']
solved: AWAKE in 4 guesses: ['AROSE', 'GLINT', 'MUCKY', 'AWAKE']
solved: BLUSH in 4 guesses: ['AROSE', 'WHITY', 'PLUMB', 'BLUSH']
solved: FOCAL in 4 guesses: ['AROSE', 'GLINT', 'DUCHY', 'FOCAL']
solved: EVADE in 6 guesses: ['AROSE', 'BLIND', 'CHUMP', 'FADGE', 'DEAVE', 'EVADE']
solved: NAVAL in 6 guesses: ['AROSE', 'LINTY', 'CHUCK', 'BLAND', 'ALANG', 'NAVAL']
solved: SERVE in 5 guesses: ['AROSE', 'INPUT', 'GHYLL', 'SCREE', 'SERVE']
solved: HEATH in 5 guesses: ['AROSE', 'LINTY', 'CHUMP', 'DEATH', 'HEATH']
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
1. First it attempts to make exclusive guesses. These are guesses that don't use any of the letters used in previous guesses. As each guess is made (and the algorithm receives or generates feedback on the hits/misses from that guess) the possible exclusive guesses are trimmed until there are none.
2. As soon as there are no exclusive guesses to be made (takes roughly 3 guesses), then the algorithm switches to using inclusive guesses. A list of exclusive words is continually pruned to only include those with letters that have been matched so far.

The potential words that populate both of these lists initially is built from a list of 5 letter words passed in from either  `/usr/share/dict/words` on OSX systems or `wordle-dictionary.txt` included in this repository ([originally found here](https://github.com/redbo/scrabble/blob/master/dictionary.txt)). The words will be sorted in decreasing order by the frequency of their letters in the English language. That frequency is "EARIOTNSLCUDPMHGBFYWKVXZJQ" [found here](https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html) and then given a score. Duplicate letters are intrinsically detrimental to the score of guesses. This ensures that whenever we have multiple options we pick the one with the highest likelihood of being the target word.

## Performance
Out of 383 previous Wordle puzzles, this algorithm solved:
- 216 (56%) in 4 guesses
- 112 (29%) in 5 guesses
- 38  (10%) in 6 guesses
- 15  (4%)  in 7 guesses
- 2.  (.5%) in 8 guesses
