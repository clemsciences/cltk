"""

"""

from cltk.phonology.middle_high_german.transcription import Word, Transcriber

__author__ = ["Clément Besnier <clem@clementbesnier.fr>"]


class MiddleHighGermanTranscription:
    def __init__(self):
        self.transcriber = Transcriber()

    def transcribe(self, word):
        return self.transcriber.transcribe(word, with_squared_brackets=False)

    def __repr__(self):
        return f"<MiddleHighGermanTranscription>"

    def __call__(self, word):
        return self.transcribe(word)


class MiddleHighGermanSyllabifier:
    def __init__(self):
        pass

    def syllabify(self, word):
        return Word(word).syllabify()

    def __repr__(self):
        return f"<MiddleHighGermanSyllabifier>"

    def __call__(self, word):
        return self.syllabify(word)
