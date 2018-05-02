import os.path
import math
from itertools import chain
from functools import reduce
from collections import Counter, defaultdict
from semeval_xml import get_semeval_id, get_related_threads, xmlextract
from plasem_algostruct import save_object, load_object

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

class scorer(object):
    def __init__(self, wordex, sentex, filters,
                 inversedocfreqs, out_of_corpus_value,
                 scorerfunction):
        """

        Parameters
        ----------
        wordex : 

        sentex : 

        filters : 

        Returns
        -------
        out : 

        """
        self.wordex = wordex
        self.sentex = sentex
        self.filters = filters
        self.inversedocfreqs = inversedocfreqs
        self.out_of_corpus_value = out_of_corpus_value
        self.scorerfunction = scorerfunction

    def get_score(self, *args):
        return self.scorerfunction(self, *args)

def tf_idf_scorer(self, doca, docb):
    """
    Parameters
    ----------
    doca : 

    docb : 

    inversedocfreqs : 

    out_of_corpus_value : 

    Returns
    -------
    out : 
    """
    def bag_maker(doc):
        return Counter(word
                for word in map(self.wordex, self.sentex(doc))
                if all(flt(word) for flt in self.filters))
    baga = bag_maker(doca)
    bagb = bag_maker(docb)
    intersection = baga & bagb
    termfreq = term_frequencies(baga + bagb)

    return sum(
        tf_idf(term,
               termfreq,
               self.inversedocfreqs,
               self.out_of_corpus_value) * len(intersection)# * occurences
        for term, occurences in intersection.items()
    )

def create_unit_dict(wordex, sentex, filters, doc):
    result = defaultdict(list)
    for unit in sentex(doc):
        if all(flt(wordex(unit)) for flt in filters):
            result[wordex(unit)].append(unit)
    return result


def entity_weighter(unita, unitb, weight):
    entcount = 0
    for tok in chain(unita, unitb):
        if tok.ent_type != 0:
            entcount += 1
    if entcount > 0:
        return weight
    else:
        return 1-weight

def generic_weighter(unita, unitb, weight, predicate):
    for tok in chain(unita, unitb):
        if predicate(tok):
            return weight
    return 1 - weight

def noun_weighter(unita, unitb, weight):
    return generic_weighter(
        unita, unitb, weight,
        lambda x: x.pos_ == 'NOUN'
    )

def adjective_weighter(unita, unitb, weight):
    return generic_weighter(
        unita, unitb, weight,
        lambda x: x.pos_ == 'ADJ'
    )

def verb_weighter(unita, unitb, weight):
    return generic_weighter(
        unita, unitb, weight,
        lambda x: x.pos_ == 'VERB'
    )

def entityweight_scorer(
        wordex, filters,
        doca, docb, inversedocfreqs,
        out_of_corpus_value,
        score_multiplier='interlen',
        weight=0.6):
    unitsa = create_unit_dict(wordex, lambda x: x, filters, doca)
    unitsb = create_unit_dict(wordex, lambda x: x, filters, docb)

    counta = Counter(word for word, occ in unitsa.items() for _ in occ)
    countb = Counter(word for word, occ in unitsb.items() for _ in occ)

    score = 0
    intersection = counta & countb
    termfreq = term_frequencies(counta + countb)

    if score_multiplier == 'interocc':
        for el, count in intersection.items():
            score += tf_idf(el, termfreq, inversedocfreqs, out_of_corpus_value)\
                     * count * entity_weighter(unitsa[el], unitsb[el], weight)
    else:
        for el in intersection:
            score += tf_idf(el, termfreq, inversedocfreqs, out_of_corpus_value)\
                     * len(intersection) * entity_weighter(unitsa[el], unitsb[el], weight)
    return score


def generic_weights_scorer(self, doca, docb, weights_functions):
    """

    Parameters
    ----------
    doca : document

    docb : document

    weights_functions : list(tuple(float, function))
        List of weights and functions to which they apply.

    Returns
    -------
    out : float
        Similarity score of the documents.
    """
    unitsa = create_unit_dict(self.wordex, lambda x: x, self.filters, doca)
    unitsb = create_unit_dict(self.wordex, lambda x: x, self.filters, docb)

    counta = Counter(word for word, occ in unitsa.items() for _ in occ)
    countb = Counter(word for word, occ in unitsb.items() for _ in occ)

    score = 0
    intersection = counta & countb
    termfreq = term_frequencies(counta + countb)

    for el in intersection:
        coef = reduce(lambda x, y: x * y,
                          (weighter(unitsa[el], unitsb[el], weight)
                           for weight, weighter in weights_functions),
                          1)
        tfidf = tf_idf(el, termfreq, self.inversedocfreqs, self.out_of_corpus_value)
        score += tfidf * coef
    return score * len(intersection)