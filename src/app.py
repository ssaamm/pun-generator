#BEN CODY:
#I made some git mistakes that I want to clear up with Sam in the morning. but
#while I'm thinking about it I want to outline my plan.
#1. I downloaded a pronunciation distance matrix, generated using cmudict and I
#   put it in the 'data' folder. 
#2. I plan to use the distance between phonemes in the levenstein distance
#   calculations. This will make a high score better than a low score.
#3. I plan to use the weights given in cmudict to modify the phoneme distance
#   score used in the levenstein calculations

from flask import Flask, jsonify, request, render_template
from itertools import islice
from functools import lru_cache
import logging

def get_pronounciations() -> dict:
    pronounciations = {}

    with open('data/cmudict', 'r', encoding='latin-1') as f:
        for line in f:
            if line.startswith(';;;'):
                continue

            split = line.strip().split()
            
            sounds = []
            for sound in split[1:]:
                sounds.append([sound[:2], sound[2:]])
            pronounciations[split[0]] = sounds

    return pronounciations

def get_phoneme_distances () -> dict:
    distances = {}
    distance_matrix = []
    with open ('data/wpsm', 'r') as f:
        for line in f:
            if line.startswith('#'):
                print ('SKIPPING ' +  line)
                continue
            split = line.strip().split()
            distance_matrix.append(split)
    phonemes = distance_matrix[0]
    del distance_matrix[0]
    for phoneme in phonemes:
        distances[phoneme] = {}
        for row in distance_matrix:
            for distance in row[1:]:
                distances[phoneme][row[0]] = float(distance)
    return distances
            

def word_to_phonemes(word):
    key = ''.join(c for c in word.upper() if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    try:
        return pronounciations[key]
    except KeyError:
        return None


def lev_dist(s, t, d):
    """ from Wikipedia https://en.wikipedia.org/wiki/Levenshtein_distance#Iterative_with_two_matrix_rows """
    if s == t:
        return 0
    PENALTY = -2

    if len(s) == 0:
        return PENALTY*(len(t))
    if len(t) == 0:
        return PENALTY*(len(s))

    v0 = list(range(len(t) + 1))
    for v in v0:
        v *= PENALTY
    v1 = [None for _ in range(len(t) + 1)]
    
    
    for i in range(len(s)):
        v1[0] = -i + PENALTY

        for j in range(len(t)):
            score = d[s[i][0]][t[j][0]]
            #if len(s[i][1]) > 0 and len(t[j][1]) > 0:
               # score *= (1.1 + abs(int(s[i][1])-int(t[j][1]))*.3)
            v1[j + 1] = max(v1[j] + PENALTY,
                            v0[j + 1] + PENALTY,
                            v0[j] + score)

        for j in range(len(v0)):
            v0[j] = v1[j]

    return v1[len(t)]


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
    puns = get_puns(input_string)
    return jsonify({'puns': puns})


@lru_cache()
def get_puns(input_string, limit=10):
    target = word_to_phonemes(input_string)
    if target is None:
        return []

    d = get_phoneme_distances
    scored_idioms = []

    for idiom in idioms:
        words = idiom.split()
        word_phonemes = [word_to_phonemes(w) for w in words]

        scored_idioms.extend((lev_dist(target, word_phoneme, d) / len(word_phoneme), replace_word(idiom, ndx, input_string))
                             for ndx, word_phoneme in enumerate(word_phonemes)
                             if word_phoneme is not None)

    return [pun for score, pun in islice(sorted(scored_idioms, key=lambda t: t[0]), limit)]

if __name__ == '__main__':
    app.run(debug=True)
