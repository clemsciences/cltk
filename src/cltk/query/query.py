from typing import Union, List

from cltk.core import Doc, Word
from boltons.cacheutils import cachedproperty


class QueryResult:
    def __init__(self, doc: Doc):
        self.matches = []
        self.doc = doc

    def add_match(self, match: Union[Word, List[Word]]):
        self.matches.append(match)


class Query:
    def __init__(self,
                 doc: Doc,
                 word_query: Union[Word, List[Word]]):
        self.doc = doc
        self.word_query = word_query
        self.result = QueryResult(doc)

        if type(word_query) == Word:
            for i, word in enumerate(doc.words):
                if self.__class__.compare_words(word, self.word_query):
                    self.result.add_match(word)

        elif type(word_query) == list:
            doc_size = len(doc.words)
            query_size = len(word_query)
            for i, word in enumerate(doc.words):
                if i + query_size < doc_size:
                    matches = False
                    for j in range(query_size):
                        matches = matches and self.__class__.compare_words(doc.words[i+j], self.word_query[j])
                    if matches:
                        self.result.add_match(doc.words[i: i+query_size])

    @staticmethod
    def compare_words(doc_word: Word, query_word: Word):
        matches = False
        if query_word.pos is not None:
            if doc_word.pos == query_word.pos:
                matches = True
            else:
                return False
        if query_word.lemma is not None:
            if doc_word.lemma == query_word.lemma:
                matches = True
            else:
                return False
        if query_word.string is not None:
            if doc_word.string == query_word.string:
                matches = True
            else:
                return False
        if query_word.phonetic_transcription is not None:
            if doc_word.phonetic_transcription == query_word.phonetic_transcription:
                matches = True
            else:
                return False
        return matches

    @cachedproperty
    def result(self):
        return self.result
