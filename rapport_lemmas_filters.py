#!/usr/bin/env python3
from itertools import product
corpora = {'2016': 'SemEval2016-Task3-CQA-QL-test-input.xml',
           '2017': 'SemEval2017-task3-English-test-input.xml',}

relevancy = {'2016': 'scorer/SemEval2016-Task3-CQA-QL-test.xml.subtaskB.relevancy',
             '2017': 'scorer/SemEval2017-Task3-CQA-QL-test.xml.subtaskB.relevancy'}
def wordextractor(tok):
    return tok.lemma_
import subprocess
from plasem_algostruct import transformtree

def compute_relqs_scores(orgqnode, scorer):
    return {relid: scorer(orgqnode['org'], orgqnode[relid])
            for relid in orgqnode.keys() - {'org'}}

def make_score_tree(document_tree, scorer):
    return transformtree(
        lambda x: compute_relqs_scores(x, scorer),
        document_tree,
        0
    )

def getmapscore(predfilename):
    score = subprocess.run(
        ['./extractMAP.sh', predfilename], stdout=subprocess.PIPE)
    return score.stdout.decode('utf-8').strip('\n')

from collections import Iterable
def flatten(*args):
    for el in args:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(*el)
        else:
            yield el

def getpredfilename(*args):
    return 'predictions/rapport_' + '_'.join(flatten(args, 'scores.pred'))

def orgmodetable(matrix, header=False):
    maxlen = [0] * len(matrix[0])
    for line in matrix:
        for i, cell in enumerate(line):
            if len(maxlen) <= i or len(str(cell)) > maxlen[i]:
                maxlen[i] = len(str(cell))

    def orgmodeline(line, fill=' '):
        joinsep = fill + '|' + fill
        return '|' + fill + joinsep.join(
            str(cell) + fill * (mlen - len(str(cell)))
            for cell, mlen in zip(line, maxlen)
        ) + fill + '|'

    result = ''
    if header:
        result = orgmodeline(matrix[0]) + '\n' + \
            orgmodeline(('-') * len(maxlen), fill='-') + '\n'
        matrix = matrix[1:]
    result += '\n'.join(orgmodeline(line) for line in matrix)
    return result


import spacy
from plasem_taln import inverse_document_frequencies
from plasem_semeval import make_or_load_semeval_document_tree
from semeval_xml import get_semeval_content

nlp = spacy.load('en')
doctrees = {
    corpus: make_or_load_semeval_document_tree(
        corpusxml,
        'spacy_en_' + corpus + '_questions.pickle',
        nlp,
        get_semeval_content)
    for corpus, corpusxml in corpora.items()
}

training_file = 'SemEval2016-Task3-CQA-QL-train-part1.xml'
traindoctree = make_or_load_semeval_document_tree(
    training_file,
    'spacy_en_train2016p1_questions.pickle',
    nlp,
    get_semeval_content)

inversedocfreqs = inverse_document_frequencies(
    [[wordextractor(tok) for tok in doc]
     for org in traindoctree.values()
     for doc in org.values()]
)
outofcorpusvalue = max(inversedocfreqs.values())

context = {'inversedocfreqs': inversedocfreqs,
           'outofcorpusvalue': outofcorpusvalue}

MAPPSENT_STOPWORDS = set(open('stopwords_en.txt', 'r').read().splitlines())

def isnotstopword(word):
    return word not in MAPPSENT_STOPWORDS

lenfilters = {
    'gtr1': lambda word: len(word) > 1,
    'gtr2': lambda word: len(word) > 2,
    'gtr3': lambda word: len(word) > 3,
    'gtr4': lambda word: len(word) > 4,
}

nolenfilters = {
    'nostopwords': isnotstopword,
}

filters = {}
filters.update(lenfilters)
filters.update(nolenfilters)
filters.update({ 'nofilter': lambda x: True })

all_filters_descr = {
    'gtr1': '$\leq 1$',
    'gtr2': '$\leq 2$',
    'gtr3': '$\leq 3$',
    'gtr4': '$\leq 4$',
    'nostopwords': 'Mots outils',
    'nofilter': 'Pas de filtre',
}

all_indicators_descr = {
    'named_entities_text': 'Textes des entités nommées',
    'named_entities_label': 'Étiquettes des entités nommées',
    'tokens': 'Tokens',
    'lemmas': 'Lemmes',
}

def get_filters_descr(filters):
    return ', '.join(all_filters_descr[key] for key in filters)

def get_indicator_descr(indicator):
    return all_indicators_descr[indicator]

def get_doctree_descr(doctree):
    return all_doctrees_descr[doctree]

from itertools import combinations
def nonemptypartitions(iterable):
    for i in range(1, len(iterable) + 1):
        for perm in combinations(iterable, i):
            yield perm


def join_predicates(iterable_preds):
    def joinedlocal(element):
        for pred in iterable_preds:
            if not pred(element):
                return False
        return True
    print('joining', *(pred for pred in iterable_preds))
    return joinedlocal


filters_partition = list(nonemptypartitions(nolenfilters))

for len_and_nolen in product(nolenfilters, lenfilters):
    filters_partition.append(len_and_nolen)

for lenfilter in lenfilters:
    filters_partition.append((lenfilter,))

filters_partition.append(('nofilter',))

restable = []

from plasem_taln import filters_lemmas_similarity
similarity = filters_lemmas_similarity

methodname = 'lemmas_filters'
caption = 'Semeval - Scores MAP - Lemmes avec Filtres'

parameters = list(product(corpora, filters_partition))
parameters_description = ('Édition', 'Filtres', 'Score MAP')
description_functions = [lambda x: x, get_filters_descr]
for corpus, *rest in parameters:
    context['filters'] = [filters[key] for key in rest[0]]
    from plasem_semeval import write_scores_to_file
    from plasem_taln import comparator
    
    comp = comparator(context, similarity)
    scores = make_score_tree(
        doctrees[corpus],
        comp.getscore
    )
    predfile = getpredfilename(methodname, corpus, *rest)
    write_scores_to_file(scores, predfile)
    from plasem_semeval import sorted_scores_from_semeval_relevancy
    from plasem_algostruct import mean_average_precision
    
    MAP = mean_average_precision(
        sorted_scores_from_semeval_relevancy(
            relevancy[corpus],
            scores).values()
    )
    
    restable.append([*(description_functions[i](value)
                       for i, value in enumerate((corpus, *rest))),
                     '%.2f' % (100 * MAP)])

restable.sort(key=lambda x: x[-1], reverse=True)
restable.sort(key=lambda x: x[0])
restable.insert(0, parameters_description)

print('#+NAME:', methodname)
print('#+CAPTION:', caption)
print(orgmodetable(restable, header=True))
print()
