import logging
from functools import lru_cache
from itertools import islice

from flask import Flask, jsonify, request, render_template

from data import idioms, pronounciations


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
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

app = Flask(__name__)


@app.route('/')
def index():
    if 'stats' in request.args:
        logger.info(get_puns.cache_info())

    return render_template('index.html')


@app.route('/pun')
def pun():
    input_string = request.args.get('s')
    puns = get_puns(input_string)
    return jsonify({'puns': puns})


@lru_cache()
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
