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

import re

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

        def matching(self):
            matching = self.green.copy()
            for letter in self.yellow:
                matching[letter] = [-1]
            return matching

        def used(self):
            return self._used

    def __init__(self):
        self.letters = Data.Letters()

        # words that will match against letter matches above irrespective of position
        self._answer_words = _sort_by_score(_get_words(ANSWER_DICTIONARY), None)

        # words that will not match against any letters in matches
        self._guess_words = _sort_by_score(_get_words(GUESSING_DICTIONARY), _generate_letter_scores(self._answer_words))
        self._pruned_guess_words = _sort_by_score(_get_words(GUESSING_DICTIONARY), _generate_letter_scores(self._answer_words))

        # words we have guessed
        self.guesses = []

    # Only way to add a match from another class
    def hit(self, letter, position):
        self.letters.hit(letter, position)

    def miss(self, letter):
        self.letters.miss(letter)
        answers = self._answer_words.copy()
        for word in answers:
            # Remove all words that have letters we know don't match
            if re.search(letter, word) is not None:
                self._answer_words.remove(word)

    def add_guess(self, guess):
        self.guesses.append(guess)
        if guess in self._pruned_guess_words:
            self._pruned_guess_words.remove(guess)
        if guess in self._answer_words:
            self._answer_words.remove(guess)


    def _prune(self):
        if self.letters.used() == 0:
            return
        self._prune_answer_words()
        self._prune_guess_words()

    def _prune_answer_words(self):
        # remove words from answers if we don't have green letters
        answers = self._answer_words.copy()
        for word in answers:
            dropped_word = False
            if not dropped_word:
                for letter in self.letters.gray:
                    if re.search(letter, word) is not None:
                        self._answer_words.remove(word)
                        dropped_word = True
                        break
            if not dropped_word:
                for letter in self.letters.yellow:
                    if dropped_word:
                        break
                    if re.search(letter, word) is None:
                        self._answer_words.remove(word)
                        dropped_word = True
                        break
            if not dropped_word:
                for letter in self.letters.green.keys():
                    if dropped_word:
                        break
                    for position in self.letters.green[letter]:
                        if word[position] != letter:
                            self._answer_words.remove(word)
                            dropped_word = True
                            break

        self._answer_words = _sort_by_score(self._answer_words, None)

    def _prune_guess_words(self):
        count_answer = len(self._answer_words)
        count_guess = len(self._pruned_guess_words)
        if count_answer > 1 and count_answer > count_guess:
            print("repopulating guesses")
            self._pruned_guess_words = _sort_by_score(self._guess_words, _generate_letter_scores(self._answer_words))
        else:
            # remove words from exclusive if used letters ARE in the word
            guess_words = self._pruned_guess_words.copy()
            for guess in guess_words:
                for letter in self.letters.used():
                    if re.search(letter, guess) is not None:
                        self._pruned_guess_words.remove(guess)
                        break

            # Now sort exclusive guesses based on frequency of remaining words in answers
            self._pruned_guess_words = _sort_by_score(self._pruned_guess_words, _generate_letter_scores(self._answer_words))

    def _next_answer_word(self):
        return self._answer_words[0]

    def _next_guess_word(self):
        return self._pruned_guess_words[0]

    def _should_attempt_answer(self):
        should_attempt_anwser = len(self._pruned_guess_words) == 0 or (len(self._answer_words) < 2 and len(self._pruned_guess_words) > 0)
#        if should_attempt_anwser:
#            print("ATTEMPTING ANSWER")
        return should_attempt_anwser

    def next_guess(self, answer = False):
        self._prune()
        guess = None
        if answer == True or self._should_attempt_answer():
            guess = self._next_answer_word()
            answer = True
        if guess is None:
            guess = self._next_guess_word()

        return guess

    def matches(self, answer = False):
        if answer:
            return self._answer_words
        else:
            return self._pruned_guess_words

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

    def next_guess(self, answer = False):
        return self.data.next_guess(answer)

    def matches(self, answer = False):
        return self.data.matches(answer)

