import xml.etree.ElementTree as ET

class xmlextract(object):
    """Open an xml from semeval and allow to easily extract informations from it.
    """

    def __init__(self, xml_filename):
        """Initialise the extractor
        Keyword Arguments:
        xml_filename -- name of the source xml file
        """
        self.source = xml_filename
        self.tree = ET.parse(self.source)
        self.root = self.tree.getroot()

    def getorgquestions(self):
        """Retrieve the original questions
        """
        id_set = set()
        result = list()

        for org_question in self.root.iter('OrgQuestion'):
            org_id = org_question.attrib['ORGQ_ID']
            if org_id not in id_set: # making sure there is no repetition
                id_set.add(org_id)
                result.append(org_question)

        return result;

    def getorgsubjects(self):
        """Retrieve the subjects of the original questions        
        """
        return [ q.find('OrgQSubject') for q in self.getorgquestions() ]
        
