"""Test for Old Norse"""


import os
import unittest

from cltk.corpus.swadesh import Swadesh
from cltk.phonology.old_norse import transcription as ont
from cltk.stop.old_norse.stops import STOPS_LIST as OLD_NORSE_STOPS
from cltk.tag.pos import POSTag

__author__ = ["Clément Besnier <clemsciences@aol.com>", ]



class TestOldNorse(unittest.testCase):
    """Class for unittest"""
    def test_swadesh_old_norse(self):
        swadesh = Swadesh('old_norse')
        first_word = 'ek'
        match = swadesh.words()[0]
        self.assertEqual(first_word, match)

    def test_old_norse_transcriber(self):
        example_sentence = "Almáttigr guð skapaði í upphafi himin ok jörð ok alla þá hluti, er þeim fylgja, og " \
                           "síðast menn tvá, er ættir eru frá komnar, Adam ok Evu, ok fjölgaðist þeira kynslóð ok " \
                           "dreifðist um heim allan."

        tr = ont.Transcriber()
        transcribed_sentence = tr.main(example_sentence, ont.old_norse_rules)
        target = "[almaːtːiɣr guð skapaði iː upːhavi himin ɔk jœrð ɔk alːa θaː hluti ɛr θɛim fylɣja ɔɣ siːðast mɛnː " \
                 "tvaː ɛr ɛːtːir ɛru fraː kɔmnar adam ɔk ɛvu ɔk fjœlɣaðist θɛira kynsloːð ɔk drɛivðist um hɛim alːan]"
        self.assertEqual(target, transcribed_sentence)

    def test_old_norse_stopwords(self):
        """
        Test filtering Old Norse stopwords
        Sentence extracted from Eiríks saga rauða (http://www.heimskringla.no/wiki/Eir%C3%ADks_saga_rau%C3%B0a)
        """
        sentence = 'Þat var einn morgin, er þeir Karlsefni sá fyrir ofan rjóðrit flekk nökkurn, sem glitraði við þeim'
        lowered = sentence.lower()
        punkt = PunktLanguageVars()
        tokens = punkt.word_tokenize(lowered)
        no_stops = [w for w in tokens if w not in OLD_NORSE_STOPS]
        target_list = ['var', 'einn', 'morgin', ',', 'karlsefni', 'rjóðrit', 'flekk', 'nökkurn', ',', 'glitraði']
        self.assertEqual(no_stops, target_list)

    def test_pos_tnt_tagger_old_norse(self):
        """Test tagging Old Norse POS with TnT tagger."""
        tagger = POSTag('old_norse')
        tagged = tagger.tag_tnt('Hlióðs bið ek allar.')
        print(tagged)
        self.assertTrue(tagged)

    def test_old_norse_word_tokenizer(self):
        text = "Gylfi konungr var maðr vitr ok fjölkunnigr. " \
               "Hann undraðist þat mjök, er ásafólk var svá kunnigt, at allir hlutir gengu at vilja þeira."
        target = ['Gylfi', 'konungr', 'var', 'maðr', 'vitr', 'ok', 'fjölkunnigr', '.', 'Hann', 'undraðist', 'þat',
                  'mjök', ',', 'er', 'ásafólk', 'var', 'svá', 'kunnigt', ',', 'at', 'allir', 'hlutir', 'gengu', 'at',
                  'vilja', 'þeira', '.']
        word_tokenizer = WordTokenizer('old_norse')
        result = word_tokenizer.tokenize(text)
        self.assertTrue(result == target)


if __name__ == '__main__':
    unittest.main()
