# Python Wordle Solver

## What is Wordle?
This is a Python script to solve the [NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html) in least possible guesses. Wordle is a 5-letter word guessing game where the player must guess a target word in six guesses. For each attempt, the player enters a 5-letter word and receives feedback for each letter:
- Correct letters not in their correct positions will be marked yellow.
- Correct letters in their correct positions will be marked green.
- Letters that are not included in the target word will be marked gray.

## Performance
![results-3 9706](https://user-images.githubusercontent.com/11002/182399042-b6e3286c-c075-43e2-97d9-cb57c4ec8c14.png)

Out of 2315 Wordle puzzles (included in "nyt-answers.txt" file), this algorithm solved 99.6% in 6 guesses or fewer and 74% in 4 guesses or fewer. There are currently 8 words that aren't solved within the 6 guess limit.

## About the Program
There are two dictionaries provided by the NYTimes for Wordle. One is for valid guesses which is around ten thousand words and the other is for valid answers which is only around 2300 words. Both are included in this repository:
- [nyt-answers.txt](https://github.com/joshstephenson/Wordle-Solver/blob/main/nyt-answers.txt)
- [nyt-guesses.txt](https://github.com/joshstephenson/Wordle-Solver/blob/main/nyt-guesses.txt)

## Usage
The current version can be used in 2 different ways:

First, by running [SolverTest.py](https://github.com/joshstephenson/Wordle-Solver/blob/main/SolverTest.py) with no arguments it will parse the entire answer list and solve them, printing out the words it used to guess and total number of guesses. It will also print out a running average of guesses per answer.

Example:
```
./SolverTest.py 
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

For debugging purposes, you can enable logging with `WORDLE_LOGGING=1 && ./SolverTest.py`.

You can also test a single word with the `-w WORD` option:
```
WORDLE_LOGGING=0 && ./SolverTest.py -w elbow
Solved: YIELD in 3 guesses: 
OATER, LYSIN, YIELD
```

You can also find the rank of a word in the overall word scores with the `-r WORD` option:
```
joshuastephenson@~/Projects/Wordle-Solver$ ./SolverTest.py -r salet
63/12953
```

And finally, you can get the individual score of a word with the `-s WORD` option:
```
joshuastephenson@~/Projects/Wordle-Solver$ ./SolverTest.py -s salet
4324
```

## Interactive Solver
This is the most useful thing you might want to use while you are actually solving the puzzle online. It will recommend the player's next guess, receive the player's chosen guess along with green and yellow letters:
```
./WordleInteractive.py
```

Example:
```
joshstephenson@~/Projects/Wordle-Solver$ ./WordleInteractive.py 
What is your first word guess? May I recommend OATER? salet
You entered: SALET
Please enter green letters in a string like '__A__' (or ENTER for none) 
Please enter yellow letters (or ENTER for none) l
Your next guess should be: CORNI
What is your next guess? corni
You entered: CORNI
Please enter green letters in a string like '__A__' (or ENTER for none) co___
Please enter yellow letters (or ENTER for none) 
Your next guess should be: COYLY
What is your next guess? coyly
You entered: COYLY
Please enter green letters in a string like '__A__' (or ENTER for none) coyly
We won in 3 guesses!
```

## Finding the Best Starting Word
Using the right starting word makes a big difference. While OATER has the highest calculated score, many believe SALET to be the best starting word. To find the best starting word, use the script `FindStartingWord.py` and wait a long time. This script will loop over all 12952 words calculating the average number of guesses to solve each of the 2315 answer words. It will print out the best performance so far after each batch.

## The Algorithm
The algorithm has two separate word lists. The property `answers` is populated from nyt-answers.txt and the property `exclusive_words` is populated from a combination of 'nyt-guesses.txt' and 'nyt-answers.txt'. `exclusive_words` is a python list that is initially sorted by the popularity of letters in each word. This is best for pruning the list of answers as fast as possible. `answers` is a python list that is initially sorted by the popularity of letters in their respective positions. This is important for getting words with the highest word score.

After each guess, the algorithm finds the next best guess using the following steps:

1. First, it attempts to make exclusive guesses. These are guesses that don't use any of the letters used in all previous guesses. As each guess is made (and the algorithm receives or generates feedback on the hits/misses from that guess) the possible exclusive guesses are pruned so as not to include any previously used letters. After each guess, `answers` is also pruned but inclusively, meaning it prunes out any words that have gray letters, any words that don't have yellow letters and any words that don't have green letters in their correct indices. See method `_word_should_be_kept()` for more info.
2. As soon as the answers are pruned down to less than 100 words, but greater than 3 (usually after one guess), the algorithm will try to make a blended match I call an _intersecting match_. It will look at the set of letters contained by remaining answers and subtract the set of letters that have already been matched in guesses. From this set, it will find a word (using all original words) that has the most number of these letters. This helps prune answers when they have many common letters.
3. As soon as the answers are pruned down to less than 2 or less, it will pick the answer with the highest word score, and then finally the last remaining answer if necessary.

The words are sorted in descending order by the frequency of their letters within the remaining inclusive word list and then given an overall word score. Duplicate letters are intrinsically detrimental to the score of words. This ensures that whenever we have multiple options we pick the one with the highest likelihood of being the target word.
