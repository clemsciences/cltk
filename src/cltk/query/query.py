from collections import defaultdict
from typing import Union, List, Dict, Set

from cltk.core import Doc, Word, CLTKException
from boltons.cacheutils import cachedproperty


class QueryResults:
    """

    """

    def __init__(self):
        self.matches: Dict[Doc, List[Union[Word, List[Word]]]] = {}

    def __add__(self, other):
        if isinstance(other, QueryResult):
            qrs = QueryResults()
            qrs.matches = self.matches
            qrs.matches[other.doc] = other.matches
            return qrs

        elif isinstance(other, QueryResults):
            qrs = QueryResults()
            qrs.matches.update(self.matches)
            qrs.matches.update(other.matches)
            return qrs
        else:
            raise ValueError()

    @cachedproperty
    def matches(self):
        matches = []
        for key in self.matches:
            matches.extend(self.matches[key])
        return matches

    def __setitem__(self, key: Doc, value: List[Union[Word, List[Word]]]):
        self.matches[key] = value

    def __getitem__(self, item: Doc):
        return self.matches[item]


class Match:
    def __init__(self, w1, w2, fuzzy=False, only_attrs=None):
        """
        >>> Match()

        """
        self.w1 = w1
        self.w2 = w2
        self.fuzzy = fuzzy
        self._only_attrs = only_attrs
        self._check()

    def _check(self):
        """
        >>> m = Match()
        >>> m._check()

        """
        if self._only_attrs:
            attributes_to_check = self._only_attrs
        else:
            attributes_to_check = Word.__dict__.keys()
        # for key in attributes_to_check:
        #     if key == 'pos':
        #     elif key == 'upos':
        #     elif key == 'lemma':
        #     elif key == 'string':
        #     elif key == 'phonetic_transcription':
        #     elif key == 'category':
        #     elif key == 'definition':
        #     elif key == 'dependency_relation':
        #     elif key == 'embedding':
        #     elif key == 'features':
        #     elif key == 'governor':
        #     elif key == 'named_entity':
        #
        #     Word.pos
        #     Word.upos
        #     Word.xpos
        #     Word.lemma
        #     Word.string
        #     Word.phonetic_transcription
        #     Word.category
        #     Word.definition
        #     Word.dependency_relation
        #     Word.embedding
        #     Word.features
        #     Word.governor
        #     Word.named_entity
        #     Word.scansion
        #     Word.stem
        #     Word.stop
        #     Word.syllables

    def compare_embedding(self) -> bool:
        pass


class QueryResult:
    """
    """
    def __init__(self, doc: Doc):
        self.matches = []
        self.doc = doc

    def add_match(self, match: Union[Word, List[Word]]):
        self.matches.append(match)

    @cachedproperty
    def total(self):
        return len(self.matches)

    def __add__(self, other):
        if isinstance(other, QueryResult):
            qrs = QueryResults()
            qrs[self.doc] = self.matches
            qrs[other.doc] = other.matches
            return qrs
        else:
            raise ValueError()


class WordQuery:
    def __init__(self, *args):
        """
        >>> wq = WordQuery(Word(string="E"), Word(string="Ju"))
        >>> wq.words

        """
        self.words = args
        self.values = defaultdict(list)
        for w in self.words:
            for key in w.__dict__().keys():
                self.values[key].append(w.__dict__()[key])


class Query:
    """
    >>> from cltk import NLP
    >>> non_nlp = NLP("non", suppress_banner=True)
    >>> doc = non_nlp.analyze("ek er armr")
    >>> q = Query(doc)
    >>> from cltk.core.data_types import Word
    >>> word_query = Word(string="er")
    >>> r = q.filter(word_query)
    >>> r.total
    1
    >>> r.matches[0].string
    'er'
    >>> r.doc.tokens
    ['ek', 'er', 'armr']

    """

    def __init__(self,
                 doc: Doc):
        self.doc = doc
        self.word_query = None
        self.result = QueryResult(doc)

    def filter(self, word_query: Union[Word, List[Word]]) -> QueryResult:
        self.word_query = word_query
        if type(word_query) == Word:
            for i, word in enumerate(self.doc.words):
                if self.__class__.compare_words(word, self.word_query):
                    self.result.add_match(word)

        elif type(word_query) == list:
            doc_size = len(self.doc.words)
            query_size = len(word_query)
            for i, word in enumerate(self.doc.words):
                if i + query_size < doc_size:
                    matches = False
                    for j in range(query_size):
                        matches = matches and self.__class__.compare_words(self.doc.words[i+j], self.word_query[j])
                    if matches:
                        self.result.add_match(self.doc.words[i: i+query_size])
        return self.result

    def filter_cooccurrence(self, word_query: Union[List[Word], Set[Word]]):
        if type(word_query) == list:
            pass
        elif type(word_query) == set:
            pass
        else:
            raise CLTKException("wrong argument")


    @staticmethod
    def compare_words(doc_word: Word, query_word: Word) -> Match:
        matches = Match(doc_word, query_word)

        return matches

    @cachedproperty
    def result(self):
        return self.result
