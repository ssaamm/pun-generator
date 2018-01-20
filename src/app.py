import os
from flask import Flask, jsonify, request, render_template
import flask_ask as fa
from functools import lru_cache
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


def lev_dist(s, t):
    """ from Wikipedia https://en.wikipedia.org/wiki/Levenshtein_distance#Iterative_with_two_matrix_rows """
    if s == t:
        return 0
    if len(s) == 0:
        return len(t)
    if len(t) == 0:
        return len(s)

    v0 = list(range(len(t) + 1))
    v1 = [None for _ in range(len(t) + 1)]

    for i in range(len(s)):
        v1[0] = i + 1

        for j in range(len(t)):
            cost = 0 if s[i] == t[j] else 1
            v1[j + 1] = min(v1[j] + 1,
                            v0[j + 1] + 1,
                            v0[j] + cost)

        for j in range(len(v0)):
            v0[j] = v1[j]

    return v1[len(t)]


def replace_word(sentence, ndx, replacement):
    split = sentence.split()
    if split[ndx].lower() == replacement.lower():
        return None
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
app.config['ASK_APPLICATION_ID'] = os.getenv('ASK_APPLICATION_ID', None)
ask = fa.Ask(app, '/alexa')

logger.info('Loading phoneme data')
pronounciations = get_pronounciations()

logger.info('Loading idioms data')
with open('data/idioms', 'r') as f:
    idioms = [L.strip() for L in f]


@app.route('/')
def index():
    if 'stats' in request.args:
        logger.info(get_puns.cache_info())

    return render_template('index.html')


@app.route('/pun')
def pun():
    input_string = request.args.get('s')
    puns = get_puns(input_string.strip())
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

    scored_idioms.sort(key=lambda score_pun: score_pun[0])
    return [pun for score, pun in scored_idioms if pun is not None][:limit]


@ask.launch
def new_pun():
    welcome = render_template('welcome')
    return fa.question(welcome)


@ask.intent('PunIntent')
def get_pun(word):
    puns = get_puns(word, limit=3)
    if puns:
        return fa.statement(render_template('pun_found', puns=puns, word=word))
    return fa.statement(render_template('sorry', word=word))


@ask.intent('AMAZON.HelpIntent')
def get_help():
    return fa.question(render_template('help'))


@ask.intent('AMAZON.CancelIntent')
@ask.intent('AMAZON.StopIntent')
def stop():
    return fa.statement(render_template('stop'))


@ask.intent('AMAZON.NoIntent')
def re_prompt():
    return fa.question(render_template('re_prompt'))

if __name__ == '__main__':
    app.run(debug=True)
