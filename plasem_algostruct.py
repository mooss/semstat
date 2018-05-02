import re
import operator
import pickle

def save_object(obj, filename):
    pickle.dump(obj, open(filename, 'wb'))

def load_object(filename):
    return pickle.load(open(filename, 'rb'))

def transformtree_deep(func, tree):
    """Transform a tree by applying a function to its leaves.

    Parameters
    ----------
    func : function
        The function that will transform each leaf.

    tree : recursive dict
        The tree to transform.

    Returns
    -------
    out : recursive dict
        The transformed tree.
    """
    return {
        key: transformtree_deep(func, value)
        if isinstance(value, dict)
        else func(value)
        for key, value in tree.items()
    }

def transformtree_n(func, tree, n):
    """Transform a tree up to a maximum depth by applying a function to its leaves.

    Once the maximum depth is reached, the function is applied, even if it is not a leaf.

    Parameters
    ----------
    func : function
        The function that will transform each leaf, as well as the final depth.

    tree : recursive dict
        The tree to transform.

    n : int
        The maximum depth

    Returns
    -------
    out : recursive dict
        The transformed tree.
    """
    if n > 0:
        return {
            key: transformtree_n(func, value, n - 1)
            if isinstance(value, dict)
            else func(value)
            for key, value in tree.items()
        }
    else:
        return { key: func(value) for key, value in tree.items() }

def transformtree(func, tree, n=-1):
    if n < 0:
        return transformtree_deep(func, tree)
    else:
        return transformtree_n(func, tree, n)

def sorted_items(dictionary, key=operator.itemgetter(1), reverse=False):
    return sorted(dictionary.items(), key=key, reverse=reverse)

def natural_sort_key(key):
    """Transform a key in order to achieve natural sort.
    from https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
    """
    def convert(text):
        return int(text) if text.isdigit() else text
    return [convert(c) for c in re.split('([0-9]+)', key)]

