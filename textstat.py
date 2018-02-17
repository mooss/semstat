from nltk.tokenize import word_tokenize

# dictionary with Perl-like autovivification feature
from collections import defaultdict


def delimiter_tokenizer(source, word_delimiters='.,?!:/\\_-'):
    """Tokenize the text using characters delimiters.

    Parameters
    ----------
    source : str
        The text to tokenize.

    word_delimiters : str, optional
        The word delimiters.

    Returns
    -------
    out : str
        The text, tokenized according to the delimiters.
    """
    resultbuffer = list()
    strbuffer = list()

    if ' ' in word_delimiters:
        word_delimiters -= ' '

    for char in source:
        if char in word_delimiters:
            resultbuffer.append(''.join(strbuffer))
            resultbuffer.append(char)
            strbuffer = list()
        else:
            strbuffer.append(char)

    if len(strbuffer):
        resultbuffer.append(''.join(strbuffer))

    return ' '.join(resultbuffer)


def frequency_analysis(source, word_separators=set([' ', '\t', '\n'])):
    """Analyses the frequencies of words in text.

    Parameters
    ----------
    source : str
        Text to be analysed.

    word_separators : set of str, optional
        List of *characters* forming the boundaries between words.

    Returns
    -------
    out : dict of str: int
        Individuals words associated with the number of their apparitions in text.
    """
    result = defaultdict(int)
    strbuffer = list()

    for char in source:
        if char in word_separators:
            result[''.join(strbuffer)] += 1
            strbuffer = list()
        else:
            strbuffer.append(char)

    return result


def nltk_frequency_analysis(source):
    """Analyses the frequency of words in text using nltk's word_tokenize

    Parameters
    ----------
    source : str
        Text to be analysed.

    Returns
    -------
    out : dict of str: int
        Individuals words associated with the number of their apparitions in text.
    """
    result = defaultdict(int)
    for word in word_tokenize(source):
        result[word] += 1

    return result


def count_patterns(data, pattern_classifier):
    """Count the occurence of patterns according to a pattern classification function.

    Parameters
    ----------
    data : Container of a
        The data to count.

    pattern_classifier : function(a) -> b
        The function used to classify patterns.

    Returns
    -------
    out : dict of b: int
    """
    result = defaultdict(int)

    for el in data:
        result[pattern_classifier(el)] += 1

    return result


def average(collection, score_function=lambda x: x):
    """Compute the average of a score on a collection.

    Parameters
    ----------
    collection : Container of a
        The container of elements to average.

    score_function : function(a) -> Number, optional
        Function computing the score to average.

    Returns
    -------
    out : float
        The mean of the scores returned by the score function on the elements.
    """
    return sum([score_function(el) for el in collection]) / len(collection)
