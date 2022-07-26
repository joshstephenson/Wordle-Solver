#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
import re

DICTIONARY = "/usr/share/dict/words"
LENGTH = 5

# We will attempt to pict words with most frequently used letters first
# https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html
LFREQ = [l for l in "EARIOTNSLCUDPMHGBFYWKVXZJQ"]

class Solution:
    def __init__(self, word, guess_count):
        self.word = word
        self.guess_count = guess_count

class Solver:
    def __init__(self, target):
        self.target = target
        self._get_words()
        self.guesses = []
        self.matches = dict()

    def _get_words(self, file=DICTIONARY):
        words = []
        with open(file, 'r') as dict:
            for line in dict:
                word = line.strip().upper()
                if len(word) == 5:
                    words.append(word)

        self.words = words


    def _is_solved(self, word):
        return word == self.target

    def _find_guess(self):
        target_count = len(self.matches)
        guess = None
        print("Finding guess for chars: " + str(self.matches))
        while guess is None:
            if len(self.words) == 0:
                raise "No Match Found."
            for word in self.words:
                #print("--- " + word)
                self.words.remove(word)
                current_count = 0
                for mat in self.matches:
                    matcher = re.compile(mat)
                    if matcher.search(word) is not None:
                        current_count += 1
                if current_count == target_count:
                    print("found a possible word: " + word)
                    guess = word
                    self.guesses.append(guess)
                    break
        return guess

    def solve(self):
        guess = self._find_guess()
        while self._is_solved(guess) is False:
            index = 0
            for char in guess:
                matching = re.compile(char)
                result = matching.search(self.target)

                # character is in target word
                if result is not None:
                    position = result.span()[0]
                    # character is in correct position
                    if position == index:
                        self.matches[char] = index

                    # character is not in correct position
                    else:
                        self.matches[char] = -1
                index += 1
            guess = self._find_guess()

        print(self.guesses)
        return Solution(guess, len(self.guesses))

solution = Solver("CINIC").solve()

print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses.")
