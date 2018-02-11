try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from enum import Enum

import re

id_classification = Enum('id_classification', 'org rel comment none')

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
        the next three elements are the org fragment (ex Q268),
        the rel fragment (ex _R4), and
        the comment fragment (ex _C2).
    """
    match = re.match( r'(Q[0-9]+)(_R[0-9]+)?(_C[0-9]+)?', identifier)
    if match:
        result = match.groups()
        group_number = 0
        for i in result:
            if i is not None:
                group_number += 1 # there must be a better way to get the number of non None elements in a tuple
            
        if group_number == 1:
            return (id_classification.org, ) + result
        if group_number == 2:
            return (id_classification.rel, ) + result
        if group_number == 3:
            return (id_classification.comment, ) + result
    
    return (id_classification.none,)

    
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
                current_subtree = org_question # works because assignment has reference semantics
                ids_encountered.add(org_id)
            else:
                current_subtree.append( org_question.find('./Thread') )
                self.root.remove(org_question)
        self.merged_tree._setroot(self.merged_root)
        
    def get_org_questions_all(self):
        """Retrieve *all* the original questions.
        
        Returns
        -------
        out : list of ET.Element
            The list of *all* original questions.
        """
        result = list()
        for org_question in self.root.iter('OrgQuestion'):
            result.append(org_question)
        return result
        

    def get_org_questions_uniq(self):
        """Retrieve the original questions, uniq version.
        
        Returns
        -------
        out : list of ET.Element
            The list of original questions, without duplicate.
        """
        id_set = set() # this is for keeping track of the IDs
        result = list()

        for org_question in self.root.iter('OrgQuestion'):
            org_id = org_question.attrib['ORGQ_ID']
            if org_id not in id_set: # making sure there is no repetition
                id_set.add(org_id)
                result.append(org_question)

        return result;


    def get_org_questions_ids(self):
        """Retrieve the original questions' IDs.
        
        Returns
        -------
        out : list of str
            The list of the original questions IDs.
        """
        return [q.attrib['ORGQ_ID'] for q in self.get_org_questions_uniq()]
    
    #################################
    # retrieve elements from any id #
    #################################
    
    #################################
    # retrieve elements from org id #
    #################################
    def get_rel_comments_from_org_id(self, org_id):
        """Retrieve the related comments from an original question ID.
        
        Parameters
        ----------
        org_id : str
           The ID of the original question.
        
        Returns
        -------
        out : list of ET.Element
            The list of the related comments to the original question.
        """
        all_org_questions = self.get_org_questions_all()
        result = list()

        for question in all_org_questions:
            if question.attrib['ORGQ_ID'] == org_id:
                result.extend( question.findall('./Thread/RelComment') ) # using xpath support to easily extract all related comments

        return result

    def get_org_question_from_org_id(self, org_id):
        """Retrieve an original question using its id.
        
        Parameters
        ----------
        org_id : srt
            The ID of the original question.
        
        Returns
        -------
        out : ET.Element
            The original question.
        """
        all_org_questions = self.get_org_questions_all()

        for question in all_org_questions:
            if question.attrib['ORGQ_ID'] == org_id:
                return question

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
        result=list()
        for org_question in self.root.iter('OrgQuestion'):
            if org_question.attrib['ORGQ_ID'] == org_id:
                result.extend( org_question.findall(path) )

        return result

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
        for org_question in self.root.iter('OrgQuestion'):
            if org_question.attrib['ORGQ_ID'] == org_id:
                extraction = org_question.find(path)
                if extraction is not None:
                    return extraction # only returns if a path was found

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

        # first we add the original subject and the original body, to avoid duplication
        for question in self.get_org_questions_uniq():
            result.append( question.find('OrgQSubject').text )
            result.append( question.find('OrgQBody').text )

        # then we add the rest
        for path in [ './OrgQuestion/Thread/RelQuestion/RelQSubject',
                      './OrgQuestion/Thread/RelQuestion/RelQBody',
                      './OrgQuestion/Thread/RelComment/']:
            result.extend([
                element.text if element.text != None else '' for element in self.root.findall( path )
            ]) # extract text from each element matching the path

        # There is certainly a more performant/elegant/idiomatic solution to this problem.
        # I'll come back to it eventually.

        return result;    
