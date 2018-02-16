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


def merge_dict_in_place(modified_dict, other_dict, merge_value_function):
    """Merges two dictionaries according to a merge function.

    Parameters
    ----------
    modified_dict : dict of a
        The dictionary that will receive the merged elements.

    other_dict : dict of a
        The dictionary that will add new elements.

    merge_value_function : function(a, a)
        The function that will be used to merge the values.
        It must alter its first argument.
        This means that merge_dict_in_place cannot be used to merge dictionaries of immutable objects.
    """
    for key in other_dict:
        if key in modified_dict:
            merge_value_function(modified_dict[key], other_dict[key])
        else:
            modified_dict[key] = other_dict[key]


def split_container(container, criterion):
    """Split a container into a dict of containers according to a criterion funtion.

    Parameters
    ----------
    container : Container of a

    criterion : function(a) -> b

    Returns
    -------
    out : dict of list of a

    """
    result = {}

    for el in container:
        tag = criterion(el)
        if tag not in result.keys():
            result[tag] = list()  # creation of a new entry
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
