"""

"""

import re

from copy import deepcopy
from dataclasses import dataclass
from typing import List

from boltons.cacheutils import cachedproperty

from cltk.core.data_types import Doc, Process, Word
from cltk.prosody.lat.process import LatinProsody
from cltk.prosody.non import OldNorseProsody
from cltk.stops.processes import StopsProcess

__author__ = ["Clément Besnier <clem@clementbesnier.fr>"]


@dataclass
class ProsodyProcess(Process):
    """General prosody `Process`.
    """
    # verse_separator: List[str] = None
    verse_separators = r"\n"

    @staticmethod
    def compute_verses(doc: Doc) -> List[List[Word]]:
        verse_indices = [i.start() for i in re.finditer(ProsodyProcess.verse_separators, doc.raw)]
        h = 0
        i = 0
        res = []
        while h < len(verse_indices):
            res.append([])
            while i < len(doc.tokens):
                if doc.words[i].index_char_start < verse_indices[h]:
                    res[h].append(doc.words[i])
                    i += 1
                else:
                    break

            h += 1
        return res

    def run(self, input_doc: Doc) -> Doc:
        scanner = self.algorithm

        output_doc = deepcopy(input_doc)
        output_doc.verses = self.compute_verses(output_doc)

        result = []
        for verse in output_doc.verses:
            result.append(scanner(verse))
        output_doc.prosody_result = result
        return output_doc


# class AlliterationProcess(Process):
#     def run(self, input_doc: Doc) -> Doc:
#         scanner = self.algorithm
#
#         output_doc = deepcopy(input_doc)
#
#         return output_doc
#
#
# class SyllableLengthProcess(Process):
#     def run(self, input_doc: Doc) -> Doc:
#         scanner = self.algorithm
#
#         output_doc = deepcopy(input_doc)
#
#         return output_doc
#
#
# class MeterIdentification(Process):
#     def run(self, input_doc: Doc) -> Doc:
#         scanner = self.algorithm
#
#         output_doc = deepcopy(input_doc)
#
#         return output_doc


# class GreekProsodyProcess(ProsodyProcess):
#     """Prosody `Process` for Ancient Greek.
#
#     >>> from cltk.core.data_types import Process, Pipeline
#     >>> from cltk.tokenizers.processes import GreekTokenizationProcess
#     >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
#     >>> from cltk.languages.utils import get_lang
#     >>> from cltk.languages.example_texts import get_example_text
#     >>> from cltk.nlp import NLP
#     >>> pipe = Pipeline(description="A custom Greek pipeline", \
#     processes=[GreekTokenizationProcess, DefaultPunctuationRemovalProcess,\
#     GreekProsodyProcess], language=get_lang("grc"))
#     >>> nlp = NLP(language='grc', custom_pipeline=pipe)
#     >>> text = get_example_text("grc")
#     >>> cltk_doc = nlp(text)
#     >>> [word.phonetic_transcription for word in cltk_doc.words[:5]]
#     ['hó.ti', 'men', 'hy.mệːs', 'ɔ̂ː', 'ɑ́n.dres']
#     """
#
#     description = "The default Greek transcription process"
#
#     @cachedproperty
#     def algorithm(self):
#         return GreekProsody()


class LatinProsodyProcess(ProsodyProcess):
    """Prosody `Process` for Latin.

    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.phonology.processes import LatinPhonologicalTranscriberProcess, LatinSyllabificationProcess
    >>> from cltk.tokenizers.processes import LatinTokenizationProcess
    >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk import NLP
    >>> a_pipeline = Pipeline(description="A custom Latin pipeline", processes=[LatinTokenizationProcess, DefaultPunctuationRemovalProcess, LatinPhonologicalTranscriberProcess, LatinSyllabificationProcess, LatinProsodyProcess], language=get_lang("lat"))
    >>> nlp = NLP(language="lat", custom_pipeline=a_pipeline)
    >>> text = get_example_text("lat")
    >>> cltk_doc = nlp.analyze(text)
    >>> [word.phonetic_transcription for word in cltk_doc.words][:5]
    ['[gaɫlɪ̣ja]', '[ɛst̪]', '[ɔmn̪ɪs]', '[d̪ɪwɪsa]', '[ɪn̪]']
    """

    description = "The default Latin transcription process"

    @cachedproperty
    def algorithm(self):
        return LatinProsody()


# class MiddleHighGermanProsodyProcess(ProsodyProcess):
#     """Prosody `Process` for Middle High German.
#     >>> from cltk.core.data_types import Process, Pipeline
#     >>> from cltk.tokenizers.processes import MiddleHighGermanTokenizationProcess
#     >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
#     >>> from cltk.languages.utils import get_lang
#     >>> from cltk.languages.example_texts import get_example_text
#     >>> from cltk.nlp import NLP
#     >>> pipe = Pipeline(description="A custom Middle High German pipeline", \
#     processes=[MiddleHighGermanTokenizationProcess, DefaultPunctuationRemovalProcess, \
#     MiddleHighGermanProsodyProcess], language=get_lang("gmh"))
#     >>> nlp = NLP(language='gmh', custom_pipeline=pipe)
#     >>> text = get_example_text("gmh")
#     >>> cltk_doc = nlp(text)
#     >>> [word.phonetic_transcription for word in cltk_doc.words[:5]]
#     ['ʊns', 'ɪst', 'ɪn', 'alten', 'mɛren']
#     """
#
#     description = "The default Middle High German transcription process"
#
#     @cachedproperty
#     def algorithm(self):
#         return MiddleHighGermanProsody()


class OldNorseProsodyProcess(ProsodyProcess):
    """Prosody `Process` for Old Norse.

    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers.processes import OldNorseTokenizationProcess
    >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
    >>> from cltk.phonology.processes import OldNorsePhonologicalTranscriberProcess, OldNorseSyllabificationProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Old Norse pipeline", processes=[OldNorseTokenizationProcess, DefaultPunctuationRemovalProcess, OldNorsePhonologicalTranscriberProcess, OldNorseSyllabificationProcess, OldNorseProsodyProcess], language=get_lang("non"))
    >>> nlp = NLP(language='non', custom_pipeline=pipe)
    >>> text = "Hljóðs bið ek allar helgar kindir\\nmeiri ok minni mögu Heimdallar\\nviltu at ek Valföðr vel fyr telja\\nforn spjöll fira þau er fremst of man\\n"
    >>> cltk_doc = nlp(text)
    >>> [word.phonetic_transcription for word in cltk_doc.words[:5]]
    ['hljoːðs', 'bið', 'ɛk', 'alːar', 'hɛlɣar']
    >>> [[(couple[0].string, couple[1].string) for couple in verse] for verse in cltk_doc.prosody_result]
    [[('Hljóðs', 'helgar'), ('ek', 'allar')], [('meiri', 'minni'), ('meiri', 'mögu'), ('minni', 'mögu')], [('viltu', 'Valföðr'), ('viltu', 'vel'), ('at', 'ek'), ('Valföðr', 'vel')], [('forn', 'fira'), ('forn', 'fremst'), ('fira', 'fremst'), ('er', 'of')]]
    """

    description = "The default Old Norse poetry process"

    @cachedproperty
    def algorithm(self):
        return OldNorseProsody()
