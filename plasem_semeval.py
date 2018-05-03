import os.path
from plasem_algostruct import save_object, load_object, natural_sort_key
from semeval_xml import get_semeval_id, get_related_threads, xmlextract

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
