"""Verse structures of Old Norse poetry"""

from math import floor

from cltk.phonology.syllabify import Syllabifier
from cltk.tokenize.word import tokenize_old_norse_words
from cltk.utils.cltk_logger import logger

__author__ = ["Clément Besnier <clemsciences@aol.com>", ]


class VerseManager:
    """
    * Fornyrðislag
    * Ljóðaháttr
    """
    @staticmethod
    def is_fornyrdhislag(text: str):
        """
        Basic check
        >>> text1 = "Hljóðs bið ek allar\\nhelgar kindir,\\nmeiri ok minni\\nmögu Heimdallar;\\nviltu at ek, Valföðr,\\nvel fyr telja\\nforn spjöll fira,\\nþau er fremst of man."
        >>> text2 = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> VerseManager.is_fornyrdhislag(text1)
        True
        >>> VerseManager.is_fornyrdhislag(text2)
        False

        :param text:
        :return:
        """
        l = [line for line in text.split("\n") if line != ""]
        return len(l) == 8

    @staticmethod
    def is_ljoodhhaattr(text: str):
        """
        Basic check*

        >>> text1 = "Hljóðs bið ek allar\\nhelgar kindir,\\nmeiri ok minni\\nmögu Heimdallar;\\nviltu at ek, Valföðr,\\nvel fyr telja\\nforn spjöll fira,\\nþau er fremst of man."
        >>> text2 = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> VerseManager.is_ljoodhhaattr(text1)
        False
        >>> VerseManager.is_ljoodhhaattr(text2)
        True

        :param text:
        :return:
        """
        l = [line for line in text.split("\n") if line != ""]
        return len(l) == 6


class Fornyrdhislag:
    """
    Fornyrðislag
    """
    def __init__(self):
        self.text = ""
        self.long_lines = []
        self.short_lines = []

    def from_short_lines_text(self, text: str):
        """
        Famous example from Völsupá 1
        >>> text = "Hljóðs bið ek allar\\nhelgar kindir,\\nmeiri ok minni\\nmögu Heimdallar;\\nviltu at ek, Valföðr,\\nvel fyr telja\\nforn spjöll fira,\\nþau er fremst of man."
        >>> fo = Fornyrdhislag()
        >>> fo.from_short_lines_text(text)
        >>> fo.short_lines
        ['Hljóðs bið ek allar', 'helgar kindir,', 'meiri ok minni', 'mögu Heimdallar;', 'viltu at ek, Valföðr,', 'vel fyr telja', 'forn spjöll fira,', 'þau er fremst of man.']
        >>> fo.long_lines
        [['Hljóðs bið ek allar', 'helgar kindir,'], ['meiri ok minni', 'mögu Heimdallar;'], ['viltu at ek, Valföðr,', 'vel fyr telja'], ['forn spjöll fira,', 'þau er fremst of man.']]

        :param text:
        :return:
        """
        self.text = text
        self.short_lines = [line for line in text.split("\n") if line != ""]
        self.long_lines = [self.short_lines[2*i:2*i+2] for i in range(int(floor(len(self.short_lines)/2)))]


class Ljoodhhaatr:
    """
    Ljóðaháttr
    """
    def __init__(self):
        self.text = ""
        self.long_lines = []
        self.short_lines = []

    def from_short_lines_text(self, text: str):
        """
        Famous example from Hávamál 77
        >>> text = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."
        >>> lj = Ljoodhhaatr()
        >>> lj.from_short_lines_text(text)
        >>> lj.short_lines
        ['Deyr fé,', 'deyja frændr,', 'deyr sjalfr it sama,', 'ek veit einn,', 'at aldrei deyr:', 'dómr um dauðan hvern.']
        >>> lj.long_lines
        [['Deyr fé,', 'deyja frændr,'], ['deyr sjalfr it sama,'], ['ek veit einn,', 'at aldrei deyr:'], ['dómr um dauðan hvern.']]

        :param text:
        :return:
        """
        self.text = text
        self.short_lines = [line for line in text.split("\n") if line != ""]
        self.long_lines = [self.short_lines[0:2], [self.short_lines[2]], self.short_lines[3:5], [self.short_lines[5]]]
    
    def syllabify(self):
        """
        >>> lj = Ljoodhhaatr()
        >>> text = "Deyr fé,\\ndeyja frændr,\\ndeyr sjalfr it sama,\\nek veit einn,\\nat aldrei deyr:\\ndómr um dauðan hvern."

        >>> lj.from_short_lines_text(text)
        >>> lj.syllabify()
        >>> lj.syllabified_text

        """
        if len(self.long_lines) == 0:
            logger.error("No text was imported")
            self.syllabified_text = []
        else:
            syllabifier = Syllabifier(language="old_norse", break_geminants=True)
            syllabified_text = []
            for i, line in enumerate(self.long_lines):
                syllabified_text.append([])
                for j, viisuordh in enumerate(line):
                    syllabified_text[i].append([])
                    words = []
                    for word in tokenize_old_norse_words(viisuordh):
                        if word != '':
                            words.append(syllabifier.syllabify(word))
                    syllabified_text[i][j].append(words)
            self.syllabified_text = syllabified_text


