"""
Sonority hierarchy for Old Norse
"""

__author__ = ["Clément Besnier <clemsicences@aol.com>", ]
__license__ = "MIT License"

# Used according to sonority principle
hierarchy = [
    ["a", "á", "æ", "e", "é", "i", "í", "o", "ǫ", "ø", "ö", "œ", "ó", "u", "ú", "y", "ý"],
    ["j"],
    ["m"],
    ["n"],
    ["p", "b", "d", "g", "t", "k"],
    ["c", "f", "s", "h", "v", "x", "z", "þ", "ð"],
    ["r"],
    ["l"]
]

VOWELS = ["a", "e", "i", "o", "ǫ", "ö", "ø", "u", "y", "á", "æ", "œ", "é", "í", "ó", "ú", "ý"]
LONG_VOWELS = ["ö", "ø", "á", "æ", "œ", "é", "í", "ó", "ú", "ý"]
SHORT_VOWELS = ["a", "e", "i", "o", "u", "y", "ǫ"]
DIPHTHONGS = ["ey", "au", "ei"]
CONSONANTS = [
    "b",
    "d",
    "f",
    "g",
    "h",
    "j",
    "k",
    "l",
    "m",
    "n",
    "p",
    "r",
    "s",
    "t",
    "v",
    "x",
    "z",
    "þ",
    "ð"]

invalid_onsets = ['lm', "fj", "nm", "rk", "nn", "tt", "ðr"]

# for old_norse_ipa
ipa_vowels = ["a", "ɛ", "i", "ɔ", "ɒ", "ø", "u", "y", "œ", "e", "o", "j"]

ipa_hierarchy = [ipa_vowels, ["r"], ["l"], ["m", "n"], ["f", "v", "θ", "ð", "s", "h"], ["b", "d", "g", "k", "p", "t"]]
