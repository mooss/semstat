def normalized_ratio(x, y):
    """Divises the smallest argument by the greatest.

    Parameters
    ----------
    x : number

    y : number

    Returns
    -------
    out : float
        The normalized ratio
    """
    return min([x, y]) / max([x, y])


def split_container(container, criterion):
    """Split a container into a dict of containers according to a criterion funtion.

    Parameters
    ----------
    container : Container of a

    criterion : function(a) -> b

    Returns
    -------
    out : dict of Container of a

    """
    result = {}

    for el in container:
        tag = criterion(el)
        if tag not in result.keys():
            result[tag] = type(container)  # creation of a new entry
        result[tag].append(el)
    return result


###################
# print functions #
###################


def print_related(related_thread, tabulator):
    """Print the related questions.

    Parameters
    ----------
    related_thread : ET.Element
        Element tree to print.
    """
    relquestion = related_thread.find('./RelQuestion')
    print(tabulator, '#', relquestion.find('./RelQSubject').text,
          '# ID:', relquestion.attrib['RELQ_ID'],
          ', ', relquestion.attrib['RELQ_RELEVANCE2ORGQ'],
          '\n', tabulator * 2, relquestion.find('./RelQBody').text, '\n', sep='')


def print_comments(related_thread, tabulator):
    """Print the related comments.

    Parameters
    ----------
    related_thread : ET.Element
        Element tree to print.
    """
    comments = related_thread.findall('./RelComment')
    for comment in comments:
        print(tabulator * 3, '# ID:',
              comment.attrib['RELC_ID'],
              ', ', comment.attrib['RELC_RELEVANCE2ORGQ'], ' to org',
              ', ', comment.attrib['RELC_RELEVANCE2RELQ'], ' to rel',
              '\n', tabulator * 3, comment.find('./RelCText').text, '\n', sep='')
