"""
Source: Viking Language 1 by Jesse L. Byock
"""

from enum import Enum, auto
from cltk.phonology.utils import Length
__author__ = ["Clément Besnier <clemsciences@aol.com>", ]


class WeakVerbClass(Enum):
    first = auto()
    second = auto()
    third = auto()
    fourth = auto()


class StrongVerbClass(Enum):
    first = auto()
    second = auto()
    third = auto()
    fourth = auto()
    fifth = auto()
    sixth = auto()
    seventh = auto()


def compute_stem(verb_pattern):
    """

    >>> compute_stem()
    >>> compute_stem()
    >>> compute_stem()
    >>> compute_stem()
    >>> compute_stem()
    >>> compute_stem()
    >>> compute_stem()
    >>> compute_stem()

    :param verb_pattern:
    :return:
    """
    if verb_pattern[0][-1] == "a":
        return verb_pattern[0][:-1]
    else:
        return verb_pattern[0]


def recognize_weak_verb_class(verb_pattern):
    """
    Weak verbs are classifed into 4 classes:


    >>> recognize_weak_verb_class(("", "", ""))
    >>> recognize_weak_verb_class(("", "", ""))
    >>> recognize_weak_verb_class(("", "", ""))
    >>> recognize_weak_verb_class(("", "", ""))
    >>> recognize_weak_verb_class(("", "", ""))
    >>> recognize_weak_verb_class(("", "", ""))
    >>> recognize_weak_verb_class(("", "", ""))

    :param verb_pattern:
    :return:
    """
    if type(verb_pattern[0]) != str or len(verb_pattern[0]) == 0:
        raise ValueError
    else:
        infinitive = verb_pattern[0]
        assert type(infinitive) == str

        if infinitive in ["segja", "þegja"]:
            return WeakVerbClass.fourth
        elif infinitive in ["vilja"]:
            return WeakVerbClass.third
        elif infinitive in ["spá", "gera"]:
            return WeakVerbClass.second

    if type(verb_pattern[1]) != str or len(verb_pattern[1]) == 0:
        raise ValueError
    else:
        past_indicative = verb_pattern[1]
        assert type(past_indicative) == str

    if type(verb_pattern[2]) != str or len(verb_pattern[2]) == 0:
        raise ValueError
    else:
        past_participle = verb_pattern[2]
        assert type(past_participle) == str

    if past_indicative.endswith("aða"):
        return WeakVerbClass.first

    elif len(infinitive) >= 2:
        pass
    else:
        stem = compute_stem(verb_pattern)
        if stem.length == Length.short:
            return WeakVerbClass.second
        else:
            return WeakVerbClass.third


def recognize_strong_verb_pattern(verb_pattern):
    """
    Strong verbs are classified into 7 classes:

    >>> recognize_strong_verb_pattern(("", "", ""))
    >>> recognize_strong_verb_pattern(("", "", ""))
    >>> recognize_strong_verb_pattern(("", "", ""))
    >>> recognize_strong_verb_pattern(("", "", ""))
    >>> recognize_strong_verb_pattern(("", "", ""))
    >>> recognize_strong_verb_pattern(("", "", ""))
    >>> recognize_strong_verb_pattern(("", "", ""))

    :param verb_pattern:
    :return:
    """
    if type(verb_pattern[1]) != str or len(verb_pattern[1]) == 0:
        raise ValueError
    else:
        past_indicative = verb_pattern[1]
        assert type(past_indicative) == str

    if type(verb_pattern[2]) != str or len(verb_pattern[2]) == 0:
        raise ValueError
    else:
        past_participle = verb_pattern[2]
        assert type(past_participle) == str

    if type(verb_pattern[1]) != str or len(verb_pattern[1]) == 0:
        raise ValueError
    else:
        past_indicative = verb_pattern[1]
        assert type(past_indicative) == str

    if type(verb_pattern[2]) != str or len(verb_pattern[2]) == 0:
        raise ValueError
    else:
        past_participle = verb_pattern[2]
        assert type(past_participle) == str


def recognize_verb_class(verb_pattern):
    """
    >>> recognize_verb_class(("", "", ""))
    >>> recognize_verb_class(("", "", ""))
    >>> recognize_verb_class(("", "", ""))
    >>> recognize_verb_class(("", "", ""))
    >>> recognize_verb_class(("", "", ""))

    :param verb_pattern:
    :return:
    """
    if len(verb_pattern) == 3:
        recognize_weak_verb_class(verb_pattern)
    elif len(verb_pattern) == 5:
        recognize_strong_verb_pattern(verb_pattern)
    else:
        raise ValueError