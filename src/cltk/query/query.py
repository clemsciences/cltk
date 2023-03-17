from collections import defaultdict
from functools import lru_cache
from typing import Union, List, Dict, Set, Optional

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


class WordMatch:
    def __init__(self, word_ref: Word, word_compare: Word, fuzzy=False, only_attrs=None):
        """
        >>> WordMatch()

        """
        self.w1 = word_ref
        self.w2 = word_compare
        self.fuzzy = fuzzy
        self._only_attrs = only_attrs
        self._check()

    def _check(self):
        """
        >>> m = WordMatch()
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

    @staticmethod
    def are_vectors_similar(self, v1, v2, ) -> bool:
        pass

    def are_strings_similar(self, s1, s2, strict=True) -> bool:
        if strict:
            pass
        return True

    def starts_with(self, ):
        pass

    def ends_with(self):
        pass

    def are_equal(self):
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
    def __init__(self, *args: Word):
        """
        >>> wq = WordQuery(Word(string="E",), Word(string="Ju"))
        >>> wq.values

        """
        self.words: List[Word] = list(args)

    @property
    @lru_cache()
    def values(self) -> defaultdict[str, Word]:
        values: defaultdict = defaultdict(list)
        for w in self.words:
            for key in w.__dict__.keys():
                if w.__dict__[key]:
                    values[key].append(w.__dict__[key])

        return values

    def __add__(self, other):
        """
        >>> wq1 = WordQuery(Word(string="E"))
        >>> wq2 = WordQuery(Word(string="Ju"))
        >>> wq = wq1 + wq2
        >>> wq.words

        >>> wq.values

        """
        if isinstance(other, WordQuery):
            return WordQuery(*(self.words + other.words))
        return None

    def starts_with(self, word: Word, attribute: str, lower=False) -> bool:
        if hasattr(word, attribute):
            value = word.__dict__[attribute]
            if lower:
                value = value.lower()
            if type(value) == str:
                for v in self.values[attribute]:
                    if value.startswith(v):
                        # print(word.__dict__[key], word_query.values[key])
                        return True
        return False

    def ends_with(self, word: Word, attribute: str, lower=False) -> bool:
        if hasattr(word, attribute):
            value = word.__dict__[attribute]
            if lower:
                value = value.lower()
            if type(value) == str:
                for v in self.values[attribute]:
                    if value.endswith(v):
                        # print(word.__dict__[key], word_query.values[key])
                        return True
        return False

    def equals(self, word: Word):
        fields_to_compare = self.values.keys()
        # print(fields_to_compare)
        for key in fields_to_compare:
            if word.__dict__[key] in self.values[key]:
                # print(word.__dict__[key], word_query.values[key])
                yield word

    def is_contained(self, word: Word):
        fields_to_compare = self.values.keys()
        # print(fields_to_compare)
        for key in fields_to_compare:
            if word.__dict__[key] in self.values[key]:
                # print(word.__dict__[key], word_query.values[key])
                yield word


class Query:
    """
    >>> from cltk import NLP
    >>> non_nlp = NLP("non", suppress_banner=True)
    >>> doc = non_nlp.analyze("ek er armr")
    >>> q = Query(doc)
    >>> from cltk.core.data_types import Word
    >>> word_query = WordQuery(Word(string="er"))
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

    def filter(self, word_query: Union[WordQuery, List[WordQuery]]) -> QueryResult:
        """
        >>> from cltk import NLP
        >>> non_nlp = NLP("non", suppress_banner=True)
        >>> doc = non_nlp.analyze("ek er armr")
        >>> q = Query(doc)
        >>> from cltk.core.data_types import Word
        >>> word_query = WordQuery(Word(string="er"))
        >>> r = q.filter(word_query)
        >>> r.total
        1
        >>> r.matches[0].string
        'er'
        >>> r.doc.tokens
        ['ek', 'er', 'armr']


        >>> wq1 = WordQuery(Word(string="er"))
        >>> wq2 = WordQuery(Word(string="armr"))
        >>> r = q.filter([wq1, wq2])

        >>> r.total
        1
        >>> [[w.string for w in m] for m in r.matches]
        [['er', 'armr']]


        """
        result = QueryResult(self.doc)
        if isinstance(word_query, WordQuery):
            for i, word in enumerate(self.doc.words):
                for word_match in word_query.equals(word):
                    result.add_match(word_match)

        elif type(word_query) == list:
            doc_size = len(self.doc.words)
            # print(f"doc size {doc_size}")
            query_size = len(word_query)
            # print(f"query size {query_size}")
            for i, word in enumerate(self.doc.words):
                if i + query_size <= doc_size:
                    matches = True
                    for j in range(query_size):
                        a_match = False
                        # print(i, j, self.doc.words[i+j], word_query[j])
                        # for _ in self._filter_word_query(self.doc.words[i+j], word_query[j]):
                        for _ in word_query[j].equals(self.doc.words[i+j]):
                            a_match = True
                            # print(f"a match!!! {self.doc.words[i+j]} {word_query[j]}")
                        matches = matches and a_match
                        if not matches:
                            break
                    if matches:
                        result.add_match(self.doc.words[i: i+query_size])
        return result

    def _filter_word_query(self, word: Word, word_query: WordQuery):
        return
        # fields_to_compare = word_query.values.keys()
        # # print(fields_to_compare)
        # for key in fields_to_compare:
        #     if word.__dict__[key] in word_query.values[key]:
        #         # print(word.__dict__[key], word_query.values[key])
        #         yield word

    def filter_cooccurrence(self, word_query: Union[List[WordQuery], WordQuery]):
        """
        >>> from cltk import NLP
        >>> non_nlp = NLP("non", suppress_banner=True)
        >>> doc = non_nlp.analyze("ek er armr")
        >>> q = Query(doc)
        >>> from cltk.core.data_types import Word
        >>> word_query = WordQuery(Word(string="er"))
        >>> r = q.filter(word_query)
        >>> r.total
        1
        >>> r.matches[0].string
        'er'
        >>> r.doc.tokens
        ['ek', 'er', 'armr']

        """
        if type(word_query) == list:
            pass
        elif type(word_query) == set:
            pass
        else:
            raise CLTKException("wrong argument")

    @staticmethod
    def are_equal(doc_word: Word, query_word: Word) -> Optional[WordMatch]:
        matches = WordMatch(doc_word, query_word)
        if matches.ends_with():
            return matches
        return None

    @cachedproperty
    def result(self):
        return self.result

    def starts_with(self, word_query: WordQuery, attribute: str, returns_bool=True, lower=False) -> Union[bool, QueryResult]:
        """
        >>> from cltk import NLP
        >>> non_nlp = NLP("non", suppress_banner=True)
        >>> doc = non_nlp.analyze("ek er armr")
        >>> q = Query(doc)
        >>> from cltk.core.data_types import Word
        >>> w = Word(string="ar")
        >>> word_query = WordQuery(w)
        >>> q.starts_with(word_query, 'string')
        True
        >>> wq2 = WordQuery(Word(string='ke'))
        >>> q.starts_with(wq2, 'string')
        False

        """
        result = QueryResult(self.doc)
        for i, word in enumerate(self.doc.words):
            if word_query.starts_with(word, attribute, lower):
                result.add_match(word)
        if returns_bool:
            return len(result.matches) > 0
        else:
            return result

    def ends_with(self, word_query: WordQuery, attribute: str, returns_bool=True) -> Union[bool, QueryResult]:
        """
        >>> from cltk import NLP
        >>> non_nlp = NLP("non", suppress_banner=True)
        >>> doc = non_nlp.analyze("ek er armr")
        >>> q = Query(doc)
        >>> from cltk.core.data_types import Word
        >>> w = Word(string="mr")
        >>> word_query = WordQuery(w)
        >>> q.ends_with(word_query, 'string')
        True
        >>> q.ends_with(WordQuery(Word(string="ir")), attribute="string")
        False

        """
        result = QueryResult(self.doc)
        for i, word in enumerate(self.doc.words):
            if word_query.ends_with(word, attribute):
                result.add_match(word)
        if returns_bool:
            return len(result.matches) > 0
        else:
            return result

    def __contains__(self, word_query: WordQuery) -> bool:
        """
        >>> from cltk import NLP
        >>> non_nlp = NLP("non", suppress_banner=True)
        >>> doc = non_nlp.analyze("ek er armr")
        >>> q = Query(doc)
        >>> from cltk.core.data_types import Word
        >>> w = Word(string="rm")
        >>> word_query = WordQuery(w)
        >>> word_query in q

        """
        return self.contains(word_query, returns_bool=True)

    def contains(self, word_query: WordQuery, returns_bool=True) -> Union[bool, QueryResult]:
        """
        >>> from cltk import NLP
        >>> non_nlp = NLP("non", suppress_banner=True)
        >>> doc = non_nlp.analyze("ek er armr")
        >>> q = Query(doc)
        >>> from cltk.core.data_types import Word
        >>> w = Word(string="er")
        >>> word_query = WordQuery(w)
        >>> q.contains(word_query)

        """
        result = QueryResult(self.doc)
        for i, word in enumerate(self.doc.words):
            if word_query.is_contained(word):
                result.add_match(word)
        if returns_bool:
            return len(result.matches) > 0
        return result
