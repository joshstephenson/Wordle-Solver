# Python Wordle Solver

This is a Python script to solve [NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html) in least possible guesses.

The current version requires putting a target word in the script. After algorithm has been found, then it will be abstracted to help you solve a wordle puzzle by:
1. Providing a guess
2. Receiving feedback on that guess, including matching letters and whether their positions are correct or not
3. Providing subsequent guess

## The Algorithm
The algorithm will be based on a data structure of all the 5 letter words found in `/usr/share/dict/words` on OSX systems. The words will be sorted by the frequency of their letters in the English language. That frequency is "EARIOTNSLCUDPMHGBFYWKVXZJQ" [found here](https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html).
