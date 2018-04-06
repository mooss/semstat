#!/usr/bin/env python3
from itertools import product, combinations
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from semeval_struct import *
from semeval_util import *
from semeval_xml import get_semeval_content
from semeval_taln import *

def compute_relqs_scores(orgqnode, scorer):
    return {relid: scorer(orgqnode['org'], orgqnode[relid])
            for relid in orgqnode.keys() - {'org'}}

def make_score_tree(document_tree, scorer):
    return transformtree(
        lambda x: compute_relqs_scores(x, scorer),
        document_tree,
        0
    )

def write_scores_to_file(scores, filename):
    """Write a semeval score tree to a prediction file.

    Parameters
    ----------
    scores : dict of dict of float
        The scores to write.

    filename : str
       The name of the output file.
    """
    linebuffer = [(orgid, relid, str(0), str(score), 'true')
                  for orgid, relqs in scores.items()
                  for relid, score in relqs.items()]

    linebuffer.sort(key=lambda x: natural_sort_key(x[1]))

    with open(filename, 'w') as out:
        out.write('\n'.join(['\t'.join(el) for el in linebuffer]))

models = {
    'spacy_en': spacy.load('en')
}

corpuses = {
    '2016': 'SemEval2016-Task3-CQA-QL-test-input.xml',
    '2017': 'SemEval2017-task3-English-test-input.xml',
}

extractors = {
    'questions': lambda x: get_semeval_content(x).lower(),
   # 'questions_with_comments': get_semeval_content_with_relcomments
}

def isnotstopword(word):
    return word not in STOP_WORDS

filters = {
    'gtr2': lambda word: len(word) > 2,
    'nostopwords': isnotstopword,
    'nofilter': lambda x: True,
}

def extracttext(tok):
    return tok.text

def extractlemma(tok):
    return tok.lemma_

def extractlabel(ent):
    return ent.label_ if hasattr(ent, 'label_') else None

def getentities(doc):
    return doc.ents

wordextractors = {
    'text': extracttext,
    'lemma': extractlemma,
    'label': extractlabel,
}

sentenceextractors = {
    'entities': getentities,
    'document': lambda x: x,
}

bowmakers = {
    'named_entities_text': ('text', 'entities'),
    'named_entities_label': ('label', 'entities'),
    'tokens': ('text', 'document'),
    'lemmas': ('lemma', 'document'),
}

def getbowmakerfunctions(key):
    return (wordextractors[bowmakers[key][0]], sentenceextractors[bowmakers[key][1]])

def createbowmaker(wordextractor, sentenceextractor, filters):
    def bowmaker(document):
        return Counter(
            list(filter(lambda x: all(f(x) for f in filters),
                   map(wordextractor, sentenceextractor(document))))
            )

    return bowmaker

training_file = 'SemEval2016-Task3-CQA-QL-train-part1.xml'

training_doctree = make_or_load_document_tree(
    training_file,
    'train_2016_part1.pickle',
    models['spacy_en'],
    get_semeval_content,
    verbose=True
)

doctrees = {
    '_'.join((model, corpus, extractor)): make_or_load_document_tree(
        corpuses[corpus],
        '_'.join((model, corpus, extractor) )+ '.pickle',
        models[model],
        extractors[extractor],
        verbose=True
    )
    for model, corpus, extractor in product(models, corpuses, extractors)
}

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

filters_partition = list(nonemptypartitions(set(filters) - {'nofilter'}))

filters_partition.append(('nofilter',))

approches = list(product(doctrees, bowmakers, filters_partition))

def getpredfilename(doctree, bowmaker, filterspartition):
    return '_'.join((doctree, bowmaker, *filterspartition, 'scores.pred'))


# inversedocfreqs = transformtree(
#     lambda wordextractor: inverse_document_frequencies(
#         [[wordextractor(tok) for tok in doc]
#          for org in training_doctree.values()
#          for doc in org.values()]
#     ),
#     wordextractors
# )

inversedocfreqs = {
    wordex + '_' + sentex: inverse_document_frequencies(
        [[wordextractors[wordex](tok) for tok in sentenceextractors[sentex](doc)]
         for org in training_doctree.values()
         for doc in org.values()]
    )
    for wordex, sentex in bowmakers.values()
}

out_of_corpus_value = max(inversedocfreqs['text_document'].values())

for doctree, bowmaker, filterspartition in approches:
    wordex, sentex = bowmakers[bowmaker]
    bowmakerfunc = createbowmaker(wordextractors[wordex], sentenceextractors[sentex],
                                  [filters[filterkey] for filterkey in filterspartition])

    scores = make_score_tree(
        doctrees[doctree],
        lambda a, b: tf_idf_bow_scorer(
            bowmakerfunc, a, b,
            inversedocfreqs[wordex + '_' + sentex], out_of_corpus_value)
    )

    prediction_file = getpredfilename(doctree, bowmaker, filterspartition)
    print('writing scores to', prediction_file)
    write_scores_to_file(scores, prediction_file)