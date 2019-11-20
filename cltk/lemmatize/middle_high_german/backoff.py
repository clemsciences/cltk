"""Module for lemmatizing Middle High German
"""

__author__ = ['Clément Besnier <clemsciences@aol.com>', ]
__license__ = 'MIT License. See LICENSE.'

import os
from typing import List

from cltk.lemmatize.backoff import IdentityLemmatizer, DictLemmatizer

from cltk.utils.file_operations import open_pickle


class BackoffMHGLemmatizer:
    """Suggested backoff chain; includes at least on of each
    type of major sequential backoff class from backoff.py
    """

    models_path = os.path.normpath(get_cltk_data_dir() +
                                   '/middle_high_german/model/middle_high_german_models_cltk/lemmata/backoff')

    def __init__(self, train: List[list] = None, seed: int = 3, verbose: bool = False):
        self.models_path = BackoffMHGLemmatizer.models_path

        missing_models_message = "BackoffMHGLemmatizer requires the ```middle_high_german_models_cltk``` " \
                                 "to be in cltk_data. Please load this corpus."
        self.train = train
        self.seed = seed
        self.verbose = verbose

        self.token_to_lemmata = []
        self.lemma_to_tokens = []

        try:
            self.lemma_to_tokens = open_pickle(os.path.join(self.models_path, "lemma_to_tokens.pickle"))
            self.token_to_lemmata = open_pickle(os.path.join(self.models_path, "token_to_lemma.pickle"))
        except FileNotFoundError as err:
            raise type(err)(missing_models_message)

        self._define_lemmatizer()

    def _define_lemmatizer(self):
        # Suggested backoff chain--should be tested for optimal order
        self.backoff0 = None
        self.backoff1 = IdentityLemmatizer(verbose=self.verbose)
        self.backoff2 = DictLemmatizer(lemmas=self.token_to_lemmata, source='ReferenzKorpus Mittelhochdeutsch Lemmata',
                                       backoff=self.backoff1, verbose=self.verbose)
        self.lemmatizer = self.backoff2

    def lemmatize(self, tokens: List[str]):
        lemmas = self.lemmatizer.lemmatize(tokens)
        return lemmas

    def __repr__(self):
        return f'<BackoffMHGLemmatizer v0.1>'
