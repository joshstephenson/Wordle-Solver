import re
import functools
import os

LOGGING = False
#DICTIONARY = "/usr/share/dict/words"
GUESSING_DICTIONARY = "./nyt-guesses.txt"
ANSWER_DICTIONARY = "./nyt-answers.txt"
WORD_LENGTH = 5

def log(string):
    logging = int(os.getenv('WORDLE_LOGGING')) == 1 if os.getenv('WORDLE_LOGGING') else False
    if logging:
        print(string)

class UnsupportedAnswer(Exception):
    """Used when Solver is initialized with an unsupported word"""
    pass

    def __str__(self):
        return "This word is not a supported answer"

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
        self.guesses = self._sort_by_score(self.word_scores)
        self.answers = self._sort_by_score(self._word_scores(answers))

        self.feedback = LetterFeedback()

    def get_words(self, filename):
        word_arr = []
        with open(filename, 'r') as words:
            for word in words:
                word_arr.append(word.strip().upper())

        return word_arr

    def _generate_letter_frequency(self, target_words):
        """ Returns a dictionary of letters with their corresponding frequencies
        target_words: list of words
        """
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
        """
        Sorts letters by their frequency returning a dictionary with positional indices as the keys
        Values are arrays of PositionLetters which have the letter, index and word letter score
        """
        letters_by_position = dict()
        for i in range(0,WORD_LENGTH):
            letters_by_position[i] = []
            for letter in self.frequency:
                letters_by_position[i].append(PositionLetters(letter, i, self.frequency[letter].by_position[i]))
            letters_by_position[i] = sorted(letters_by_position[i], reverse = True)

        return letters_by_position

    def _get_word_score(self, word, by_position = True):
        """
        Returns score for word
        by_position: if true, then score will be based on letter position
        """
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
        """
        Returns a sorted dictionary of words with word as key and score as value
        words: list of words
        by_position: if True then scores will be based on letter position
        """
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

    def register_guess(self, guess):
        """
        Call this after a guess is actually made. It will make sure guesses are removed from available answers and guess words.
        guess: the word to remove
        """
        log(f'GUESSING: {guess}')
        if guess in self.answers:
            self.answers.remove(guess)
        if guess in self.guesses:
            self.guesses.remove(guess)

    def _update(self):
        # Looping over words is costly, don't do it if we don't need to
        if self.feedback.used() == 0:
            return
        # always update answers first
        self._update_answers()

    def _word_should_be_saved(self, word):
        """
        Used internally to decide whether or not a word should be removed from a given word list
        based on LetterFeedback (greens, yellows, grays and used).
        """
        # Don't save words that have YELLOW letters in YELLOW spots
        for position, letters in self.feedback.yellow.items():
            for letter in letters:
                if letter not in word or word[position] == letter:
                    return False
        # Don't save words that have GRAY letters
        for letter in self.feedback.gray:
            if letter in word:
                return False
        # Don't save words that don't have GREEN letters in GREEN spots
        for position, letter in self.feedback.green.items():
            if word[position] != letter:
                return False

        return True

    def _word_should_be_saved_intersecting(self, word, letter_info):
        for letter in letter_info.keys():
            if letter in word:
                return True
        return False

    def _get_intersecting_score(self, word, info):
        score = 0
        letters_matched = list()
        for letter in word:
            if letter in info and letter not in letters_matched:
                letters_matched.append(letter)
                score += info[letter]
        return score

    def _find_best_intersecting_word(self):
        """
            Find a word that will cut through a small list of answers with many common letters. Assuming we are trying to find the word HOUND, and after guessing SLATE and CRONY the possible answers are:
                BOUND, POUND, FOUND, DOING, MOUND, GOING, WOUND, HOUND, OWING
            Letters in those words:
                O, U, F, N, I, D, B, M, W, G, P, H
            After filtering out letters we have matched already, we are left with:
                U, F, I, D, B, M, W, G, P, H
            This will sort all available guesses by their composition of these letters, favoring first those with the letters that occur the most times in the above answers and then will break ties using the word score of those scores.
            The word with the most of these letters is HUMID which narrows the answer list down to only one word:
                HOUND
"""
        letter_info = self._find_letter_frequency_in_answers()
        options = list(filter(lambda word: self._word_should_be_saved_intersecting(word, letter_info), self.guesses))
        if len(options) == 0:
            return None

        # Creating a list of tuples with (word, word score)
        options = list(map(lambda word: (word, self._get_intersecting_score(word, letter_info)), options))
        options = sorted(options, key = lambda word: word[1], reverse = True)
        log(f'Options: {options[0:20]}')

        # take the top scoring words:
        max_score = max(list(map(lambda score: score[1], options)))
        highest_scoring = list(filter(lambda score: score[1] == max_score, options))
        log(f'Max Score: {highest_scoring}')

        # Sort by word score here, since they are all equally with intersecting score
        highest_scoring = sorted(highest_scoring, key = lambda ws: self._get_word_score(ws[0]), reverse = True)
        word = highest_scoring[0][0]
        log(f'Highest scoring intersecting: {word}')
        return word

    def _find_letter_frequency_in_answers(self):
        """
            Returns a dictionary of the letters in answers along with a score
            for their unique frequency in each word (meaning only 1 point per word)
        """
        letters_guessed = self.feedback.used()
        # Remove duplicate letters from available answers
        # FUZZY => FUZY or because sets don't preserve order
        # FUZZY => YFZU
        words = list(map(lambda word: ''.join(list(set(letter for letter in word))), self.answers))

        letters_in_word = set(letter for letter in ''.join(words))

        # Remove letters already guessed
        letters_targeted = letters_in_word - letters_guessed

        # Then create a dict of letters and their frequency (after making letters distinct)
        # A letter gets +1 for each word it is in
        letter_info = dict(map(lambda letter: (letter, ''.join(words).count(letter)), letters_targeted))

        # Sort them by their frequency
        letter_info = dict(sorted(letter_info.items(), key = lambda item: item[1], reverse = True))
        log(f'Letters: {letter_info}')

        return letter_info

    def intersecting_word(self):
        return self._find_best_intersecting_word()

    def _update_answers(self):
        self.answers = list(filter(self._word_should_be_saved, self.answers))

    def next_guess(self):
        """
        This function starts the pruning process and based on number of answers and exclusive_words remaining,
        returns either an answer or an intersecting word
        """
        self._update()
        log(f'Remaining Answers ({len(self.answers)}): {self.answers}')
        guess = None
        if len(self.answers) < 50 and len(self.answers) > 2:
            guess = self.intersecting_word()
        if guess is None:
            guess = self.answers[0]

        assert(guess is not None)
        return guess

    def is_answer(self, guess):
        """
        This is to ensure we don't try to solve a word that isn't supported in the answer list
        Should only be called before registering any guesses
        """
        self._update()
        return len(self.answers) == 0 and self.answers[0] == guess

    def answer_count(self):
        return len(self.answers)

    def rank_of(self, word):
        """
        Get the rank of a single word out of all words
        """
        word = word.upper()
        count = len(self.guesses)
        index = self.guesses.index(word)+1
        return f'{index}/{count}'

    def score_of(self, word):
        """
        Get the score for a single word: x/(total word count)
        """
        word = word.upper()
        found = filter(lambda x: x[1] if x[0] == word else None, self.word_scores)
        return list(found)[0][1]

    def __str__(self):
        return f'Dictionary\n{list(map(lambda x: x, words.frequency.values()))}'

    def log(self):
        log(*list(map(lambda x: x, self.letters_by_position.items())), sep = '\n')

class LetterFeedback:
    """
    This class keeps track of letters used and whether they were green, yellow or gray
    """
    def __init__(self):
        # These are for letters in known position
        # Key is index, Value is letter
        self.green  = dict()

        # letters in the word but in the wrong position
        # Key is index, value is letter
        self.yellow = dict()

        # letters not in the word
        self.gray   = set()

        # letters used in guesses
        self._used   = set()

        self._unused = set([letter for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"])

    def hit(self, letter, position, is_green):
        self.use(letter)
        if is_green:
            self.green[position] = letter
        else:
            if position not in self.yellow:
                self.yellow[position] = [letter]
            elif letter not in self.yellow[position]: # don't add the same letter twice in the same index
                    self.yellow[position].append(letter)

    def miss(self, letter):
        self.gray.add(letter)
        self.use(letter)

    def use(self, letter):
        self._used.add(letter)
        if letter in self._unused:
            self._unused.remove(letter)

    def used(self):
        return self._used

    def unused(self):
        return self._unused

    def __str__(self):
        gray = ''.join(sorted(self.gray))
        unused = ''.join(sorted(self.unused()))
        greens = ['*' for i in range(0,5)]
        for key in self.green:
            greens[key] = self.green[key]
        greens = ''.join(greens)
        yellows = ['*' for i in range(0,5)]
        for key in self.yellow:
            yellows[key] = [''.join(x) for x in self.yellow[key]]
        yellows = ''.join(yellows)
        return f'--Green: {greens}, Yellow: {yellows}, Gray: {gray}, Unused: {unused}'

class Puzzle:
    def __init__(self):
        self.dictionary = Dictionary()
        self.feedback = self.dictionary.feedback

        # words we have guessed
        self.guesses = list()

    # Only way to add a match from another class
    def hit(self, letter, position, is_green):
        self.feedback.hit(letter, position, is_green)

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

    def is_answer(self, guess):
        return self.dictionary.is_answer(guess)

    def is_supported_answer(self, answer):
        return answer in self.dictionary.answers

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
        if self.target is not None and not self.puzzle.is_supported_answer(self.target):
            raise UnsupportedAnswer()
        self._is_solved = False

    def _process_guess(self, guess):
        for (index, letter) in enumerate(guess):
            if letter in self.target:
                # letter is in correct position (Green)
                if self.target[index] == letter:
                    self.puzzle.hit(letter, index, True)
                # letter is not in the correct position (Yellow)
                else:
                    self.puzzle.hit(letter, index, False)
            else:
                self.puzzle.miss(letter)
        log(self.puzzle.feedback)

    def solve(self, starting_word = "SALET"):
        guess = starting_word if starting_word else self.puzzle.next_guess()
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

    ######################################################
    # The following methods are for the interactive solver
    ######################################################
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
                self.puzzle.hit(letter, index, True)
                if letter in unused:
                    unused.remove(letter)
        for letter in out_of_place:
            self.puzzle.hit(letter, word.index(letter), False)
            if letter in unused:
                unused.remove(letter)
        for letter in unused:
            self.puzzle.miss(letter)

    def answer_count(self):
        return self.puzzle.dictionary.answer_count()

    def next_guess(self):
        guess = self.puzzle.next_guess()
        self._is_solved = self.puzzle.is_answer(guess)
        return guess

    def matches(self, answer = False):
        return self.puzzle.matches(answer)

    def is_solved(self):
        return self._is_solved

    def guesses(self):
        return self.puzzle.guesses
