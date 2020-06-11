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


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(f'usage: python {sys.argv[0]} <word>')

    eword = sys.argv[1]
    ewords = wn.synsets(eword)
    if len(eword) < 1:
        print(f'unrecognized word: {eword}')
        exit(1)

    print(f'found {len(ewords)} english syns for the word {eword}:')
    print(' '.join([w.name() for w in ewords]))
    print()
    hwords = [wn.synset(ew.name()).lemma_names('heb') for ew in ewords if len(wn.synset(ew.name()).lemma_names('heb')) > 0]
    hwords_str = '/'.join([' '.join(hw) for hw in hwords])
    print(f'hebrew synsets for {eword}: {hwords_str}:')

    print()
    syns = [[wn.synsets(h,lang='heb') for h in  hw] for hw in hwords]
    syns_str = ' '.join([l.name() for l in flatten(syns)])
    print(f'english syns for {hwords_str}:\n {syns_str}')

