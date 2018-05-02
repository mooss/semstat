import os.path
from plasem_algostruct import save_object, load_object
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
        result = make_document_tree(
            extractor.get_org_elements(), model, content_extractor)

        if verbose:
            print('Saving document tree to', saved_path)
        save_object(result, saved_path)

        return result
