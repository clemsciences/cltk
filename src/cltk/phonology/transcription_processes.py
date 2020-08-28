"""

"""


from copy import deepcopy
from dataclasses import dataclass

from boltons.cacheutils import cachedproperty

from cltk.core.data_types import Doc, Process

from cltk.phonology.orthophonology import Orthophonology

from cltk.phonology.non.orthophonology import OldNorsePhonologicalTranscriber

# from cltk.phonology.akk import AkkadianPhonologicalTranscriber
# from cltk.phonology.arabic import ArabicPhonologicalTranscriber
from cltk.phonology.gothic.phonology import GothicTranscription
from cltk.phonology.greek.phonology import GreekTranscription
from cltk.phonology.lat.phonology import LatinTranscription
from cltk.phonology.middle_english.phonology import MiddleEnglishTranscription
from cltk.phonology.middle_high_german.phonology import MiddleHighGermanTranscription
from cltk.phonology.old_english.phonology import OldEnglishTranscription
from cltk.phonology.old_swedish.phonology import OldSwedishTranscription


__author__ = ["Clément Besnier <clem@clementbesnier.fr>"]


@dataclass
class PhonologicalTranscriptionProcess(Process):
    """

    """
    def run(self, input_doc: Doc) -> Doc:
        transcriber = self.algorithm

        output_doc = deepcopy(input_doc)
        for word in output_doc.words:
            word.phonetic_transcription = transcriber(word.string.lower())
        return output_doc


# class AkkadianPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
#     """
#     >>> from cltk.core.data_types import Process, Pipeline
#     >>> from cltk.tokenizers.processes import AkkadianTokenizationProcess
#     >>> from cltk.languages.utils import get_lang
#     >>> from cltk.languages.example_texts import get_example_text
#     >>> from cltk.nlp import NLP
#     >>> pipe = Pipeline(description="A custom Akkadian pipeline", \
#     processes=[AkkadianTokenizationProcess, AkkadianPhonologicalTranscriberProcess], \
#     language=get_lang("akk"))
#     >>> nlp = NLP(language='akk', custom_pipeline=pipe)
#     >>> nlp(get_example_text("akk")).phonetic_transcription
#
#     """
#
#     description = "The default Akkadian transcription process"
#
#     @cachedproperty
#     def algorithm(self):
#         return AkkadianPhonologicalTranscriber()


class ArabicPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
    """
    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers.processes import ArabicTokenizationProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Old Norse pipeline", \
    processes=[ArabicTokenizationProcess, ArabicPhonologicalTranscriberProcess], \
    language=get_lang("arb"))
    >>> nlp = NLP(language='arb', custom_pipeline=pipe)
    >>> text = get_example_text("arb")
    >>> [word.phonetic_transcription for word in nlp(text)]

    """

    description = "The default Arabic transcription process"

    @cachedproperty
    def algorithm(self):
        return ArabicPhonologicalTranscriberProcess()


class GothicPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
    """
    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers.processes import OldNorseTokenizationProcess
    >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Gothic pipeline", \
    processes=[OldNorseTokenizationProcess, DefaultPunctuationRemovalProcess, \
    GothicPhonologicalTranscriberProcess], language=get_lang("got"))
    >>> nlp = NLP(language='got', custom_pipeline=pipe)
    >>> text = get_example_text("got")
    >>> text
    
    >>> [word.phonetic_transcription for word in nlp(text)[:5]]

    """

    description = "The default Gothic transcription process"

    @cachedproperty
    def algorithm(self):
        return GothicTranscription()


class GreekPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
    """
    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers.processes import GreekTokenizationProcess
    >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Greek pipeline", \
    processes=[GreekTokenizationProcess, DefaultPunctuationRemovalProcess,\
    GreekPhonologicalTranscriberProcess], language=get_lang("grc"))
    >>> nlp = NLP(language='grc', custom_pipeline=pipe)
    >>> text = get_example_text("grc")

    >>> [word.string for word in nlp(text)[:5]]

    """

    description = "The default Greek transcription process"

    @cachedproperty
    def algorithm(self):
        return GreekTranscription()


# TODO original algorithm does not work
# class LatinPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
#     """
#     >>> from cltk.core.data_types import Process, Pipeline
#     >>> from cltk.tokenizers.processes import LatinTokenizationProcess
#     >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
#     >>> from cltk.languages.utils import get_lang
#     >>> from cltk.languages.example_texts import get_example_text
#     >>> from cltk.nlp import NLP
#     >>> pipe = Pipeline(description="A custom Latin pipeline", \
#     processes=[LatinTokenizationProcess, DefaultPunctuationRemovalProcess, \
#     LatinPhonologicalTranscriberProcess], language=get_lang("lat"))
#     >>> nlp = NLP(language='lat', custom_pipeline=pipe)
#     >>> text = get_example_text("lat")
#
#     >>> [word.phonetic_transcription for word in nlp(text)[:5]]
#
#     """
#
#     description = "The default Latin transcription process"
#
#     @cachedproperty
#     def algorithm(self):
#         return LatinTranscription()


# class MiddleEnglishPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
#     """
#     >>> from cltk.core.data_types import Process, Pipeline
#     >>> from cltk.tokenizers.processes import MiddleEnglishTokenizationProcess
#     >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
#     >>> from cltk.languages.utils import get_lang
#     >>> from cltk.languages.example_texts import get_example_text
#     >>> from cltk.nlp import NLP
#     >>> pipe = Pipeline(description="A custom Middle English pipeline", \
#     processes=[MiddleEnglishTokenizationProcess, DefaultPunctuationRemovalProcess, \
#     MiddleEnglishPhonologicalTranscriberProcess], language=get_lang("enm"))
#     >>> nlp = NLP(language='enm', custom_pipeline=pipe)
#     >>> text = get_example_text("enm")
#     >>> [word.phonetic_transcription for word in nlp(text)[:5]]
#
#     """
#
#     description = "The default Middle English transcription process"
#
#     @cachedproperty
#     def algorithm(self):
#         return MiddleEnglishTranscription()


class MiddleHighGermanPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
    """
    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers.processes import MiddleHighGermanTokenizationProcess
    >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Middle High German pipeline", \
    processes=[MiddleHighGermanTokenizationProcess, DefaultPunctuationRemovalProcess, \
    MiddleHighGermanPhonologicalTranscriberProcess], language=get_lang("gmh"))
    >>> nlp = NLP(language='gmh', custom_pipeline=pipe)
    >>> text = get_example_text("gmh")
    >>> [word.phonetic_transcription for word in nlp(text)[:5]]
    ['ʊns', 'ɪst', 'ɪn', 'alten', 'mɛren']
    """

    description = "The default Middle High German transcription process"

    @cachedproperty
    def algorithm(self):
        return MiddleHighGermanTranscription()


class OldEnglishPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
    """
    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers.processes import MiddleEnglishTokenizationProcess
    >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Old English pipeline", \
    processes=[MiddleEnglishTokenizationProcess, DefaultPunctuationRemovalProcess, \
    OldEnglishPhonologicalTranscriberProcess], language=get_lang("ang"))
    >>> nlp = NLP(language='ang', custom_pipeline=pipe)
    >>> text = get_example_text("ang")
    >>> [word.phonetic_transcription for word in nlp(text)[:5]]
    ['ʍæt', 'we', 'gɑrˠdenɑ', 'in', 'gæːɑrˠdɑgum']
    """

    description = "The default Old English transcription process"

    @cachedproperty
    def algorithm(self):
        return OldEnglishTranscription()


class OldNorsePhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
    """
    >>> from cltk.core.data_types import Process, Pipeline
    >>> from cltk.tokenizers.processes import OldNorseTokenizationProcess
    >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
    >>> from cltk.languages.utils import get_lang
    >>> from cltk.languages.example_texts import get_example_text
    >>> from cltk.nlp import NLP
    >>> pipe = Pipeline(description="A custom Old Norse pipeline", \
    processes=[OldNorseTokenizationProcess, DefaultPunctuationRemovalProcess, \
    OldNorsePhonologicalTranscriberProcess], language=get_lang("non"))
    >>> nlp = NLP(language='non', custom_pipeline=pipe)
    >>> text = get_example_text("non")
    >>> [word.phonetic_transcription for word in nlp(text)[:5]]
    ['gylvi', 'kɔnunɣr', 'reːð', 'θar', 'lœndum']

    """

    description = "The default Old Norse poetry process"

    @cachedproperty
    def algorithm(self):
        return OldNorsePhonologicalTranscriber()


# class OldSwedishPhonologicalTranscriberProcess(PhonologicalTranscriptionProcess):
#     """
#     >>> from cltk.core.data_types import Process, Pipeline
#     >>> from cltk.tokenizers.processes import OldNorseTokenizationProcess
#     >>> from cltk.filtering.processes import DefaultPunctuationRemovalProcess
#     >>> from cltk.languages.utils import get_lang
#     >>> from cltk.languages.example_texts import get_example_text
#     >>> from cltk.nlp import NLP
#     >>> pipe = Pipeline(description="A custom Old Swedish pipeline", \
#     processes=[OldNorseTokenizationProcess, DefaultPunctuationRemovalProcess, \
#     OldSwedishPhonologicalTranscriberProcess], language=get_lang("non"))
#     >>> nlp = NLP(language='non', custom_pipeline=pipe)
#     >>> nlp(get_example_text("non")).phonetic_transcription
#
#     """
#
#     description = "The default Old Swedish transcription process"
#
#     @cachedproperty
#     def algorithm(self):
#         return OldSwedishTranscription()