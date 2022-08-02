import re
import functools
import os

LOGGING = False
#DICTIONARY = "/usr/share/dict/words"
GUESSING_DICTIONARY = "./nyt-guesses.txt"
ANSWER_DICTIONARY = "./nyt-answers.txt"
WORD_LENGTH = 5
PENALTY_FOR_LETTER_REDUNDANCY = 0

def log(string):
    if int(os.getenv('WORDLE_LOGGING')) == 1:
        print(string)

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

        self.word_scores = self._word_scores(guesses + answers, False)
        self.all_words = self._sort_by_score(self.word_scores)
        self.exclusive_words = self.all_words.copy()
        self.answers = self._sort_by_score(self._word_scores(answers))

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

    # returns score for word based on each letter in its position (if by_position = True)
    # Or by its position anywhere in the word
    def _get_word_score(self, word, by_position = True):
        scores = dict()
        if by_position:
            for i, letter in enumerate(word):
                this_score = self.frequency[letter][i]
                # Don't give points for duplicate letters
                # For duplicate letters, give the highest score
                if letter not in scores or scores[letter] < this_score:
                    scores[letter] = this_score
        else:
            for letter in word:
                scores[letter] = self.frequency[letter].total
        score = functools.reduce(lambda a, b: a + b, scores.values())
        return score

    def _word_scores(self, words, by_position = True):
        word_dict = dict()
        count = 0
        for word in words:
            word_dict[word] = self._get_word_score(word, by_position)
            count += 1

        sorted_word_dict = sorted(word_dict.items(), key = lambda item: item[1], reverse = True)
        return sorted_word_dict

    def _sort_by_score(self, scores):
        sorted_word_arr = list(map(lambda x: x[0], scores))
        return sorted_word_arr

    # Get the rank of a single word out of all words
    def rank_of(self, word):
        word = word.upper()
        count = len(self.all_words)
        index = self.all_words.index(word)
        return f'{index}/{count}'

    # Get a score for a single word
    def score_of(self, word):
        word = word.upper()
        found = filter(lambda x: x[1] if x[0] == word else None, self.word_scores)
        return list(found)[0][1]

    # Call this after a guess is actually made
    def register_guess(self, guess):
        log("GUESS: " + guess)
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

#    def _filter_by_feedback(self, words, inclusive = False):
#        known = self.feedback.green_by_spots()
#        grays = ''.join(self.feedback.gray)
#        re_string = ""
#        for i in list(range(0,WORD_LENGTH)):
#            if i in known and inclusive:
#                re_string += known[i]
#            elif len(grays) > 0:
#                re_string += r"[^"
#                re_string += grays
#                re_string += r"]"
#        log("REGEX: " + re_string)
#        return list(filter(lambda x: re.search(re_string, x) is not None, words))

    def _word_should_be_kept(self, word, inclusive = True):
        if inclusive:
            for letter in self.feedback.gray:
                if letter in word:
                    return False
            for letter in self.feedback.green.keys():
                for position in self.feedback.green[letter]:
                    if word[position] != letter:
                        return False
            for letter in self.feedback.yellow:
                if letter not in word:
                    return False
        else:
            for letter in self.feedback.used():
                if letter in word:
                    return False

        return True

    def _update_answers(self):
        self.answers = list(filter(self._word_should_be_kept, self.answers))

    def _update_exclusive_words(self):
        self.exclusive_words = list(filter(lambda word: self._word_should_be_kept(word, False), self.exclusive_words))

    def intersecting_word(self):
        log(self.answers)
        available_letters = set((letter for letter in ''.join(self.answers)))
        log(f'Letters in Answers: {available_letters}')
        to_target = available_letters - set(self.feedback.matching().keys())
        log(f'Target: {to_target}')
        log(self.feedback)
        count = len(available_letters)
        if len(to_target) == 0:
            return None

        words = self.all_words.copy()
        pruned = words.copy()
        for word in words:
            has_a_target_letter = False
            for letter in to_target:
                if letter in word:
                    has_a_target_letter = True
                    break
            if not has_a_target_letter:
                pruned.remove(word)

        if len(pruned) == 0:
            return None
        best_word = pruned[0]
        best_length = 0
        for word in pruned:
            length = 0
            for letter in to_target:
                if letter in word:
                    length += 1
            if length > best_length:
                best_length = length
                best_word = word

        log(f'INTERSECTING: {best_word}')
        return best_word

    def next_guess(self):
        self._update()
        log(f'Answers: {len(self.answers)}, Exclusive: {len(self.exclusive_words)}')
        guess = None
        if len(self.answers) > 100 and len(self.exclusive_words) > 0:
            log("EXCLUSIVE")
            guess = self.exclusive_words[0]
        elif len(self.answers) > 3:
            guess = self.intersecting_word()

        if guess is None:
            guess = self.answers[0]

        assert(guess is not None)
        return guess

    def __str__(self):
        return f'Dictionary\n{list(map(lambda x: x, words.frequency.values()))}'

    def log(self):
        log(*list(map(lambda x: x, self.letters_by_position.items())), sep = '\n')

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

    def green_by_spots(self):
        spots = dict()
        if len(self.green) == 0:
            return spots
        for letter in self.green.keys():
            for position in self.green[letter]:
                spots[position] = letter
        return spots

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

    def __str__(self):
        return f'Green: {list(self.green.keys())}, Yellow: {self.yellow}, Used: {self.used()}, Unused: {self.unused()}'

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

    def guess(self, word, in_place, out_of_place):
        out_of_place = out_of_place.upper() if out_of_place else ""
        in_place = in_place.upper() if in_place else ""
        word = word.upper()
        self.puzzle.add_guess(word)
        unused = set([letter for letter in word])
        for index, letter in enumerate(in_place):
            if letter != "_":
                self.puzzle.hit(letter, index)
                unused.remove(letter)
        for letter in out_of_place:
            self.puzzle.hit(letter, -1)
            unused.remove(letter)
        for letter in unused:
            self.puzzle.miss(letter)

    def next_guess(self):
        return self.puzzle.next_guess()

    def matches(self, answer = False):
        return self.puzzle.matches(answer)

