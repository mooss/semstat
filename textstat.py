from nltk.tokenize import word_tokenize

from collections import defaultdict # dictionary with Perl-like autovivification feature

def delimiter_tokeniser(source, word_delimiters=set([' ', '\t', '\n']) ):
    """Tokenize the text using characters delimiters.

    Parameters
    ----------
    source : str
        The text to tokenise.
    
    word_delimiters : Container of str, optional
        The word delimiters.
    
    Returns
    -------
    out : list of str
        The text, tokenised according to the delimiters.
    """
    result = list()
    strbuffer = list()
    
    for char in source:
        if char in word_delimiters:
            result.append(''.join(strbuffer))
            strbuffer = list()
        else:
            strbuffer.append(char)
    return result

def frequency_analysis(source, word_separators=set([' ', '\t', '\n']) ):
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
    strbuffer=list()

    for char in source:
        if char in word_separators:
            result[''.join(strbuffer)] += 1
            strbuffer=list()
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
        result[ pattern_classifier(el) ] += 1

    return result
