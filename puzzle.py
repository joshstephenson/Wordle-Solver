LETTER_COUNT = 26
LETTER_A = 65

class Word:
    def __init__(self, word):
        self.word = word
        positions = [0,0,0,0,0]
        for index, letter in enumerate(word):
            shift = ord(letter)-LETTER_A
            positions[index] = 1<<shift
        self.positions = positions

class Puzzle:
    def _get_words(self, filename):
        word_arr = []
        with open(filename, 'r') as words:
            for word in words:
                word_arr.append(word.strip().upper())

        return word_arr

    def __init__(self):
        """
        positions: an array of 5 integers
        -- each integer corresponds to all possible letters in that position of 5 letter words
        -- where the inclusion of each letter is represented by an enabled bit `1`

        The numbers are built from the answers because some letters never appear in certain positions
        -- X is never first, Q is never in position 4 and J, Q, V are never last
        """
        positional = [0,0,0,0,0]
        answers = self._get_words('nyt-answers.txt')
        for answer in answers:
            word = Word(answer)
            for index, pos in enumerate(word.positions):
                positional[index] = positional[index] | pos
        self.positions = positional

    def allows(self, position, letter):
        """
        Takes a char and returns a bool
        True if the position allows that char
        False if not
        """
        pos = self.positions[position]
        shift = ord(letter)-LETTER_A
        mask = 1<<shift
        return pos & mask != 0

    def set_green(self, position, letter):
        """
        Takes a position/index [0-4] and a letter
        disables bits for all other letters
        """
        shift = ord(letter)-LETTER_A
        self.positions[position] = 1<<shift

    def set_yellow(self, position, letter):
        """
        Takes a position/index [0-4] and a letter
        disables only the bit corresponding to letter
        """
        shift = ord(letter)-LETTER_A
        self.positions[position] &= ~(1<<shift)

    def set_gray(self, letter):
        """
        Takes a letter and disables that bit in all letter positions/indices
        """
        shift = ord(letter)-LETTER_A
        for i in range(0,5):
            self.positions[i] &= ~(1<<shift)

