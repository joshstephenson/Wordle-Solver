# Python Wordle Solver

## What is Wordle?
This is a Python script to solve the [NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html) in least possible guesses. Wordle is a 5-letter word guessing game where the player must guess a word in six guesses. For each guess, the player enters a 5-letter word and receives feedback. Feedback includes:
- letters in the word but not in correct position (yellow)
- letters in the word and in the correct position (green)
- letters not in the word at all (gray)

## Performance
![results-4 0575](https://user-images.githubusercontent.com/11002/182266138-b42cf540-0fdf-4677-be6f-9427df93e005.png)

Out of 2315 Wordle puzzles (included in "nyt-answers.txt" file), this algorithm solved 99.6% in 6 guesses or fewer. There are currently 10 words that aren't solved within 6 guesses with elbow, the worst offender at 8 guesses.

## About the Program
There are two dictionaries provided by the NYTimes for Wordle. One is for valid guesses which is around ten thousand words and the other is for valid answers which is only around 2300 words. Both are included in this repository.

## Usage
The current version can be used in 2 different ways:
First, by running the script directly it will parse a list of recent Wordle words and solve them, printing out the words it used to guess and total number of guesses

To run the entire NYT Wordle dictionary of answers:
```
WORDLE_LOGGING=0 && ./SolverTest.py 
```

```
4.1858 HYDRO(3): OATER, LYSIN, HYDRO
4.1846 HYENA(3): OATER, LYSIN, HYENA
4.1834 HYMEN(3): OATER, LYSIN, HYMEN
4.1833 HYPER(4): OATER, LYSIN, CYBER, HYPER
4.1831 ICILY(4): OATER, LYSIN, CHAMP, ICILY
4.1829 ICING(4): OATER, LYSIN, CHUMP, ICING
4.1827 IDEAL(4): OATER, LYSIN, GAMED, IDEAL
4.1825 IDIOM(4): OATER, LYSIN, CHUMP, IDIOM
4.1824 IDIOT(4): OATER, LYSIN, CAPED, IDIOT
4.1822 IDLER(4): OATER, LYSIN, PAVED, IDLER
4.184  IDYLL(6): OATER, LYSIN, CHAMP, BOWED, DILLY, IDYLL
4.1848 IGLOO(5): OATER, LYSIN, GAMBE, LOGIC, IGLOO
4.1855 ILIAC(5): OATER, LYSIN, CUBED, AMOVE, ILIAC
4.1854 IMAGE(4): OATER, LYSIN, GAMED, IMAGE
4.1852 IMBUE(4): OATER, LYSIN, CHUMP, IMBUE
4.185  IMPEL(4): OATER, LYSIN, AMPED, IMPEL
...
```

For debugging purposes, you can enable logging with `WORDLE_LOGGING=1` in your OS environment.

To test a single word:
```
WORDLE_LOGGING=0 && ./SolverTest.py -w elbow
Solved: YIELD in 3 guesses: 
OATER, LYSIN, YIELD
```

Second, by loading the Solver class into the python shell or another python script, a player can play Wordle receiving advice on which word to guess next. After each guess the player must provide the feedback from the Wordle game (green, yellow and gray letters).

If the target word is SANER:
```
from WordleSolver import Solver
 
 solver = Solver()
 # First argument: The word you guessed
 # Second argument: Green letters in their corresponding positions. Both E and R are in the right spot.
 # Third argument: Yellow letters (out of place hits)
 # All other letters (O and T) are misses.
 solver.guess("oater", "___er", "a")
 print("Your next guess should be: " + solver.next_guess())```
```

Output:
```
~/Projects/Wordle-Solver$ ./wordle-sample.py 
Your next guess should be: LYSIN
```

## The Algorithm
The algorithm has two distinct word lists. The `answers` list is populated from nyt-answers.txt and `exclusive_words` is populated from a combination of 'nyt-guesses.txt' and 'nyt-answers.txt'. `exclusive_words` is a python list that is initially sorted by the popularity of letters in each word. `answers` is a python list that is initially sorted by the popularity of letters in their respective positions.

1. First it attempts to make exclusive guesses. These are guesses that don't use any of the letters used in previous guesses. As each guess is made (and the algorithm receives or generates feedback on the hits/misses from that guess) the possible exclusive guesses are trimmed.
2. As soon as there are fewer inclusive guesses than exclusive guesses to be made (takes roughly 3 guesses) the algorithm switches to using inclusive guesses. A list of exclusive words is continually pruned to only include those with letters that have been matched so far.

As the inclusive word list is updated, the frequency of letters available in the inclusive list is continually updated and then both word lists are resorted based on the composition of the new letter frequency. This ensures that each guess cuts the word list down maximally.

The words are sorted in decreasing order by the frequency of their letters within the remaining inclusive word list and then given an overall word score. Duplicate letters are intrinsically detrimental to the score of words. This ensures that whenever we have multiple options we pick the one with the highest likelihood of being the target word.
