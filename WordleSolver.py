import re
import functools

LOGGING = False
#DICTIONARY = "/usr/share/dict/words"
GUESSING_DICTIONARY = "./nyt-guesses.txt"
ANSWER_DICTIONARY = "./nyt-answers.txt"
WORD_LENGTH = 5
PENALTY_FOR_LETTER_REDUNDANCY = 0

class LetterFrequency:
    def __init__(self, letter, position):
        self.letter = letter
        self.by_position = {0:0,1:0,2:0,3:0,4:0}
        self.total = 0
        self.by_position[position] = 1

    def add(self, position):
        self.by_position[position] += 1
        self.total += 1

    def __getitem__(self, item):
        return self.by_position[item]

    def __repr__(self):
        return f'{self.letter}:{self.total}:{self.by_position}'

class PositionLetters:
    def __init__(self, letter, position, score):
        self.letter = letter
        self.position = position
        self.score = score

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'{self.letter}:{self.score}'

class Dictionary:
    def __init__(self):
        guesses = self.get_words('nyt-guesses.txt')
        answers = self.get_words('nyt-answers.txt')
        self.frequency = self._generate_letter_frequency(answers)
        self.letters_by_position = self._sort_letters()

        self.all_words = self._sort_by_score(guesses + answers)
        self.exclusive_words = self.all_words.copy()
        self.intersecting_words = self.all_words.copy()
        self.answers = self._sort_by_score(answers)

        self.feedback = LetterFeedback()

    def get_words(self, filename):
        word_arr = []
        with open(filename, 'r') as words:
            for word in words:
                word_arr.append(word.strip().upper())

        return word_arr

    def _generate_letter_frequency(self, target_words):
        frequency = dict()
        for word in target_words:
            for position, letter in enumerate(word):
                if letter not in frequency:
                    frequency[letter] = LetterFrequency(letter, position)
                else:
                    lett = frequency[letter]
                    lett.add(position)
        return frequency

    def _sort_letters(self):
        letters_by_position = dict()
        for i in range(0,WORD_LENGTH):
            letters_by_position[i] = []
            for letter in self.frequency:
                letters_by_position[i].append(PositionLetters(letter, i, self.frequency[letter].by_position[i]))
            letters_by_position[i] = sorted(letters_by_position[i], reverse = True)

        return letters_by_position

    # returns score for word based on each letter in its position (rather than it's frequency overall)
    def _get_word_score(self, word):
        scores = dict()
        for i, letter in enumerate(word):
            this_score = self.frequency[letter][i]
            # Don't give points for duplicate letters
            if letter not in scores or scores[letter] < this_score:
                scores[letter] = this_score
        score = functools.reduce(lambda a, b: a + b, scores.values())
        return score

    def _sort_by_score(self, words):
        word_dict = dict()
        count = 0
        for word in words:
            word_dict[word] = self._get_word_score(word)
#            if count == 100:
#                break
            count += 1

        sorted_word_dict = sorted(word_dict.items(), key = lambda item: item[1], reverse = True)
        sorted_word_arr = list(map(lambda x: x[0], sorted_word_dict))
        return sorted_word_arr

    def words_for_open_positions(self):
        print("HERE")

    def register_guess(self, guess):
        print("GUESS: " + guess)
        if guess in self.answers:
            self.answers.remove(guess)
        if guess in self.all_words:
            self.all_words.remove(guess)
        if guess in self.exclusive_words:
            self.exclusive_words.remove(guess)

    def _update(self):
        if self.feedback.used() == 0:
            return
        # always update answers first
        self._update_answers()
        # and then guesses after
        self._update_exclusive_words()
        self._update_intersecting_words()

    def _update_answers(self):
        # remove words from answers if we don't have green letters
        answers = self.answers.copy()
        for word in answers:
            dropped_word = False
            if not dropped_word:
                for letter in self.feedback.gray:
                    if letter in word:
                        self.answers.remove(word)
                        dropped_word = True
                        break
            if not dropped_word:
                for letter in self.feedback.yellow:
                    if dropped_word:
                        break
                    if letter not in word:
                        self.answers.remove(word)
                        dropped_word = True
                        break
            if not dropped_word:
                for letter in self.feedback.green.keys():
                    if dropped_word:
                        break
                    for position in self.feedback.green[letter]:
                        if word[position] != letter:
                            self.answers.remove(word)
                            dropped_word = True
                            break

        self.answers = self._sort_by_score(self.answers)

    def _update_exclusive_words(self):
        guesses = self.exclusive_words.copy()
        for word in guesses:
            for letter in self.feedback.used():
                if letter in word:
                    self.exclusive_words.remove(word)
                    break
        self.exclusive_words = self._sort_by_score(self.exclusive_words)

    def _update_intersecting_guesses(self):
        words = self.all_words.copy()
        free_positions = self.feedback.open_spots
        print("free positions: " + str(self.feedback.open_spots))
        matching = dict()
        for word in words:
#        for i in free_positions:
#            print(self.letters_by_position[i])
        print("===========")

        self.intersecting_guesses = self._sort_by_score(matching)

    def next_guess(self):
        self._update()
        if len(self.answers) > 20:
            guess = self.exclusive_guesses[0]
        elif len(self.answers) > 1:
            guess = self.intersecting_guesses[0]
        else:
            guess = self.answers[0]


        if LOGGING:
            print("Suggesting: " + guess)

        assert(guess is not None)
        return guess

    def __str__(self):
        return f'Dictionary\n{list(map(lambda x: x, words.frequency.values()))}'

    def log(self):
#        print(*list(map(lambda x: x, self.frequency.values())), sep = '\n')
        print(*list(map(lambda x: x, self.letters_by_position.items())), sep = '\n')

class LetterFeedback:
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

        self.open_spots = list(range(0,WORD_LENGTH))

    def hit(self, letter, position):
        self.use(letter)
        if position > -1:
            if letter not in self.green:
                self.green[letter] = []
            if position not in self.green[letter]:
                self.open_spots.remove(position)
                self.green[letter].append(position)
                if letter in self.yellow:
                    self.yellow.remove(letter)
        elif position == -1:
            if letter not in self.yellow:
                self.yellow.add(letter)

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

class Puzzle:
    def __init__(self):
        self.dictionary = Dictionary()
        self.feedback = self.dictionary.feedback

        # words we have guessed
        self.guesses = list()

    # Only way to add a match from another class
    def hit(self, letter, position):
        self.feedback.hit(letter, position)

    def miss(self, letter):
        self.feedback.miss(letter)

    def add_guess(self, guess):
        self.guesses.append(guess)
        self.dictionary.register_guess(guess)

    def next_guess(self):
        return self.dictionary.next_guess()

    def matches(self, answer = False):
        if answer:
            return self.dictionary.answers
        else:
            return self.dictionary.guesses

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
        self.puzzle = Puzzle()
        self.guesses = []
        self._is_solved = False

    def _process_guess(self, guess):
        index = 0
        for letter in guess:
            # This gives us ALL the positions of a matching letter
            results = [_.start() for _ in re.finditer(letter, self.target)]

            # if the letter is a miss
            if len(results) == 0:
                self.puzzle.miss(letter)

            # if the letter is a hit
            else:
                for position in results:
                    # letter is in correct position
                    if position == index:
                        self.puzzle.hit(letter, position)
                    # letter is not in the correct position
                    else:
                        self.puzzle.hit(letter, -1)

            index += 1

    def solve(self):
        guess = self.puzzle.next_guess()
        while not self._is_solved:
            # Keep track of words and letters guessed
            self.puzzle.add_guess(guess)
            if guess == self.target:
                self._is_solved = True
                break
            else:
                self._process_guess(guess)
                guess = self.puzzle.next_guess()

        return Solution(self.puzzle.guesses)

    # The following methods are for the interactive solver
    def hit(self, letter, position = -1):
        self.puzzle.hit(letter.upper(), position-1)

    def miss(self, string):
        for letter in string.upper():
            self.puzzle.miss(letter)

    def guess(self, word):
        self.puzzle.add_guess(word.upper())

    def next_guess(self, answer = False):
        return self.puzzle.next_guess(answer)

    def matches(self, answer = False):
        return self.puzzle.matches(answer)

