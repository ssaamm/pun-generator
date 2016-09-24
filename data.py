from itertools import count
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup


def replace_all(string, values, replace_with=''):
    s = str(string)
    for v in values:
        s = s.replace(v, replace_with)
    return s


def get_idioms_idiomsphrases(html):
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.select('.entry-title')

    for i in elements:
        yield next(i.children).text


bad_vals = [':', '(command)', '(n.)', '(v.)', '(v. and n.)', '(adj.)', '(adj)', '(adj/adv)', '(adv.)', '(noun or adjective)']


def get_idioms_lefg(html):
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.select('.blue')

    for i in elements:
        idioms = i.text.split(';')
        for idiom_text in idioms:
            idiom = replace_all(idiom_text.strip(), values=bad_vals)
            yield idiom


def get_all_idioms():
    yield 'girls just wanna have fun'

    for n in count(1):
        r = requests.get('http://www.idiomsphrases.com/page/{n}/'.format(n=n))
        yield from get_idioms_idiomsphrases(r.text)

        if r.status_code != 200:
            break

    r = requests.get('http://www.learnenglishfeelgood.com/americanidioms/index.html')
    if r.status_code != 200:
        raise Exception('sos {}'.format('a'))
    yield from get_idioms_lefg(r.text)

    for c in 'bcdefghijklmnopqrstuvwxyz':
        r = requests.get('http://www.learnenglishfeelgood.com/americanidioms/american-idioms_{c}.html'.format(c=c))
        if r.status_code != 200:
            raise Exception('sos {}'.format(c))
        yield from get_idioms_lefg(r.text)


def get_pronounciations() -> dict:
    pronounciations = {}

    with urlopen('http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b') as f:
        for unencoded_line in f:
            line = unencoded_line.decode('latin-1')
            if line.startswith(';;;'):
                continue

            split = line.replace('0', '').replace('1', '').replace('2', '').strip().split()

            pronounciations[split[0]] = split[1:]

    return pronounciations

pronounciations = get_pronounciations()
idioms = list(get_all_idioms())
