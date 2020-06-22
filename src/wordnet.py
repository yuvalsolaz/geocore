import sys,os
from nltk.corpus import wordnet as wn
from googletrans import Translator

translator = Translator()

def flip_words(text):
   words = text.split()
   return ' '.join([word[::-1] if translator.detect(word).lang in ['iw','ar'] else word for word in words])


def flatten(lst):
    if isinstance(lst, list):
        if len(lst) == 0:
            return []
        first, rest = lst[0], lst[1:]
        return flatten(first) + flatten(rest)
    else:
        return [lst]


lang = 'heb'

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(f'usage: python {sys.argv[0]} <word>')
        exit(1)

    print(f'nltk supported langueges: \n {sorted(wn.langs())} \n')

    eword = sys.argv[1]
    ewords = wn.synsets(eword)
    if len(eword) < 1:
        print(f'unrecognized word: {eword}')
        exit(1)

    print(f'found {len(ewords)} english syns for the word {eword}:')

    for ew in ewords:
        name = ew.name()
        lname = wn.synset(ew.name()).lemma_names(lang)
        trans = flip_words(translator.translate(lname, dest="iw")[0].text if len(lname) > 0 else 'unknown')
        definition = ew.definition()
        lex = ew.lexname()
        syns = [wn.synsets(h, lang=lang) for h in lname]
        syns_str = ' '.join([l.name() for l in flatten(syns)])
        print (f'{name} - {lname} - {trans} -  {lex} - {definition} ') # synsets: {syns_str}')





