"""

"""
from typing import List

from cltk.core import Word
from cltk.prosody.lat.macronizer import Macronizer
from cltk.prosody.lat.scan.verse_scanner import VerseScanner
from cltk.prosody.utils import ProsodyAnalysis


__author__ = ["Clément Besnier <clem@clementbesnier.fr>"]


class LatinProsody:

    def __init__(self):
        self.macronizer = Macronizer("tag_ngram_123_backoff")
        self.verse_scanner = VerseScanner()

    def scan(self, verse: List[Word]):
        result = ProsodyAnalysis()
        result.macronized = []

        result.macronized = self.macronizer.macronize_text([word.string for word in verse]).split(" ")

        # result.scansion

        return result
