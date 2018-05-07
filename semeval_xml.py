try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from enum import Enum
import re
from itertools import chain

id_classification = Enum('id_classification', 'org rel com none')

#############################
# defining pseudo constants #
#############################
"""The following regex, though hard to look at, perform the simple task of capturing:
 - the original id,
 - the related id,
 - and the comment id.

Examples:
 - 'Q4'         matches the groups ('Q4', None, None)
 - 'Q4_R8'      matches the groups ('Q4', 'R8', None)
 - 'Q4_R8_C154' matches the groups ('Q4', 'R8', 'C154')
 - 'R8'         does not match
"""
ID_EXTRACTION_REGEX = r'(Q[0-9]+)(?:_(R[0-9]+)(?:_(C[0-9]))?)?'

##################################
# helper functions to xmlextract #
##################################


def classify_id(identifier):
    """Gives information about an id.

    Parameters
    ----------
    identifier : str
        The identifier to classify.

    Returns
    -------
    out : tuple
        The classification of the identifier,
        the first element being the classification proper and
        the next three elements are:
         - the org fragment (ex Q268),
         - the rel fragment (ex _R4), and
         - the comment fragment (ex _C2).
    """
    match = re.match(ID_EXTRACTION_REGEX, identifier)
    if match:
        result = match.groups()
        group_number = 0
        for i in result:
            if i is not None:
                # there must be a better way to get the number of non None elements in a tuple
                group_number += 1

        if group_number == 1:
            return (id_classification.org, ) + result
        if group_number == 2:
            return (id_classification.rel, ) + result
        if group_number == 3:
            return (id_classification.com, ) + result

    return (id_classification.none,)


##############################
# semeval element retrievers #
##############################
def get_orgquestion_content(orgquestion):
    """Retrieve the content of an original question element.

    That is to say the textual content of both the subject and the body.

    Parameters
    ----------
    orgquestion : ET.Element
        The original question from which to get the text.

    Returns
    -------
    out : str
        The textual content of the original question.
    """
    return '. '.join(
        [orgquestion.find(tag).text
         if orgquestion.find(tag).text is not None else ''
         for tag in ['OrgQSubject', 'OrgQBody']
         ]
    )


def get_relquestion_content(relquestion):
    """Retrieve the content of an related question element.

    That is to say the textual content of both the subject and the body.

    Parameters
    ----------
    relquestion : ET.Element
        The related question from which to get the text.

    Returns
    -------
    out : str
        The textual content of the related question.
    """
    return '. '.join(
        [relquestion.find(tag).text
         if relquestion.find(tag).text is not None else ''
         for tag in ['RelQSubject', 'RelQBody']
         ]
    )


def get_relcomment_content(relcomment):
    """Retrieve the content of an related comment element.

    That is to say its textual content.

    Parameters
    ----------
    relcomment : ET.Element
        The related comment from which to get the text.

    Returns
    -------
    out : str
        The textual content of the related comment.
    """
    return relcomment.find('RelCText').text


def get_semeval_content(element):
    """Retrieve the content of a semeval element.

    That is to say the textual content of the both the subject and the body.

    Parameters
    ----------
    element : ET.Element
        The original question, related question or related comment to get the text from.

    Returns
    -------
    out : str
        The text of the element.
    """
    if element.tag == 'OrgQuestion':
        return get_orgquestion_content(element)

    if element.tag == 'RelQuestion':
        return get_relquestion_content(element)

    if element.tag == 'Thread':
        return get_relquestion_content(element.find('./RelQuestion'))

    if element.tag == 'RelComment':
        return get_relcomment_content(element)

    return None


def get_semeval_content_with_relcomments(element):
    """Retrieve the content of a semeval element, related comment included.

    That is to say an original question will return the textual content of the subject and the body whereas a related thread will return the textual content of the subject, the body and the comment.

    For consistency's sake, if the element is a comment, its content will still be returned.

    None is returned if the element is a related question.

    Parameters
    ----------
    element : ET.Element
        The original question, related question or related comment to get the text from.

    Returns
    -------
    out : str
        The text of the element.
    """
    if element.tag == 'OrgQuestion':
        return get_orgquestion_content(element)

    if element.tag == 'Thread':
        return ' '.join(chain(
            [get_relquestion_content(element.find('./RelQuestion'))],
            [get_relcomment_content(comment)
             for comment in element.findall('./RelComment')]
        ))

    if element.tag == 'RelComment':
        return get_relcomment_content(element)

    return None


def get_semeval_id(element):
    """Retrieve the id of a semeval element.

    Parameters
    ----------

    element : ET.Element
        The original question, related question or related comment from which to extract the id.

    Returns
    -------

    out : str
        The id of the element.
    """
    translation = {'OrgQuestion': 'ORGQ_ID',
                   'RelQuestion': 'RELQ_ID',
                   'RelComment': 'RELC_ID',
                   'Thread': 'THREAD_SEQUENCE'}

    if element.tag in translation.keys():
        return element.attrib[translation[element.tag]]
    return None


def get_semeval_relevance_orgq(element):
    """Retrieve the relevance of a semeval element, in regards with its original question.

    Parameters
    ----------
    element : ET.Element
        The related question or related comment from which to get the relevance.

    Returns
    -------
    out : str
        The relevance of the element.
    """
    if element.tag == 'RelQuestion':
        return element.attrib['RELQ_RELEVANCE2ORGQ']
    if element.tag == 'RelComment':
        return element.attrib['RELQ_RELEVANCE2ORGQ']
    return None

RELEVANT_TAGS = {'Good', 'PerfectMatch'}

def is_relevant_to_orgq(element):
    """Check if a semeval element is relevant to its original question.

    Parameters
    ----------
    element : ET.Element
        The related question or related comment.

    Returns
    -------
    out : boolean
        True if the element is relevant.
    """
    relevance = get_semeval_relevance_orgq(element)
    return relevance in RELEVANT_TAGS

def get_related_questions(element):
    """Retrieve the related question from an element.

    This element can be:
     - original question
     - related question (returns itself)
     - thread
     - full tree

    Parameters
    ----------
    element : ET.element
        The element from wich to extract the related questions.

    Returns
    -------
    out : list of ET.element
    """
    tag2path = {
        'OrgQuestion': './Thread/RelQuestion',
        'Thread': './RelQuestion',
        'RelQuestion': '.',
    }
    if element.tag in tag2path:
        return element.findall(tag2path[element.tag])
    return element.findall('./OrgQuestion/Thread/RelQuestion')


def get_related_threads(element):
    """Retrieve the related threads from an element.

    This element can be:
     - original question
     - related thread (returns itself)
     - full tree

    Parameters
    ----------
    element : ET.element
        The element from wich to extract the related thread.

    Returns
    -------
    out : list of ET.element
    """
    tag2path = {
        'OrgQuestion': './Thread',
        'Thread': '.',
    }
    if element.tag in tag2path:
        return element.findall(tag2path[element.tag])
    return element.findall('./OrgQuestion/Thread')


class xmlextract(object):
    """Open an xml from semeval and allow to easily extract informations from it.

    Most methods in this module return an ElementTree object, with the notable exception of the *ids methods and of get_all_text.
    """

    def __init__(self, xml_filename):
        """Initialize the extractor.

        Parameters
        ----------
        xml_filename : str
            The name of the source file.
        """
        self.source = xml_filename
        self.tree = ET.parse(self.source)
        self.root = self.tree.getroot()
        self.merge_original_questions()

    def merge_original_questions(self):
        """Merges together the subtrees of original questions sharing the same IDs.

        The original structure looks like

        Root
        |
        |__OrgQuestion<Org_ID1>
        |  |
        |  |__(subject and body)
        |  |
        |  |__Thread<Thread_ID1>
        |     |
        |     |__RelQuestion
        |     |  |
        |     |  |__...
        |     |
        |     |__RelComment +
        |        |__...
        |
        |__OrgQuestion<Org_ID1> # Same original question
        |  |
        | ...
        |  |
        |  |__Thread<Thread_ID2> # New thread
        |     |
       ...   ...

        The merged structure looks like

        Root
        |
        |__Orgquestion<ID1>
        |  |
        |  |__(subject and body)
        |  |
        |  |__Thread<Thread_ID1>
        |  |  |
        |  | ...
        |  |
        |  |__Thread<Thread_ID2> # The threads are now gathered at the same level
        |  |  |
        |  | ...
        | ...
        |
        |__OrgQuestion<ID2> # Next original question
        |  |
        | ...
       ...
        """
        self.merged_tree = ET.ElementTree()
        self.merged_root = self.root
        ids_encountered = set()
        for org_question in self.merged_root.findall('./OrgQuestion'):
            org_id = org_question.attrib['ORGQ_ID']
            if org_id not in ids_encountered:
                current_subtree = org_question  # works because assignment has reference semantics
                ids_encountered.add(org_id)
            else:
                current_subtree.append(org_question.find('./Thread'))
                self.root.remove(org_question)
        self.merged_tree._setroot(self.merged_root)

    def get_org_questions_ids(self):
        """Retrieve the original questions' IDs.

        Returns
        -------
        out : list of str
            The list of the original questions IDs.
        """
        return [q.attrib['ORGQ_ID'] for q in self.merged_root.findall('OrgQuestion')]

    #######################
    # elements extraction #
    #######################
    def get_org_elements(self):
        """Retrieve the elements of the original questions.

        Returns
        -------
        out : list of ET.element
        """
        return self.merged_root.findall('OrgQuestion')

    def get_rel_elements(self):
        """Retrieve the elements of the related questions.

        Returns
        -------
        out : list of ET.element
        """
        return self.merged_root.findall('OrgQuestion/Thread/RelQuestion')

    #######################################
    # retrieve specific elements from ids #
    #######################################
    def get_org_question(self, org_id):
        """Retrieve an original question using its id.

        Parameters
        ----------
        org_id : str
            The ID of the original question.

        Returns
        -------
        out : ET.Element
            The original question element if found, None otherwise.
        """
        for question in self.merged_root.iter('OrgQuestion'):
            if question.attrib['ORGQ_ID'] == org_id:
                return question
        return None

    def get_rel_thread(self, org_id, rel_id):
        """Retrieve a related thread using its original ID and its related ID.

        Parameters
        ----------
        org_id : str
           The original ID of the thread.

        rel_id : str
           The related ID of the thread.

        Returns
        -------
        out : ET.Element
            The related thread element if found, None otherwise.
        """
        for thread in self.get_org_question(org_id).iter('Thread'):
            if thread.attrib['THREAD_SEQUENCE'] == org_id + "_" + rel_id:
                return thread
        return None

    def get_rel_question(self, org_id, rel_id):
        """Retrieve a related question using its original ID and its related ID.

        Parameters
        ----------
        org_id : str
           The original ID of the question.

        rel_id : str
           The related ID of the question.

        Returns
        -------
        out : ET.Element
            The related question element if found, None otherwise.
        """
        return self.get_rel_thread(org_id, rel_id).find('./RelQuestion')

    def get_rel_comment(self, org_id, rel_id, com_id):
        """Retrieve a related comment using its original ID, its related ID and its comment ID.

        Parameters
        ----------
        org_id : str
            The original ID of the comment.

        rel_id : str
            The related ID of the comment.

        com_id : str
            The comment ID of the comment.

        Returns
        -------
        out : ET.Element
            The related comment element if found, None otherwise.
        """
        for comment in self.get_rel_thread(org_id, rel_id).iter('RelComment'):
            if comment.attrib['RELC_ID'] == org_id + '_' + rel_id + '_' + com_id:
                return comment
        return None

    #################################
    # retrieve any element from ids #
    #################################
    def get_element_from_id(self, identifier):
        """Retrieve an element from its ID.

        The element in question can either be an original question, a related question or a related comment.

        Parameters
        ----------
        identifier : str
            ID of the element (corresponding to an ORGQ_ID, RELQ_ID or RELC_ID).

        Returns
        -------
        out : ET.Element
            The asked-for element if it was found, None otherwise.
        """
        classification, org, rel, com = classify_id(identifier)
        if classification == id_classification.org:
            return self.get_org_question(org)
        elif classification == id_classification.rel:
            return self.get_rel_question(org, rel)
        elif classification == id_classification.com:
            return self.get_rel_comment(org, rel, com)
        return None

    ###########################
    # extracting path from id #
    ###########################
    def findall_path_from_org_id(self, path, org_id):
        """Retrieve instances of an xml path from the tree of an original question, identified by its ID.

        Parameters
        ----------
        path : str
            XML path to extract.

        org_id : str
            ID of the original question.

        Returns
        -------
        out : list of ET.Element
            The list of elements matching the path and the original question ID.
        """
        for org_question in self.merged_root.iter('OrgQuestion'):
            if org_question.attrib['ORGQ_ID'] == org_id:
                extraction = org_question.findall(path)
                if len(extraction) != 0:
                    return extraction

        return list()

    def find_path_from_org_id(self, path, org_id):
        """Retrieve the first xml path from the tree of an original question, identified by its ID.

        Parameters
        ----------
        path : str
            XML path to extract.

        org_id : str
            ID of the original question.

        Returns
        -------
        out : ET.Element
            The first element matching the path and the original question ID.
        """
        for org_question in self.merged_root.iter('OrgQuestion'):
            if org_question.attrib['ORGQ_ID'] == org_id:
                extraction = org_question.find(path)
                if extraction is not None:
                    return extraction  # only returns if a path was found

        return None

    ###################
    # text extraction #
    ###################
    def get_all_text(self):
        """Retrieve all the textual contents from the source file.

        This includes :
         - The original subject.
         - The original body.
         - The related subject.
         - The related body.
         - The related comments.

        Returns
        -------
        out : list of str
            The list of all the textual contents.
        """
        result = list()

        for path in ['./OrgQuestion/OrgQSubject',
                     './OrgQuestion/OrgQBody',
                     './OrgQuestion/Thread/RelQuestion/RelQSubject',
                     './OrgQuestion/Thread/RelQuestion/RelQBody',
                     './OrgQuestion/Thread/RelComment/']:
            result.extend([
                element.text if element.text is not None else '' for element in self.merged_root.findall(path)
            ])  # extract text from each element matching the path

        return result
