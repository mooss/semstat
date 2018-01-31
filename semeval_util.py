try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class xmlextract(object):
    """Open an xml from semeval and allow to easily extract informations from it.
    
    Most methods in this module return an ElementTree object, with the notable exception of the ids methods.
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


    def get_org_subjects(self):
        """Retrieve the subjects of the original questions.
        
        Returns
        -------
        out : list of ET.element
            The list of the subjects of the original questions.
        """
        return [q.find('OrgQSubject') for q in self.get_org_questions_uniq()]


    def get_org_bodies(self):
        """Retrieve the bodies of the original questions.
        
        Returns
        -------
        out : list of ET.Element
            The list of the bodies of the original questions.
        """
        return [q.find('OrgQBody') for q in self.get_org_questions_uniq()]


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
                element.text for element in self.root.findall( path )
            ]) # extract text from each element matching the path

        # There is certainly a more performant/elegant/idiomatic solution to this problem.
        # I'll come back to it eventually.

        return result;
