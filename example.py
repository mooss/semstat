#!/usr/bin/python3

import sys
from semeval_util import xmlextract
from textstat import frequency_analysis

usage = "usage: " + sys.argv[0] + " file.xml"

if len(sys.argv) != 2:
    print(usage)
    quit()

source_filename = sys.argv[1]

extractor = xmlextract(source_filename)

# for subject in extractor.get_org_subjects():
#     print('\t', subject.text)
    
# for body in extractor.get_org_bodies():
#     print('\t', body.text)

# for iden in extractor.get_org_questions_ids():
#     print('\t', iden)

# for relc in extractor.get_rel_comments_from_org_id('Q268'):
#     print('\trelated comment id:', relc.attrib['RELC_ID'])

fulltext = extractor.get_all_text()

print( len(fulltext), ' entries')

freq =  frequency_analysis( ''.join(fulltext) )

cardinal = 20

print('here are the ', cardinal, ' most common words from ', source_filename, ':')

count=1

for el in sorted(freq, key=freq.__getitem__, reverse=True):
    if count <= cardinal:
        print('\t', el, '\t --> ', freq[el], ' occurences')
        count += 1
    else:
        break
