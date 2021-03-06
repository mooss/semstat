import math
from itertools import chain
from functools import reduce
from collections import Counter, defaultdict

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

def tf_idf(term, termfreq, inversedocfreq, outofcorpusvalue):
    """Term Frequency - Inverse Document Frequency of a term using dictionaries.

    If the term is not in the inverse document frequency dictionary, this function will use the argument outofcorpusvalue.

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
        return outofcorpusvalue
    return termfreq[term] * inversedocfreq[term]

class scorer(object):
    def __init__(self, wordex, sentex, filters,
                 inversedocfreqs, outofcorpusvalue,
                 scorerfunction):
        """All informations needed to compute a score.
        The score is computed using an external custom similarity function which works by accessing to the informations set here.

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
        self.outofcorpusvalue = outofcorpusvalue
        self.scorerfunction = scorerfunction

    def get_score(self, *args):
        return self.scorerfunction(self, *args)

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class comparator(dotdict):
    """Minimalistic class that provides context to compare two questions
    """
    def __init__(self, context, similarity):
        """
        Parameters
        ----------
        context : dict
        
        similarity : function(context, reference, candidate)
            Similarity function that will use the context to determine the similarity between two questions.
        """
        super().__init__(context)
        self.similarity = similarity

    def getscore(self, reference, candidate):
        return self.similarity(self, reference, candidate)
        

def tf_idf_scorer(self, doca, docb):
    """
    Parameters
    ----------
    doca : 

    docb : 

    inversedocfreqs : 

    outofcorpusvalue : 

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
               self.outofcorpusvalue) * len(intersection)# * occurences
        for term, occurences in intersection.items()
    )


def generic_similarity(context, reference, candidate, bagmaker):
    bagref = bagmaker(reference)
    bagcan = bagmaker(candidate)
    termfreq = term_frequencies(bagref + bagcan)
    intersection = bagref & bagcan
    
    similarity = sum(
        tf_idf(term, termfreq, context.inversedocfreqs, context.outofcorpusvalue)
        for term in intersection
    )
    return similarity

def baseline_similarity(context, reference, candidate):
    """Computes the similarity score of two questions, using only bag of words and TF-IDF.

    Parameters
    ----------
    context : Namespace
        Necessary informations accessibles with dot notation.
        
    reference : Container of words
        Document of the reference sentence.

    candidate : Container of words
        Document of the candidate sentence.

    Returns
    -------
    out : float
        The baseline similarity score.
    """
    def bagmaker(doc):
        return Counter(str(word) for word in doc)

    return generic_similarity(context, reference, candidate, bagmaker)

def filters_baseline_similarity(context, reference, candidate):
    """Baseline similarity using filters.

    Parameters
    ----------
    context : Namespace
        Necessary informations accessibles with dot notation.
        
    reference : Container of words
        Document of the reference sentence.

    candidate : Container of words
        Document of the candidate sentence.

    Returns
    -------
    out : float
        The baseline with filters similarity score.
    """
    def makebag(doc):
        return Counter(word.lower()
                       for word in map(str, doc)
                       if all(pred(word) for pred in context.filters))
    
    return generic_similarity(context, reference, candidate, makebag)


def filters_lemmas_similarity(context, reference, candidate):
    """Lemmas similarity using filters.

    Parameters
    ----------
    context : Namespace
        Necessary informations accessibles with dot notation.
        
    reference : Container of words
        Document of the reference sentence.

    candidate : Container of words
        Document of the candidate sentence.

    Returns
    -------
    out : float
        The lemmas similarity score with filters.
    """
    def makebag(doc):
        return Counter(word.lemma_
                       for word in doc
                       if all(pred(str(word)) for pred in context.filters))
    
    return generic_similarity(context, reference, candidate, makebag)


def create_unit_dict(wordex, sentex, filters, doc):
    result = defaultdict(list)
    for unit in sentex(doc):
        if all(flt(str(unit)) for flt in filters):
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
        outofcorpusvalue,
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
            score += tf_idf(el, termfreq, inversedocfreqs, outofcorpusvalue)\
                     * count * entity_weighter(unitsa[el], unitsb[el], weight)
    else:
        for el in intersection:
            score += tf_idf(el, termfreq, inversedocfreqs, outofcorpusvalue)\
                     * len(intersection) * entity_weighter(unitsa[el], unitsb[el], weight)
    return score


def generic_weights_scorer(context, doca, docb, weights_functions):
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
    unitsa = create_unit_dict(context.wordex, lambda x: x, context.filters, doca)
    unitsb = create_unit_dict(context.wordex, lambda x: x, context.filters, docb)

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
        tfidf = tf_idf(el, termfreq, context.inversedocfreqs, context.outofcorpusvalue)
        score += tfidf * coef
    return score
