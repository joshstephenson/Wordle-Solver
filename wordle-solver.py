#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
import re

DICTIONARY = "/usr/share/dict/words"
LENGTH = 5

# We will attempt to pict words with most frequently used letters first
# https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html
LFREQ = [l for l in "EARIOTNSLCUDPMHGBFYWKVXZJQ"]

# FRDICT dictionary will map letters to points. Those with most frequency get most points.
# Words can then have points based on frequency of characters
FRDICT = dict()
for i in range(len(LFREQ)):
    FRDICT[LFREQ[i]] = 26-i

def _get_word_points(word):
    points = 0
    for char in word:
        points += FRDICT[char]
    return points

class Solution:
    def __init__(self, word, guess_count):
        self.word = word
        self.guess_count = guess_count

class Solver:
    def __init__(self, target):
        self.target = target
        self.words = []
        self._get_words()
        self.guesses = []
        self.matches = dict()

    def _get_words(self, file=DICTIONARY):
        word_arr = []

        # Open dictionary and save words with correct length
        with open(file, 'r') as words:
            for line in words:
                word = line.strip().upper()
                if len(word) == LENGTH:
                    word_arr.append(word)

        # Apparently sorting words by frequency lead to poorer performance by far
        # Sort words by frequency of characters in English
#        word_dict = dict()
#        for word in word_arr:
#            word_dict[word] = _get_word_points(word)
#
#        sorted_words = sorted(word_dict.items(), key=lambda item: item[1], reverse=True)
#        for word in sorted_words:
#            self.words.append(word[0])

        self.words = word_arr

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

solution = Solver("CYNIC").solve()

print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses.")
