import os.path
import math
from itertools import chain
from collections import Counter
from semeval_xml import get_semeval_id, get_related_threads, xmlextract
from semeval_util import save_object, load_object

def make_document_tree(original_questions, model, content_extractor):
    result = {}
    for org in original_questions:
        orgid = get_semeval_id(org)
        result[orgid] = {
            get_semeval_id(rel): model(content_extractor(rel))
            for rel in get_related_threads(org)
        }
        result[orgid]['org'] = model(content_extractor(org))
    return result

def make_or_load_document_tree(xml_source, saved_path, model, content_extractor, verbose=False):
    if os.path.isfile(saved_path):
        if verbose:
            print('Loading document tree from', saved_path)
        result = load_object(saved_path)
        return result
    else:
        if verbose:
            print('Creating document tree. This might take a while...')

        extractor = xmlextract(xml_source)
        result = make_document_tree(
            extractor.get_org_elements(), model, content_extractor)

        if verbose:
            print('Saving document tree to', saved_path)
        save_object(result, saved_path)

        return result

def term_frequencies(bag):
    documentlen = sum(bag.values())
    return {
        term: occurrences / documentlen
        for term, occurrences in bag.items()
    }

def document_frequencies(corpus):
    result = Counter()
    for document in corpus:
        result.update({term for term in document})
    return result


def inverse_document_frequencies(corpus, DF=None):
    if DF == None:
        DF = document_frequencies(corpus)
    return {term: math.log2(len(corpus)/docfreq)
            for term, docfreq in DF.items()}

def tf_idf(term, termfreq, inversedocfreq, out_of_corpus_value):
    """Term Frequency - Inverse Document Frequency of a term using dictionaries.

    If the term is not in the inverse document frequency dictionary, this function will use the argument out_of_corpus_value.

    Parameters
    ----------
    term : str
        The term.

    termfreq : dict
        The term frequencies of the document.

    inversedocfreq : dict
        The inverse document frequencies of the corpus.

    Returns
    -------
    out : float
        The TF-IDF value of the term.
    """
    if term not in termfreq:
        return 0
    if term not in inversedocfreq:
        return out_of_corpus_value

    return termfreq[term] * inversedocfreq[term]

def tf_idf_bow(bag, termfreq, inversedocfreq, out_of_corpus_value):
    return sum(tf_idf(term, termfreq, inversedocfreq, out_of_corpus_value) * occurences
               for term, occurences in bag.items())

def tf_idf_bow_scorer(bag_maker, doca, docb, inversedocfreqs, out_of_corpus_value):
    baga = bag_maker(doca)
    bagb = bag_maker(docb)
    intersection = baga & bagb
    termfreq = term_frequencies(baga + bagb)

    return (sum(tf_idf(term, termfreq, inversedocfreqs, out_of_corpus_value) * occurences
               for term, occurences in intersection.items()) * sum(intersection.values()))
#    return tf_idf_bow(intersection, termfreq, inversedocfreqs, out_of_corpus_value)


# def create_unit_dict(wordex, sentex, filters, doca, docb):
#     for unit in sentex(doca)

# def customizable_scorer(wordex, sentex, filters, doca, docb, inversedocfreqs, out_of_corpus_value):
#     for unit in sentex(doca)

#     score = 0;
#     for term in :
#         if
