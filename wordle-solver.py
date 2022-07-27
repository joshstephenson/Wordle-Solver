#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
import re

DICTIONARY = "/usr/share/dict/words"
LENGTH = 5
PENALTY_FOR_LETTER_REDUNDANCY = 0

# We will attempt to pict words with most frequently used letters first
# https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html
LFREQ = [l for l in "EARIOTNSLCUDPMHGBFYWKVXZJQ"]

# FRDICT dictionary will map letters to points. Those with most frequency get most points.
# Words can then have points based on frequency of characters
FRDICT = dict()
for i in range(len(LFREQ)):
    FRDICT[LFREQ[i]] = (26-i)*5

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
            points -= PENALTY_FOR_LETTER_REDUNDANCY # minus 10 points for duplicate letters, 10 is fairly arbitrary here
        letters.append(letter)
    return points

def _sort_by_score(words):
    word_dict = dict()
    for word in words:
        word_dict[word] = _get_word_points(word)

    sorted_word_dict = sorted(word_dict.items(), key=lambda item: item[1], reverse=True)
    sorted_word_arr = []
    for word in sorted_word_dict:
        sorted_word_arr.append(word[0])

    return sorted_word_arr

# length of the string should equal the length of items in a set after splitting word into letters and adding to set
def _has_redundancy(guess):
    letters = [letter for letter in guess]
    return len(guess) != len(set(letters))

# INITIAL STATE:
# - matches is empty
# - guesses is empty
# - inclusive is empty (no matches)
# - exclusive is all words
#
# START by making a guess from highest scored words in exclusive
# - find matching letters and add to `matches` dictionary
# - value will be the position of "in position" letters or -1 for out of position letters
# PROCEED by making an EXCLUSIVE GUESS
# - only look for words with NO matching letters to narrow down letters faster
# - e.g. - if letter "R" is matched, then only words without R will be guessed
# AFTER EACH EXCLUSIVE GUESS:
# - all words that have matching letters are added to `inclusive`
# - all words that have matching letters are removed from `exclusive`
# WHEN EXCLUSIVE MATCHES HAVE BEEN EXHAUSTED
# - switch to inclusive guesses

class Data:
    def __init__(self):
        words = self._get_words()

        # all letter matches with letter as key and index as value
        self._matches = dict()

        # only positional matches where value is >= 0
        self._positional = dict()

        # only non-positional matches where value is -1
        self._non_positional = dict()

        # keep track of which letters have been used in guesses
        self._letters_used = []

        # words in the dictionary
        self._words  = words.copy()

        # words that will match against letter matches above irrespective of position
        self._inclusive  = _sort_by_score(words.copy())

        # words that will not match against any letters in matches
        self._exclusive  = _sort_by_score(words.copy())

        # words we have guessed
        self.guesses    = []

    def _used_unmatched_letters(self):
        return list(filter(lambda letter: letter not in self._matches.keys(), self._letters_used))

    # Only way to add a match from the outside
    def add_match(self, letter, position):
        if position > -1 and letter not in self._positional:
            self._positional[letter] = position
            self._matches[letter] = position
        if position == -1 and letter not in self._non_positional:
            self._non_positional[letter] = position
            self._matches[letter] = position

        self._cleanup()

    def _cleanup(self, inclusive = False):
        if inclusive:
            self._cleanup_inclusive()
        else:
            self._cleanup_exclusive()

    def _cleanup_inclusive(self):
        # remove words from inclusive if matched letters ARE NOT in the word
        for letter in self._matches.keys():
            inclusive = self._inclusive.copy()
            for word in inclusive:
                position = self._matches[letter]
                if re.search(letter, word) is None or (position > -1 and word[position] != letter):
                    self._inclusive.remove(word)

        unmatched_letters = self._used_unmatched_letters()
        inclusive = self._inclusive.copy()
        for word in inclusive:
            for letter in word:
                if letter in unmatched_letters:
                    self._inclusive.remove(word)
                    break

    def _cleanup_exclusive(self):
        for letter in self._letters_used:
            # remove words from exclusive if matched letters ARE in the word
            exclusive = self._exclusive.copy()
            for word in exclusive:
                if re.search(letter, word) is not None:
                    self._exclusive.remove(word)

    def _inclusive_guess(self):
        target_count = len(self._matches)
        guess = None
        while guess is None:
            if len(self._inclusive) == 0:
                raise "No Inclusive Matches Left"
            else:
                guess = self._inclusive[0]
#                inclusive = self._inclusive.copy()
#                for word in inclusive:
#                    current_count = 0
#
#                    # First check for any positional matches
#                    for letter in self._positional:
#                        if word[self._positional[letter]] != letter:
#                            self._inclusive.remove(word)
#                            break
#                        else:
#                            current_count += 1
#
#                    # Then check for all non positional matches
#                    for letter in self._non_positional:
#                        if re.search(letter, word) is not None:
#                            current_count += 1
#
#                    print(word + ": current_count: " + str(current_count) + ", target: " + str(target_count))
#                    if current_count >= target_count:
#                        guess = word
#                        break
#                    elif word in self._inclusive:
#                        self._inclusive.remove(word)

        # TODO: this probably goes somewhere else
        if guess in self._inclusive:
            self._inclusive.remove(guess)
        return guess

    def _exclusive_guess(self):
        return self._exclusive[0]

    def next_guess(self):
        guess = None
        inclusive = False
        if len(self._exclusive) > 0:
            guess = self._exclusive_guess()
        if guess is None:
            guess = self._inclusive_guess()
            inclusive = True

        print(("INCLUSIVE" if inclusive else "EXCLUSIVE") + " guess '" + guess + "' for letters matching: " + str(self._matches))

        # Keep track of words and letters guessed
        self.guesses.append(guess)
        for letter in guess:
            if letter not in self._letters_used:
                self._letters_used.append(letter)

        # update the inclusive and exclusive lists
        self._cleanup(inclusive)

        return guess

    def _get_words(self, file=DICTIONARY):
        word_arr = []

        # Open dictionary and save words with correct length
        with open(file, 'r') as words:
            for line in words:
                word = line.strip().upper()
                if len(word) == LENGTH:
                    word_arr.append(word)

        return word_arr

class Solution:
    def __init__(self, guesses):
        self.word = guesses[-1]
        self.guess_count = len(guesses)
        self.guesses = guesses

class Solver:
    def __init__(self, target):
        self.target = target
        self.data = Data()
        self.guesses = []
        self._is_solved = False

    def _process_guess(self, guess):

        index = 0
        for letter in guess:
            result = re.search(letter, self.target)

            # if the letter is a match
            if result is not None:
                position = result.span()[0]

                # letter is in correct position
                if position == index:
                    self.data.add_match(letter, position)

                # letter is not in the correct position
                else:
                    self.data.add_match(letter, -1)

            index += 1

    def solve(self):
        guess = self.data.next_guess()
        while not self._is_solved:
            if guess == self.target:
                self._is_solved = True
                break
            else:
                self._process_guess(guess)
                guess = self.data.next_guess()

        return Solution(self.data.guesses)

solution = Solver("STEAM").solve()
print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses: ")
print(solution.guesses)

#count = 0
#with open("wordle-answers.txt", 'r') as words:
#    for word in words:
#        count += 1
#        solution = Solver(word.strip()).solve()
#        print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses: " + str(solution.guesses))
#        if count == 20:
#            raise "DONE"

