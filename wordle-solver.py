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

# generate a score for words based on composition of letters and their frequency in English
# Don't give points to duplicate letters becaues they don't help in guessing
# Perhaps give negative value for duplicate letters
def _get_word_points(word):
    points = 0
    letters = []
    for letter in word:
        if letter not in letters:
            points += FRDICT[letter]
        else:
            points -= FRDICT[letter]
        letters.append(letter)
    return points


# INITIAL STATE:
# - matches is empty
# - unguessed is all words
# - guessed is empty
# - inclusive is empty (no matches)
# - exclusive is all words
#
# START by making a wild guess
# - find matching letters and add to `matches` dictionary
# - value is position of "in position" letters or -1 for out of position letters
# PROCEED by making an EXCLUSIVE GUESS
# - only look for words with NO matching letters to narrow down letters faster
# - e.g. - if letter "R" is matched, then only words without R will be guessed
# AFTER EACH EXCLUSIVE GUESS:
# - guess is added to `guessed` and removed from `unguessed`
# - all words that have matching letters are added to `inclusive`
# - all words that have matching letters are removed from `exclusive`
# WHEN MATCHES HAS LENGTH=5, THEN SWITCH TO INCLUSIVE GUESSING

class Data:
    def __init__(self):
        words = self._get_words()
        self.matches = dict()
        self.unguessed  = words.copy()
        self.guessed    = []
        self.inclusive  = words.copy()
        self.exclusive  = words.copy()

    def add_match(self, letter, position):
        self.matches[letter] = position

    def cleanup(self):
        # remove words from inclusive if matched letters ARE NOT in the word
        for letter in self.matches.keys():
            matcher = re.compile(letter)
            inclusive = self.inclusive.copy()
            for word in inclusive:
                if matcher.search(word) is None:
                    self.inclusive.remove(word)

            # remove words from exclusive if matched letters ARE in the word
            exclusive = self.exclusive.copy()
            for word in exclusive:
                if matcher.search(word) is not None:
                    self.exclusive.remove(word)


    def make_inclusive_guess(self):
        target_count = len(self.matches)
        guess = None
        while guess is None:
            if len(self.inclusive) == 0:
                raise "No Inclusive Matches Left"
            for word in self.inclusive:
                current_count = 0
                for letter in self.matches:
                    if re.search(letter, word) is not None:
                        current_count += 1
                    if current_count == target_count:
                        break
                print("found an inclusive match: " + word)
                guess = word
                if word in self.inclusive:
                    self.inclusive.remove(word)
                self.guessed.append(word)
                break
        return guess

    def make_exclusive_guess(self):
        guess = None
        while guess is None:
            if len(self.exclusive) == 0:
                raise "No Exclusive Matches Left"
            for word in self.exclusive:
                for letter in self.matches:
                    if re.search(letter, word) is not None:
                        # skip this word and go to next
                        break
                print("found an exclusive match: " + word)
                guess = word
                if word in self.exclusive:
                    self.exclusive.remove(word)
                self.guessed.append(word)
                break
        return guess

    def next_guess(self):
        print("Finding guess for letters: " + str(self.matches))

        guess = None
        # If we haven't matched most of the letters
        if len(self.matches) < (LENGTH-1):
            # make an exclusive guess
            return self.make_exclusive_guess()
        # otherwise, make an inclusive guess (using the letters we have matched so far)
        return self.make_inclusive_guess()


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
#
#        print(self.words)
        return word_arr

class Solution:
    def __init__(self, word, guess_count):
        self.word = word
        self.guess_count = guess_count

class Solver:
    def __init__(self, target):
        self.target = target
        self.data = Data()
        self.guesses = []

    def _is_solved(self, word):
        return word == self.target

    def solve(self):
        guess = self.data.next_guess()
        while self._is_solved(guess) is False:
            index = 0

            for letter in guess:
                matching = re.compile(letter)
                result = matching.search(self.target)

                # if the letter is a match
                if result is not None:
                    position = result.span()[0]
                    # letter is in correct position
                    if position == index:
                        self.data.add_match(letter, position)
                    # letter is not in the correct position
                    else:
                        self.data.add_match(letter, -1)
                    self.data.cleanup()

                index += 1
            guess = self.data.next_guess()

        print(self.data.guessed)
        return Solution(guess, len(self.data.guessed))

solution = Solver("LYRIC").solve()

print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses.")
