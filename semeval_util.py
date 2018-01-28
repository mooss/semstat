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
