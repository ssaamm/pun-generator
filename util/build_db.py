import logging
import os
from itertools import count
from urllib.request import urlretrieve

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


def write_idioms(filepath):
    with open(filepath, 'w') as f:
        f.writelines(i + '\n' for i in get_all_idioms())


def write_cmudict(filepath):
    urlretrieve('http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b', filepath)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    for filepath, get_file in [('../data/idioms', write_idioms),
                               ('../data/cmudict', write_cmudict)]:
        if not os.path.exists(filepath):
            logging.info('Getting %s', filepath)
            get_file(filepath)
        else:
            logging.info('Already exists %s', filepath)
