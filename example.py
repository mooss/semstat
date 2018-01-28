#!/usr/bin/python3

import sys
from semeval_util import xmlextract

usage = "usage: " + sys.argv[0] + " file.xml"

if len(sys.argv) != 2:
    print(usage)
    quit()

source_filename = sys.argv[1]

extractor = xmlextract(source_filename)

for subject in extractor.get_org_subjects():
    print('\t', subject.text)
    
for body in extractor.get_org_bodies():
    print('\t', body.text)

for iden in extractor.get_org_questions_ids():
    print('\t', iden)
