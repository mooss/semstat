from nltk.tokenize import word_tokenize

from collections import defaultdict # dictionary with Perl-like autovivification feature

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
