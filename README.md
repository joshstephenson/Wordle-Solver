# Python Wordle Solver

This is a Python script to solve [NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html) in least possible guesses.

The current version can be used to solve a list of 5-letter words, printing out path to success OR it can help you beat Wordle by:
1. Providing a guess
2. Receiving feedback on that guess, including matching letters with position and misses
3. Providing subsequent guesses

## The Algorithm
The algorithm is 2 part:
1. First it attempts to make exclusive guesses. These are guesses that don't use any of the letters used in previous guesses. As each guess is made (and the algorithm receives or generates feedback on the hits/misses from that guess) the possible exclusive guesses are trimmed until there are none.
2. As soon as there are no exclusive guesses to be made (takes roughly 3 guesses), then the algorithm switches to using inclusive guesses. A list of exclusive words is continually pruned to only include those with letters that have been matched so far.

The potential wodrs is built from a list of 5 letter words passed in from either  `/usr/share/dict/words` on OSX systems or `wordle-dictionary.txt` from this repository. The words will be sorted by the frequency of their letters in the English language. That frequency is "EARIOTNSLCUDPMHGBFYWKVXZJQ" [found here](https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html) and then given a score. Duplicate letters are intrinsically detrimental to the score of guesses.

This algorithm can solve 90% of wordle puzzles in 4-5 guesses and the rest in 9 in worst case. 

### IMPERFECTIONS
Based on the scoring, the solver always starts with "IRATE", "CLONS" and "DUMPY". This clears the exclusive stack in three guesses and hands over the algorithm to guesses that match letters guessed.

Words with duplicate letters, such as "SERVE" or "ASSET" have proven to be problematic for initial implementations.
