import re

LOGGING = False
#DICTIONARY = "/usr/share/dict/words"
GUESSING_DICTIONARY = "./nyt-guesses.txt"
ANSWER_DICTIONARY = "./nyt-answers.txt"
LENGTH = 5
PENALTY_FOR_LETTER_REDUNDANCY = 0

# generate a score for words based on composition of letters and their frequency in English
# Don't give points to duplicate letters becaues they don't help in guessing
# Perhaps give negative value for duplicate letters
def _get_word_points(word, frequency_dict):
    points = 0
    letters = []
    for letter in word:
        if letter not in letters and letter in frequency_dict:
            points += frequency_dict[letter]
        letters.append(letter)
    return points

def _generate_letter_scores(words):
    frequency = dict()
    for word in words:
        for letter in word:
            if letter not in frequency:
                frequency[letter] = 1
            else:
                frequency[letter] +=1

    letters_by_frequency = dict(sorted(frequency.items(), key = lambda item: item[1], reverse = True))
    return letters_by_frequency

def _sort_by_score(words, frequency):
    if frequency is None:
        frequency = _generate_letter_scores(words)
    word_dict = dict()
    for word in words:
        word_dict[word] = _get_word_points(word, frequency)

    sorted_word_dict = sorted(word_dict.items(), key=lambda item: item[1], reverse=True)
    sorted_word_arr = []
    for word in sorted_word_dict:
        sorted_word_arr.append(word[0])

    return sorted_word_arr

def _get_words(file):
    word_arr = []

    # Open dictionary and save words with correct length
    with open(file, 'r') as words:
        for line in words:
            word = line.strip().upper()
            if len(word) == LENGTH:
                word_arr.append(word)

    return word_arr

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

            self._unused = set([letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"])

            self.letter_count = 0

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
            matching = self.green.copy()
            for letter in self.yellow:
                matching[letter] = [-1]
            return matching

        def used(self):
            return self._used

        def unused(self):
            return self._unused

    class Words:
        def __init__(self):
            self.letters = Data.Letters()
            self._answers = _sort_by_score(_get_words(ANSWER_DICTIONARY), None)
            guesses = self._answers.copy()
            guesses = guesses + _get_words(GUESSING_DICTIONARY)
            self._guesses = _sort_by_score(guesses, _generate_letter_scores(self._answers))

        def register_guess(self, guess):
            if guess in self._answers:
                self._answers.remove(guess)
            if guess in self._guesses:
                self._guesses.remove(guess)

        def _update(self):
            if self.letters.used() == 0:
                return
            # always update answers first
            self._update_answers()
            self._update_guesses()

        def _update_answers(self):
            # remove words from answers if we don't have green letters
            answers = self._answers.copy()
            for word in answers:
                dropped_word = False
                if not dropped_word:
                    for letter in self.letters.gray:
                        if letter in word:
                            self._answers.remove(word)
                            dropped_word = True
                            break
                if not dropped_word:
                    for letter in self.letters.yellow:
                        if dropped_word:
                            break
                        if letter not in word:
                            self._answers.remove(word)
                            dropped_word = True
                            break
                if not dropped_word:
                    for letter in self.letters.green.keys():
                        if dropped_word:
                            break
                        for position in self.letters.green[letter]:
                            if word[position] != letter:
                                self._answers.remove(word)
                                dropped_word = True
                                break

            self._answers = _sort_by_score(self._answers, None)

        def _update_guesses(self):
            # Remove words from guesses if used letters ARE in the word
            guesses = self._guesses.copy()
            for guess in guesses:
                for letter in self.letters.used():
                    if letter in guess:
                        self._guesses.remove(guess)
                        break

            # Now sort exclusive guesses based on frequency of remaining words in answers
            self._guesses = _sort_by_score(self._guesses, _generate_letter_scores(self._answers))

        def next_guess(self):
            self._update()
            guess = None

            if len(self._answers) == 1:
                guess = self._answers[0]
            if guess is None and len(self._guesses) > 0:
                guess = self._guesses[0]
            if guess is None:
                guess = self._answers[0]

            if LOGGING:
                print("Suggesting: " + guess)

            return guess

    def __init__(self):
        self.words = Data.Words()
        self.letters = self.words.letters

        # words we have guessed
        self.guesses = []

    # Only way to add a match from another class
    def hit(self, letter, position):
        self.letters.hit(letter, position)

    def miss(self, letter):
        self.letters.miss(letter)

    def add_guess(self, guess):
        self.guesses.append(guess)
        self.words.register_guess(guess)

    def next_guess(self):
        return self.words.next_guess()

    def matches(self, answer = False):
        if answer:
            return self.words._answers
        else:
            return self.words._guesses

class Solution:
    def __init__(self, guesses):
        self.word = guesses[-1]
        self.guess_count = len(guesses)
        self.guesses = guesses

class Solver:
    def __init__(self, target = None):
        if target is not None:
            self.target = target.upper()
        else:
            self.target = None
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

    def solve(self, starting_word = None):
        guess = (starting_word if starting_word is not None else self.data.next_guess())
        while not self._is_solved:
            # Keep track of words and letters guessed
            self.data.add_guess(guess)
            if guess == self.target:
                self._is_solved = True
                break
            else:
                self._process_guess(guess)
                guess = self.data.next_guess()
            if LOGGING:
                print(self.data.letters.matching())

        return Solution(self.data.guesses)

    # The following methods are for the interactive solver
    def hit(self, letter, position = -1):
        self.data.hit(letter.upper(), position-1)

    def miss(self, string):
        for letter in string.upper():
            self.data.miss(letter)

    def guess(self, word):
        self.data.add_guess(word.upper())

    def next_guess(self, is_start = False):
        return self.data.next_guess(is_start)

    def matches(self, answer = False):
        return self.data.matches(answer)

