# Python Wordle Solver
This is a python tool to solve [Wordle](https://www.nytimes.com/games/wordle/index.html). The goals of this project are:
1. To solve all 2315 answer words in 6 guesses or fewer. Currently, there are 11 words that require 7 guesses. 
2. To achieve the lowest possible guess average which is currently 3.9348 guesses per puzzle with the starting word EARST.
3. To implement an algorithm that is not dependent on a given wordset. While this repository is tested on a static wordset, the algorithm should perform equally well if new words are added or removed.
4. To provide an interactive tool that helps select the next best guess while playing the game online.

## What is Wordle?
[Wordle](https://www.nytimes.com/games/wordle/index.html) is a five letter English word guessing game where the player must guess a target word in six guesses. For each attempt, the player enters a five letter word and receives feedback for each letter:
- Correct letters not in their correct positions will be marked yellow.
- Correct letters in their correct positions will be marked green.
- Letters that are not included in the target word will be marked gray.

## Performance
![results-EARST-3 9348](https://user-images.githubusercontent.com/11002/182449278-57b8f3ed-ed26-4b3b-9181-13220b4c10a0.png)

Out of 2315 Wordle puzzles (included in "nyt-answers.txt" file), this algorithm solves 99.5% in 6 guesses or fewer and 79% in 4 guesses or fewer. There are currently 11 words that aren't solved within the 6 guess limit: ASSAY, AWARE, BEZEL, FETAL, GRAZE, OFFER, REGAL, RIDER, RIPER, ROGER & SHALL which all require 7 guesses.

## Dictionaries
There are two dictionaries provided by the NYTimes for Wordle:
- [nyt-answers.txt](https://github.com/joshstephenson/Wordle-Solver/blob/main/nyt-answers.txt) 2315 words which are valid puzzle answers and can also be used as guesses.
- [nyt-guesses.txt](https://github.com/joshstephenson/Wordle-Solver/blob/main/nyt-guesses.txt) 10637 words which can be used as guesses but will not be used as puzzle answers.

## Usage
The current version can be used in 2 different ways:

First, by running [SolverTest.py](https://github.com/joshstephenson/Wordle-Solver/blob/main/SolverTest.py) with no arguments it will parse the entire answer list and solve them, printing out the words it used to guess and total number of guesses. It will also print out a running average of guesses per answer.

Example:
```
./SolverTest.py 
```

```
4.1111 ANODE(3): EARST, COLIN, ANODE
4.0989 ANTIC(3): EARST, COLIN, ANTIC
4.0978 ANVIL(4): EARST, COLIN, PLAIN, ANVIL
4.086  AORTA(3): EARST, COYED, AORTA
4.0851 APART(4): EARST, CHINO, PUDGE, APART
4.0842 APHID(4): EARST, COLIN, HAMED, APHID
4.0833 APING(4): EARST, COLIN, AMPED, APING
4.0825 APNEA(4): EARST, COLIN, HYPED, APNEA
4.0918 APPLE(5): EARST, COLIN, DUMPY, LAPEL, APPLE
4.0909 APPLY(4): EARST, COLIN, DUMPY, APPLY
4.09   APRON(4): EARST, COLIN, BARON, APRON
4.0891 APTLY(4): EARST, COLIN, UPBYE, APTLY
...
```

For debugging purposes, you can enable logging with `WORDLE_LOGGING=1 && ./SolverTest.py`.

You can test a single word with the `-w WORD` option:
```
./SolverTest.py -w elbow
Solved: YIELD in 3 guesses: 
OATER, LYSIN, YIELD
```

You can find the rank of a word in the overall word scores with the `-r WORD` option:
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
joshuastephenson@~/Projects/Wordle-Solver$ ./WordleInteractive.py 
What is your first word guess? May I recommend EARST?
> salet
You entered: SALET
Please enter green letters (or ENTER for none)
>  
Please enter yellow letters (or ENTER for none)
> l
Your next guess should be: CORNI
What is your next guess?
> corni
You entered: CORNI
Please enter green letters (or ENTER for none)
> co
Please enter yellow letters (or ENTER for none)
> 
Your next guess should be: COYLY
What is your next guess?
> coyly
You entered: COYLY
Please enter green letters in a string like '__A__' (or ENTER for none)
> coyly
You won 😉 in 3 guesses!
```

## The Algorithm
The algorithm has two separate word lists. The property `answers` is populated from nyt-answers.txt and the property `exclusive_words` is populated from a combination of 'nyt-guesses.txt' and 'nyt-answers.txt'. `exclusive_words` is a python list that is initially sorted by the popularity of letters in each word. This is best for pruning the list of answers as fast as possible. `answers` is a python list that is initially sorted by the popularity of letters in their respective positions. This is important for getting words with the highest word score.

After each guess, the algorithm finds the next best guess using the following steps:

1. First, it attempts to make exclusive guesses. These are guesses that don't use any of the letters used in all previous guesses and they are always words with the highest word score for letters _irrespective_ of their positions. As each guess is made (and the Solver class provides feedback on the green, yellow and gray letters from that guess) the possible exclusive guesses are pruned so as not to include any previously used letters. Sorting is preserved, so the first item is always the highest scoring word. After each guess, `answers` is also pruned but inclusively, meaning it removes words that have gray letters, words that don't have yellow letters, and words that don't have green letters in their correct spots. See method `_word_should_be_kept()` for more info. The scoring of words in answers corresponds to the composition of letters _respective_ of their positions.
2. As soon as the answers are pruned down to less than 100 words, but greater than 3 (usually after one guess), the algorithm will try to make a blended match I call an _intersecting match_. To do this, it will look at the distinct set of letters in remaining answers and subtract the set of letters that have already been matched in guesses (see `LetterFeedback` class). From this target set, it will find a word (using all original words) that has the most number of these letters. Note that it may select a word with previously used letters in order to capture the highest number of target letters. This helps prune answers when they have many common letters.
3. As soon as the answers are pruned down to less than 2 or less, it will pick the first answer (which will always have the highest word score) and then finally the last remaining answer if necessary.

## Most Popular Letters for Each Position in Five Letter English Words
- S is the most frequent starting letter.
- A is the most frequent second and third letter.
- E is the most frequent fourth and fifth letter.

Below is a table of calculated frequencies in all positions.

Position|Letter:Frequency in Answers
------|-----------------------
1|S:366, C:198, B:173, T:149, P:142, A:141, F:136, G:115, D:111, M:107, R:105, L:88, W:83, E:72, H:69, V:43, O:41, N:37, I:34, U:33, Q:23, K:20, J:20, Y:6, Z:3, X:0
2|A:304, O:279, R:267, E:242, I:202, L:201, U:186, H:144, N:87, T:77, P:61, W:44, C:40, M:38, Y:23, D:20, B:16, S:16, V:15, X:14, G:12, K:10, F:8, Q:5, Z:2, J:2
3|A:307, I:266, O:244, E:177, U:165, R:163, N:139, L:112, T:111, S:80, D:75, G:67, M:61, P:58, B:57, C:56, V:49, Y:29, W:26, F:25, K:12, X:12, Z:11, H:9, J:3, Q:1
4|E:318, N:182, S:171, A:163, L:162, I:158, C:152, R:152, T:139, O:132, U:82, G:76, D:69, M:68, K:55, P:50, V:46, F:35, H:28, W:25, B:24, Z:20, Y:3, X:3, J:2, Q:0
5|E:424, Y:364, T:253, R:212, L:156, H:139, N:130, D:118, K:113, A:64, O:58, P:56, M:42, G:41, S:36, C:31, F:26, W:17, B:11, I:11, X:8, Z:4, U:1, V:0, J:0, Q:0

With these frequencies, we can calculate a score for each word based on the letters it has in positions 1 through 5. The 100 highest scoring words are, in order:

```
1-10:   OATER, ORATE, ROATE, REALO, ARTEL, RATEL, TALER, ALERT, ALTER, LATER, 
11-20:  AEROS, SOARE, AROSE, RETIA, TERAI, IRATE, ARETS, ASTER, EARST, RATES, 
21-30:  REAST, RESAT, STEAR, STRAE, TARES, TASER, TEARS, TERAS, STARE, ARIEL, 
31-40:  RAILE, ARLES, EARLS, LAERS, LARES, LASER, LEARS, RALES, REALS, SERAL, 
41-50:  AESIR, REAIS, SERAI, ARISE, RAISE, ANTRE, EARNT, NERAL, LEARN, RENAL, 
51-60:  STOAE, TOEAS, RAINE, EARNS, NARES, NEARS, REANS, SANER, SNARE, ALOES, 
61-70:  OCREA, TELIA, LEATS, SALET, SETAL, STELA, TAELS, TALES, TEALS, TESLA, 
71-80:  LEAST, SLATE, STALE, STEAL, CARET, CARTE, RECTA, CATER, CRATE, REACT, 
81-90:  TRACE, CARLE, LACER, RECAL, URATE, CLEAR, ALURE, UREAL, ESTRO, RESTO, 
91-100: ROSET, ROTES, TORES, TORSE, STORE, OILER, ORIEL, REOIL, EORLS, LORES
```

## Find the Best Starting Word
Using the right starting word makes a big difference. While OATER has the highest calculated score, with this algorithm EARST has the lowest average number of guesses of 3.9348. If you modify the algorithm and want to find the best starting word, use the script `FindStartingWord.py` and wait a _long time_ 😇. This script will loop over all 12952 valid answers and guesses calculating the average number of guesses to arrive at each of the 2315 answer words. It will print out the best performance so far after each starting word is finished.

## Contributions
If you use this or would like to contribute, feel free to fork, contact me or submit a PR. Please note: I am not interested in solutions that precompute the best path for every word and cache them. I don't find solutions of that kind very compelling.
