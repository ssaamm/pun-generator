from flask import Flask, jsonify, request, render_template
from itertools import islice
import logging

def get_pronounciations() -> dict:
    pronounciations = {}

    with open('data/cmudict', 'r', encoding='latin-1') as f:
        for line in f:
            if line.startswith(';;;'):
                continue

            split = line.replace('0', '').replace('1', '').replace('2', '').strip().split()

            pronounciations[split[0]] = split[1:]

    return pronounciations


def word_to_phonemes(word):
    key = ''.join(c for c in word.upper() if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    try:
        return pronounciations[key]
    except KeyError:
        return None


def lev_dist(a, b):
    return _lev_dist(a, b, len(a), len(b))


def _lev_dist(a, b, i, j):
    """ Levenshtein distance equation taken from Wikipedia https://en.wikipedia.org/wiki/Levenshtein_distance """
    if min(i, j) == 0:
        return max(i, j)

    return min(_lev_dist(a, b, i - 1, j) + 1,
               _lev_dist(a, b, i, j - 1) + 1,
               _lev_dist(a, b, i - 1, j - 1) + (0 if a[i - 1] == b[j - 1] else 1))


def replace_word(sentence, ndx, replacement):
    split = sentence.split()
    split[ndx] = replacement
    return ' '.join(split)

logger = logging.getLogger(__name__)
app = Flask(__name__)

logger.info('Loading phoneme data')
pronounciations = get_pronounciations()

logger.info('Loading idioms data')
with open('data/idioms', 'r') as f:
    idioms = [L.strip() for L in f]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pun')
def pun():
    input_string = request.args.get('s')
    puns = get_puns(input_string)
    return jsonify({'puns': puns})


def get_puns(input_string, limit=10):
    target = word_to_phonemes(input_string)
    if target is None:
        return []

    scored_idioms = []

    for idiom in idioms:
        words = idiom.split()
        word_phonemes = [word_to_phonemes(w) for w in words]

        scored_idioms.extend((lev_dist(target, word_phoneme) / len(word_phoneme), replace_word(idiom, ndx, input_string))
                             for ndx, word_phoneme in enumerate(word_phonemes)
                             if word_phoneme is not None)

    return [pun for score, pun in islice(sorted(scored_idioms), limit)]

if __name__ == '__main__':
    app.run(debug=True)
