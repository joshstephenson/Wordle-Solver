# Python Wordle Solver

## What is Wordle?
This is a Python script to solve the [NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html) in least possible guesses. Wordle is a 5-letter word guessing game where the player must guess a word in six guesses. For each guess, the player enters a 5-letter word and receives feedback. Feedback includes:
- letters in the word but not in correct position (yellow)
- letters in the word and in the correct position (green)
- letters not in the word at all (gray)

## About the Program
There are two dictionaries provided by the NYTimes for Wordle. One is for valid guesses which is around ten thousand words and the other is for valid answers which is only around 2300 words. Both are included in this repository.

## Usage
The current version can be used in 2 different ways:
First, by running the script directly it will parse a list of recent Wordle words and solve them, printing out the words it used to guess and total number of guesses

```
4.0757 UNCUT(3): OATER, LYSIN, UNCUT
4.0752 UNDER(3): OATER, LYSIN, UNDER
4.0752 UNDID(4): OATER, LYSIN, CUMIN, UNDID
4.0756 UNDUE(5): OATER, LYSIN, CUBED, NUDGE, UNDUE
4.076  UNFED(5): OATER, LYSIN, QUEEN, UNWED, UNFED
4.076  UNFIT(4): OATER, LYSIN, TUNIC, UNFIT
4.076  UNIFY(4): OATER, LYSIN, PUDGE, UNIFY
4.0755 UNION(3): OATER, LYSIN, UNION
4.0754 UNITE(4): OATER, LYSIN, TWINE, UNITE
4.0754 UNITY(4): OATER, LYSIN, MINTY, UNITY
4.0749 UNLIT(3): OATER, LYSIN, UNLIT
4.0744 UNMET(3): OATER, LINDS, UNMET
4.0739 UNSET(3): OATER, LINDS, UNSET
4.0734 UNTIE(3): OATER, LYSIN, UNTIE
4.0729 UNTIL(3): OATER, LINCH, UNTIL
...
```

Second, by loading the Solver class into the python shell or another python script, a player can play Wordle receiving advice on which word to guess next. After each guess the player must provide the feedback from the Wordle game (green, yellow and gray letters).

Example from July 28th (2022) Wordle (answer: STOMP):
```
from WordleSolver import Solver
  
solver = Solver()
solver.guess("arose")
solver.miss("are")
olver.hit("o", 3)
solver.hit("s")
solver.guess("sloth")
solver.miss("lh")
solver.hit("s", 1)
solver.hit("t")
solver.guess("stowp")
```

Output:
```
joshuastephenson@~/Projects/Wordle-Solver$ ./wordle-sample.py 
Your next guess should be: STOWP
All options:
['STOWP', 'SPOUT', 'STOUP', 'STOMP', 'SNOUT', 'STONY', 'STOCK', 'SCOUT', 'SPOTS', 'STOOP', 'STOPS', 'STOPT', 'SNOOT', 'SNOTS', 'STOIC', 'STOWS', 'SWOTS', 'SCOOT', 'SCOTS', 'STOGY', 'STOOK', 'STOUT', 'SOOTY', 'STOBS', 'STOOD', 'SOOTS', 'STOSS', 'STOTS', 'STOTT', 'SWOUN', 'SNOWY', 'SNOOP', 'SPOON', 'SWOOP', 'SWOPS', 'SCOOP', 'SCOPS', 'SNOWS', 'SWOON', 'SPOOK', 'SMOCK', 'SNOOK', 'SCOWS', 'SPOOF', 'SNOBS', 'SNOGS', 'SMOKY', 'SNOOD', 'SWOBS', 'SCOFF', 'SMOGS', 'SOOKS']
```

## The Algorithm
The algorithm has two distinct word lists. The `answers` list is populated from nyt-answers.txt and `exclusive_words` is populated from a combination of 'nyt-guesses.txt' and 'nyt-answers.txt'. `exclusive_words` is a python list that is initially sorted by the popularity of letters in each word. `answers` is a python list that is initially sorted by the popularity of letters in their respective positions.

1. First it attempts to make exclusive guesses. These are guesses that don't use any of the letters used in previous guesses. As each guess is made (and the algorithm receives or generates feedback on the hits/misses from that guess) the possible exclusive guesses are trimmed.
2. As soon as there are fewer inclusive guesses than exclusive guesses to be made (takes roughly 3 guesses) the algorithm switches to using inclusive guesses. A list of exclusive words is continually pruned to only include those with letters that have been matched so far.

As the inclusive word list is updated, the frequency of letters available in the inclusive list is continually updated and then both word lists are resorted based on the composition of the new letter frequency. This ensures that each guess cuts the word list down maximally.

The words are sorted in decreasing order by the frequency of their letters within the remaining inclusive word list and then given an overall word score. Duplicate letters are intrinsically detrimental to the score of words. This ensures that whenever we have multiple options we pick the one with the highest likelihood of being the target word.

## Performance
![results-4 0989](https://user-images.githubusercontent.com/11002/182252611-9fbca7d8-36a4-4623-9ce6-dbd43a73d31f.jpg)

Out of 2315 Wordle puzzles (included in "nyt-answers.txt" file), this algorithm solved 98.5% in 6 guesses or fewer. There are currently 34 words that aren't solved within 6 guesses.
