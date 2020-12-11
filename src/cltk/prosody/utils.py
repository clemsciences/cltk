"""

"""

from dataclasses import dataclass


__author__ = ["Clément Besnier <clem@clementbesnier.fr>"]


@dataclass
class ProsodyAnalysis:
    alliterations = None
    scansion = None
    n_syllables: int = None
