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
