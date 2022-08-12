# Python Wordle Solver
This is a python tool to solve [Wordle](https://www.nytimes.com/games/wordle/index.html).

## What is Wordle?
[Wordle](https://www.nytimes.com/games/wordle/index.html) is a five letter English word guessing game where the player must guess a target word in six guesses. For each attempt, the player enters a five letter word and receives feedback for each letter:
- Correct letters not in their correct positions will be marked yellow.
- Correct letters in their correct positions will be marked green.
- Letters that are not included in the target word will be marked gray.

![Screen Shot 2022-08-09 at 5 29 21 PM](https://user-images.githubusercontent.com/11002/183765171-4f49f73a-e4ea-42fc-ab17-91d8a9c1d77b.png)

## Goals of this Project
![results-SALET-3 6799](https://user-images.githubusercontent.com/11002/184381397-7d878a7b-430d-4662-9387-0689ce5f104a.png)

The goals of this project are:
1. To solve all 2315 answer words in 6 guesses or fewer. Currently all words are solved in 6 words or fewer with 89.8% solved in 4 and under. Using the starting word `SALET`, only 6 words require 6 guesses, but the overall average is 3.6799. Using `SLATE` as the starting word, there are 12 words that require 6 guesses but the overall average drops to 3.676.
2. To achieve the lowest possible guess average which is currently 3.676 guesses per puzzle, starting with `SLATE`.
3. To implement an algorithm that is not dependent on a given wordset. While this repository is tested on a static wordset, the algorithm should perform equally well if new words are added or removed. This is different than decesion-tree based solvers that use backtracking to determine the minimum possible average (3.42).
4. To provide [an interactive command line tool](#interactive-solver) that helps select the next best guess based on whatever previous guesses have been submitted.

## Word lists
There are two dictionaries used by the game:
- [nyt-answers.txt](https://github.com/joshstephenson/Wordle-Solver/blob/main/nyt-answers.txt) includes 2315 words which are valid puzzle answers.
- [nyt-guesses.txt](https://github.com/joshstephenson/Wordle-Solver/blob/main/nyt-guesses.txt) includes 10637 words which can only be used as guesses but will not be solutions to daily puzzles.

## About the Algorithm
The `answers` list is initially sorted by the popularity of letters in their respective positions. This is important for getting words with the highest word score.

At the start and after each guess, the algorithm finds the next best guess using the following steps:

1. If the count of available answers (starting at 2315) is above 50, then it simply returns the highest scoring answer.
2. After comparing each guess against the target word, it will tally the green, yellow and gray letters. This will be used to prune the remaining answers. See below for more information.
3. As soon as the answers are pruned down to fewer than 2 or less, it will pick the first answer (which will always have the highest word score) and then finally the last remaining answer if necessary.

### How words are pruned based on green, yellow and gray letters
After each guess, the answer list is pruned so that:
* Words without green letters in the right position are removed
* Words without yellow letters are removed
* Words with gray letters are removed
  
NOTE: Initial implementations missed one important improvement: Yellow letters are not letters in any position, they are letters in only 4 possible positions. Therefore the second bullet above was updated to:
* Words (without yellow letters) OR (with yellow letters in the same position they have already been tried) are removed.

Once the answers are pruned to fewer than 50 words, but greater than 2 (usually after one or two guesses), the algorithm will try to make a blended match I call an _intersecting match_. To do this, it will look at the set (no duplicates) of letters in the answer list and subtract the set of letters that have already been matched in guesses. From this target set, it will find a word (using a combination of `guesses` and `answers`) with letters that can reduce the available answers the most. Note that it may select a word with previously used letters in order to capture the highest number of target letters. This helps prune answers when they have many common letters. For more info see the function `_find_best_intersecting_word()` in [wordle_solver.py](https://github.com/joshstephenson/Wordle-Solver/blob/main/wordle_solver.py).

#### Example:
Let's look at the target word `HOUND`. The algorithm will start by guessing `SLATE` and then `CRONY` which will yield a green match on `N` in the 4th position and a yellow match on `O`. Once we filter out all the words that:
1. Don't have an `O` or have an `O` in the third position.
2. Don't have an `N` in the 4th position.
3. Have any of the gray letters: `{S,L,A,T,E,C,R,Y}`.

This will only leave 9 words in the answer list: `{BOUND, POUND, FOUND, DOING, MOUND, GOING, WOUND, HOUND, OWING}`.
As you can see, most of these words have 4 of the same letters and most are in the same position, so if we were to continue with the algorithm as is, it would take 8 guesses to solve `HOUND`. That's why it makes more sense here to take the letters `{M, H, D, U, G, F, W, Z, J, Q}` (letters that are in the answer list but have not been matched as green or yellow yet) and find a word with as many of those letters as possible. In this case, the word `HUMID` does well, and after that the answer list is down to just one word: `HOUND`. With this improvement it only takes 4 guesses to solve it: `SLATE>CRONY>HUMID>HOUND`

It's worth mentioning that this improvement brings down many words that take more than 4 guesses to solve, particularly 20 words that could not be solved at all in 6 guesses. However there are many words for which it degrades performance by adding an extra step, when an otherwise lucky guess would do better.

Take `LABEL` as an example. After a starting guess of `SLATE`, the remaining answers will be pruned to only 31. The highest scoring of these (based on letter frequency) is `BALER`, which after guessing would only leave 1 word: `LABEL`. Using the intersecting guess after `SLATE`, the guesses will be: `GRIND` and `CHUMP` before landing on `LABEL`.

## Usage
The current version can be used in 2 different ways:

First, by running [SolverTest.py](https://github.com/joshstephenson/Wordle-Solver/blob/main/SolverTest.py) with no arguments it will parse the entire answer list and solve them, printing out a running average, the word it solved, the number of guesses and the word path for each answer.

Example:
```
$ ./wordle_runner.py 
```

```
3.7428 HYDRO(3): SLATE, CRONY, HYDRO
3.7429 VIVID(4): SLATE, CRONY, HUMID, VIVID
3.7426 LUPUS(3): SLATE, COYPU, LUPUS
3.7427 LYMPH(4): SLATE, CURLY, HOING, LYMPH
3.7428 ABYSS(4): SLATE, CORNI, BOGEY, ABYSS
3.7429 HUMUS(4): SLATE, CORNI, DUMPY, HUMUS
3.7435 JUMBO(5): SLATE, CRONY, HUMID, GUMBO, JUMBO
3.7436 ETHIC(4): SLATE, TRIED, BENCH, ETHIC
3.7437 UNZIP(4): SLATE, CRONY, GUIMP, UNZIP
3.7438 UMBRA(4): SLATE, FAIRY, BUNCO, UMBRA
3.7439 MIMIC(4): SLATE, CRONY, BUMPH, MIMIC
3.7436 AFFIX(3): SLATE, FAIRY, AFFIX
3.7433 ETHOS(3): SLATE, CORNI, ETHOS
3.7434 INBOX(4): SLATE, CRONY, GUIDE, INBOX
3.7431 NYMPH(3): SLATE, CRONY, NYMPH
3.7432 ENNUI(4): SLATE, BONEY, MUCID, ENNUI
3.7437 IGLOO(5): SLATE, CURLY, POIND, LIMBO, IGLOO
3.7434 IDYLL(3): SLATE, CURLY, IDYLL
...
```

For debugging purposes, you can enable logging with `export WORDLE_LOGGING=1; ./SolverTest.py`.

You can test a single word with the `-w WORD` option:
```
$ ./wordle_runner.py -w alert
Solved: ALERT in 4 guesses: 
SLATE, CRAPE, ALTER, ALERT
```

You can find the rank of a word in the overall word scores with the `-r WORD` option:
```
$ ./solver_test.py -r alert
8/12953
```

And finally, you can get the individual score of a word with the `-s WORD` option:
```
$ ./solver_test.py -s alert
4554
```

## Interactive Solver
This is the most useful thing you might want to use while you are actually solving the puzzle online. It will recommend the player's next guess, receive the player's chosen guess along with green and yellow letters:
```
$ ./wordle_interactive.py
```

Example:
```
joshuastephenson@~/Projects/Wordle-Solver$ ./WordleInteractive.py 
What is your first word guess? (press ENTER for EARST) 
> 
You entered: EARST
Please enter green letters (press ENTER for none)
> t
Please enter yellow letters (press ENTER for none)
> ear
Your next guess should be: GULCH
What is your next guess? (press ENTER for GULCH)
> 
You entered: GULCH
Please enter green letters (press ENTER for none)
> 
Please enter yellow letters (press ENTER for none)
> l
Your next guess should be: ALERT
What is your next guess? (press ENTER for ALERT)
> 
You entered: ALERT
Please enter green letters (press ENTER for none)
> alert
You won 😉 in 3 guesses!
```

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

With these frequencies, we can calculate a score for each word based on the letters it has in positions 1 through 5. The 50 highest scoring answer words are, in order:

```
1-10:   SLATE, SAUCE, SLICE, SHALE, SAUTE, SHARE, SHINE, SUITE, CRANE, SAINT
11-20:  SOAPY, SHONE, SHIRE, SAUCY, SLAVE, SANER, SNARE, STALE, CRATE, SHORE
21-30:  SUAVE, SLIDE, STARE, SLIME, BRACE, SHINY, CRONE, BRINE, SHADE, SPACE
31-40:  SPARE, SHAME, SLANT, SCALE, SPINE, TRACE, SHAKE, STONE, SHAPE, SCARE
41-50:  SHAVE, SALTY, SLOPE, SINCE, POISE, SWINE, BONEY, SNORE, STOLE, SADLY
```

## Contributions
If you use this or would like to contribute, feel free to fork, contact me or submit a PR. Please note: I am not interested in solutions that precompute the best path for every word and cache them. I don't find solutions of that kind very compelling.
