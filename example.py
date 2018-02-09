#!/usr/bin/python3

import nltk
import sys
from semeval_util import xmlextract
from textstat import *

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

question_ids=extractor.get_org_questions_ids()
print("number of ids:", len(question_ids))

lost=[4,8,15,16,23,42]
my_selection = [ extractor.find_path_from_org_id('.', question_ids[offset] ) for offset in lost ]

for question in my_selection:
    question_id = question.attrib['ORGQ_ID']
    print( '#', question.find('./OrgQSubject').text,
           '# ID:', question_id,
           '\n\t', question.find('./OrgQBody').text, '\n' , sep='')
    related_questions = extractor.findall_path_from_org_id('./Thread/RelQuestion', question_id) # forced to use this because original questions are duplicated in the tree structure chosen by SemEval
    for rel in related_questions:
        print( '\t#', rel.find('./RelQSubject').text,
               '# ID:', rel.attrib['RELQ_ID'],
               ', ', rel.attrib['RELQ_RELEVANCE2ORGQ'],
               '\n\t\t', rel.find('./RelQBody').text, '\n', sep='')
    

# for relc in extractor.get_rel_comments_from_org_id('Q268'):
#     print('\trelated comment id:', relc.attrib['RELC_ID'])

# fulltext = extractor.get_all_text()
# joined_text = ''.join(fulltext)

# print( len(fulltext), ' entries')
# freq =  frequency_analysis( joined_text )

# #print( "number of tokens found :\n\tby naive frequency analysis\t|\tby nltk's word_tokenize\n\t\t", len(freq), "\t\t\t|\t\t", len( nltk_frequency_analysis(joined_text) ))

# cardinal = 20
# print('here are the ', cardinal, ' most common words from ', source_filename, ':')

# count=1
# for el in sorted(freq, key=freq.__getitem__, reverse=True):
#     if count <= cardinal:
#         print('\t', el, '\t --> ', freq[el], ' occurences')
#         count += 1
#     else:
#         break

# print("tokenizing...", end='')
# sys.stdout.flush()
# tokens = word_tokenize(joined_text)
# print("done\npos tagging...", end='')
# sys.stdout.flush()
# tagged_text = nltk.pos_tag( tokens )
# print('done')
# tag_counter = defaultdict(int)
# for (word, tag) in tagged_text:
#     tag_counter[tag] += 1

# print('\noccurence of tags:')
# for el in sorted(tag_counter, key=tag_counter.__getitem__, reverse=True):
#     print('\t', el, '\t --> ', tag_counter[el])
