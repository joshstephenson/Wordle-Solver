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
solved: LOUSE in 3 guesses: ['AROSE', 'TULIP', 'LOUSE']
solved: GULCH in 4 guesses: ['AROSE', 'UNLIT', 'PYGMY', 'GULCH']
solved: VAULT in 6 guesses: ['AROSE', 'LINTY', 'CHUMP', 'FAULT', 'GAULT', 'VAULT']
solved: GODLY in 4 guesses: ['AROSE', 'LINDY', 'MUTCH', 'GODLY']
solved: THREW in 4 guesses: ['AROSE', 'TUMID', 'LYNCH', 'THREW']
solved: FLEET in 4 guesses: ['AROSE', 'LINDY', 'BUTCH', 'FLEET']
solved: GRAVE in 4 guesses: ['AROSE', 'GLINT', 'DUCKY', 'GRAVE']
solved: INANE in 6 guesses: ['AROSE', 'LINTY', 'JUGUM', 'NAIVE', 'AZINE', 'INANE']
solved: SHOCK in 4 guesses: ['AROSE', 'CLIPT', 'FUNKY', 'SHOCK']
solved: CRAVE in 4 guesses: ['AROSE', 'GLINT', 'DUCKY', 'CRAVE']
solved: SPITE in 5 guesses: ['AROSE', 'UNLIT', 'PYGMY', 'PISTE', 'SPITE']
solved: VALVE in 6 guesses: ['AROSE', 'LINTY', 'BUMPH', 'GLACE', 'LEAVE', 'VALVE']
solved: SKIMP in 4 guesses: ['AROSE', 'UNLIT', 'PYGMY', 'SKIMP']
solved: CLAIM in 4 guesses: ['AROSE', 'LINTY', 'CHUMP', 'CLAIM']
solved: RAINY in 4 guesses: ['AROSE', 'DICTY', 'FLUNG', 'RAINY']
solved: MUSTY in 4 guesses: ['AROSE', 'UNLIT', 'PYGMY', 'MUSTY']
solved: PIQUE in 4 guesses: ['AROSE', 'UNLIT', 'PYGMY', 'PIQUE']
solved: DADDY in 7 guesses: ['AROSE', 'LINTY', 'BUMPH', 'CADGY', 'FADDY', 'WADDY', 'DADDY']
solved: QUASI in 4 guesses: ['AROSE', 'MILTY', 'PUNCH', 'QUASI']
solved: ARISE in 4 guesses: ['AROSE', 'MILTY', 'DUNCH', 'ARISE']
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
![WordleSolverResults](https://user-images.githubusercontent.com/11002/181612268-410e7b69-2970-4764-955a-b55004a765a2.png)

Out of 926 previous Wordle puzzles (included in "wordle-answers.txt" file), this algorithm solved 97.4% in 6 guesses or less with 82.5% in 4-5 guesses.
```
- 1   (0.1%) in 2 guesses (UNLIT)
- 2   (0.2%) in 3 guesses (LOUSE, HOUSE)
- 505 (55%)  in 4 guesses
- 259 (28%)  in 5 guesses
- 101 (11%)  in 6 guesses
- 41  (4.4%) in 7 guesses
- 11  (1.1%) in 8 guesses (KITTY, VISTA, RELAX, BOSOM, BOOBY, SPILL, SEVER, TAUNT, PARER, VALET, EAGLE)
- 4   (0.4%) in 9 guesses (SLEEP, RESET, RIVER, USURP)
- 2   (0.2%) in 10 guesses (SPELL, SAFER)
```
