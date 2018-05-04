#!/usr/bin/env python3
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

def getpredfilename(*args):
    return 'predictions/rapport_' + '_'.join((*args, 'scores.pred'))

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


corpora = {'2016': 'SemEval2016-Task3-CQA-QL-test-input.xml',
           '2017': 'SemEval2017-task3-English-test-input.xml',}

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
    'train_2016_part1.pickle',
    nlp,
    get_semeval_content)

inversedocfreqs = inverse_document_frequencies(
    [[str(tok) for tok in doc]
     for org in traindoctree.values()
     for doc in org.values()]
)
outofcorpusvalue = max(inversedocfreqs.values())

context = {'inversedocfreqs': inversedocfreqs,
           'outofcorpusvalue': outofcorpusvalue}
methodname = 'baseline'
name = 'refnofilter'
caption = 'Scores MAP - méthode de référence'
from plasem_taln import baseline_similarity
similarity = baseline_similarity
for corpus in corpora:
    from plasem_semeval import write_scores_to_file
    from plasem_taln import comparator
    comp = comparator(context, similarity)
    scores = make_score_tree(
        doctrees[corpus],
        comp.getscore
    )
    predfile = getpredfilename(methodname, corpus)
    write_scores_to_file(scores, predfile)

restable = [[corpus,
             getmapscore(getpredfilename(methodname, corpus))]
            for corpus in corpora]

restable.sort(key=lambda x: x[1], reverse=True)
restable.insert(0, ['Corpus', 'Score MAP'])
print('#+NAME:', name)
print('#+CAPTION:', caption)
print(orgmodetable(restable, header=True))
print()
