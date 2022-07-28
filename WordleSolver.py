#!/Library/Frameworks/Python.framework/Versions/Current/bin/python3
import re

#DICTIONARY = "/usr/share/dict/words"
DICTIONARY = "./wordle-dictionary.txt"
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
    class Letters:
        def __init__(self):
            # These are for letters in known position
            self.green  = dict()

            # letters in the word but in the wrong position
            self.yellow = set()

            # letters not in the word
            self.gray   = set()

            # letters used in guesses
            self._used   = set()

            self.letter_count = 0

            self._unused = set([letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"])

        def hit(self, letter, position):
            self.use(letter)
            if position > -1:
                if letter not in self.green:
                    self.green[letter] = []
                if position not in self.green[letter]:
                    self.green[letter].append(position)
                    if letter in self.yellow:
                        self.yellow.remove(letter)
                    else:
                        self.letter_count += 1
            elif position == -1:
                self.yellow.add(letter)
                self.letter_count += 1

        def miss(self, letter):
            self.gray.add(letter)
            self.use(letter)

        def use(self, letter):
            self._used.add(letter)
            if letter in self._unused:
                self._unused.remove(letter)

        def matching(self):
            return self.yellow.union(set(self.green.keys()))

        # returns a unique list of letters found in word list
        def letters_found_in(self, word_list):
            letters = set()
            for word in word_list:
                for letter in word:
                    letters.add(letter)
            return letters

        # first and second must be sets
        def letters_in_common(self, first, second):
            common = first.intersection(second)
            return common

        def used(self):
            return self._used

        def unused(self):
            return self._unused

    def __init__(self):
        self.letters = Data.Letters()
        words = self._get_words()

        # words in the dictionary
        self._words = words.copy()

        # words that will match against letter matches above irrespective of position
        self._inclusive = _sort_by_score(words.copy())

        # words that will not match against any letters in matches
        self._exclusive = _sort_by_score(words.copy())

        # words we have guessed
        self.guesses = []

    # Only way to add a match from another class
    def hit(self, letter, position):
        self.letters.hit(letter, position)
        self._prune(False)
        self._prune(True)

    def miss(self, letter):
        self.letters.miss(letter)
        self._prune()
        inclusive = self._inclusive.copy()
        for word in inclusive:
            # Remove all words that have letters we know don't match
            if re.search(letter, word) is not None:
                self._inclusive.remove(word)

    def add_guess(self, guess):
        self.guesses.append(guess)
        if guess in self._exclusive:
            self._exclusive.remove(guess)
        if guess in self._inclusive:
            self._inclusive.remove(guess)


    def _prune(self, inclusive = False):
        if inclusive:
            self._prune_inclusive()
        else:
            self._prune_exclusive()

    def _prune_inclusive(self):
        # remove words from inclusive if we don't have green letters
        inclusive = self._inclusive.copy()
        for word in inclusive:
            dropped_word = False
            if not dropped_word:
                for letter in self.letters.gray:
                    if re.search(letter, word) is not None:
                        self._inclusive.remove(word)
                        dropped_word = True
                        break
            if not dropped_word:
                for letter in self.letters.yellow:
                    if dropped_word:
                        break
                    if re.search(letter, word) is None:
                        self._inclusive.remove(word)
                        dropped_word = True
                        break
            if not dropped_word:
                for letter in self.letters.green.keys():
                    if dropped_word:
                        break
                    for position in self.letters.green[letter]:
                        if word[position] != letter:
                            self._inclusive.remove(word)
                            dropped_word = True
                            break

    def _prune_exclusive(self):
        # remove words from exclusive if used letters ARE in the word
        exclusive = self._exclusive.copy()
        inclusive_letters = self.letters.letters_found_in(self._inclusive)
        unused_letters = self.letters.unused()
        letters_to_discount = unused_letters - inclusive_letters
        print(str(len(self._exclusive)) + "." + str(len(self._inclusive)) + " inc: " + str(inclusive_letters) + ", unused: " + str(unused_letters) + ", discount: " + str(letters_to_discount))

        for word in exclusive:
            is_dropped = False
            for letter in self.letters.used():
                if re.search(letter, word) is not None:
                    self._exclusive.remove(word)
                    is_dropped = True
                    break
            # Remove words from exclusive if used letters are not in inclusive words
            if not is_dropped:
                for letter in letters_to_discount:
                    if re.search(letter, word) is not None:
                        print("DROPPING: " + word)
                        self._exclusive.remove(word)
                        is_dropped = True
                        break


    def _inclusive_guess(self):
        guess = None
        while guess is None:
            if len(self._inclusive) == 0:
                raise "No Inclusive Guesses Left"
            else:
                guess = self._inclusive[0]

        return guess

    def _exclusive_guess(self):
        return self._exclusive[0]

    def _should_use_exclusive(self):
#        print("EXCLUSIVE: " + str(len(self._exclusive)) + ", INCLUSIVE: " + str(len(self._inclusive)))
        return len(self._exclusive) > 0 and len(self.guesses) < 3

    def next_guess(self, inclusive = False):
        guess = None
        if inclusive == False and self._should_use_exclusive():
            guess = self._exclusive_guess()
        if guess is None:
            #print(self._inclusive)
            guess = self._inclusive_guess()
            inclusive = True

        #print(("INCLUSIVE" if inclusive else "EXCLUSIVE") + " guess '" + guess + "' for letters matching: " + str(self.letters.matching()))

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

    def matches(self, inclusive = False):
        if inclusive:
            return self._inclusive
        else:
            return self._exclusive

class Solution:
    def __init__(self, guesses):
        self.word = guesses[-1]
        self.guess_count = len(guesses)
        self.guesses = guesses

class Solver:
    def __init__(self, target = None):
        self.target = target
        self.data = Data()
        self.guesses = []
        self._is_solved = False

    def _process_guess(self, guess):
        index = 0
        for letter in guess:
            # This gives us ALL the positions of a matching letter
            results = [_.start() for _ in re.finditer(letter, self.target)]

            # if the letter is a miss
            if len(results) == 0:
                self.data.miss(letter)

            # if the letter is a hit
            else:
                for position in results:

                    # letter is in correct position
                    if position == index:
                        self.data.hit(letter, position)

                    # letter is not in the correct position
                    else:
                        self.data.hit(letter, -1)

            index += 1


    def solve(self):
        guess = self.data.next_guess()
        while not self._is_solved:
            # Keep track of words and letters guessed
            self.data.add_guess(guess)
            if guess == self.target:
                self._is_solved = True
                break
            else:
                print("GUESS: " + guess)
                self._process_guess(guess)
                guess = self.data.next_guess()

        return Solution(self.data.guesses)

    def hit(self, letter, position = -1):
        self.data.hit(letter.upper(), position-1)

    def miss(self, string):
        for letter in string.upper():
            self.data.miss(letter)

    def guess(self, word):
        self.data.add_guess(word.upper())

    def next_guess(self, inclusive = False):
        return self.data.next_guess(inclusive)

    def matches(self, inclusive = False):
        return self.data.matches(inclusive)


solution = Solver("ASSET").solve()
print("Solved: " + solution.word + " in " + str(solution.guess_count) + " guesses: ")
print(solution.guesses)

#count = 0
#with open("wordle-answers.txt", 'r') as words:
#    for word in words:
#        if count < 100:
#            count += 1
#            solution = Solver(word.strip()).solve()
#            print("solved: " + solution.word + " in " + str(solution.guess_count) + " guesses: " + str(solution.guesses))

