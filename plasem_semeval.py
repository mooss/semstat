from operator import itemgetter
import csv
import os.path
from plasem_algostruct import save_object, load_object, natural_sort_key, mean_average_precision
from semeval_xml import get_semeval_id, get_related_threads, xmlextract, is_relevant_to_orgq

def make_semeval_document_tree(original_questions, model, content_extractor):
    result = {}
    for org in original_questions:
        orgid = get_semeval_id(org)
        result[orgid] = {
            get_semeval_id(rel): model(content_extractor(rel))
            for rel in get_related_threads(org)
        }
        result[orgid]['org'] = model(content_extractor(org))
    return result

def make_or_load_semeval_document_tree(xml_source, saved_path, model, content_extractor, verbose=False):
    if os.path.isfile(saved_path):
        if verbose:
            print('Loading document tree from', saved_path)
        result = load_object(saved_path)
        return result
    else:
        if verbose:
            print('Creating document tree. This might take a while...')

        extractor = xmlextract(xml_source)
        result = make_semeval_document_tree(
            extractor.get_org_elements(), model, content_extractor)

        if verbose:
            print('Saving document tree to', saved_path)
        save_object(result, saved_path)

        return result
    
def write_scores_to_file(scores, filename, verbose=False):
    """Write a semeval score tree to a prediction file.
    
    Parameters
    ----------
    scores : dict of dict of float
        The scores to write.

    filename : str
       The name of the output file.
    """
    linebuffer = [(orgid, relid, str(0), str(score), 'true')
                  for orgid, relqs in scores.items()
                  for relid, score in relqs.items()]

    linebuffer.sort(key=lambda x: natural_sort_key(x[1]))

    if verbose:
        print('writing scores to', filename)

    with open(filename, 'w') as out:
        out.write('\n'.join(['\t'.join(el) for el in linebuffer]))

def MAP_generic(relevancy_dict, scoretree):
    """Computes the mean average precision (MAP) from a relevancy dictionnary and a score tree.

    Parameters
    ----------
    relevancy_dict : dict of boolean
        Dictionnary associating question IDs to their boolean relevance.

    scoretree : dict of dict of float
        Score tree to evaluate, as produced by the make_score_tree function.

    Returns
    -------
    out : float
       The mean average precision of the scores.
    """
    def isrelevant(sorteditems):
        return relevancy_dict[sorteditems[0]]

    def sortrelated(related):
        items = sorted(related.items(), key=lambda x: natural_sort_key(itemgetter(0)(x)))
        items.sort(key=itemgetter(1), reverse=True)
        return items

    sorted_scores = {
        original: list(map(isrelevant, sortrelated(related)))
        for original, related in scoretree.items()
    }
    print(sorted_scores)
    return mean_average_precision(sorted_scores.values())

    
def MAP_from_semeval_relevancy(relevancyfile, scoretree):
    """Computes the mean average precision (MAP) from a relevancy file and a score tree.

    Parameters
    ----------
    relevancyfile : str
        IR SemEval .relevancy file.

    scoretree : dict of dict of float
        Score tree to evaluate, as produced by the make_score_tree function.

    Returns
    -------
    out : float
       The mean average precision of the scores.
    """
    rlv = csv.reader(open(relevancyfile), delimiter='\t')
    relev = {
        row[1]: True if row[4] == 'true' else False
        for row in rlv
    }
    return MAP_generic(relev, scoretree)


def MAP_from_semeval_xml(xmlfile, scoretree):
    """Computes the mean average precision (MAP) from a relevancy file and a score tree.

    Parameters
    ----------
    xmlfile : str
        Reference XML file.

    scoretree : dict of dict of float
        Score tree to evaluate, as produced by the make_score_tree function.

    Returns
    -------
    out : float
       The mean average precision of the scores.
    """
    extractor = xmlextract(xmlfile)
    relev = {
        get_semeval_id(relquestion): is_relevant_to_orgq(relquestion)
        for relquestion in extractor.get_rel_elements()
    }
    return MAP_generic(relev, scoretree)
