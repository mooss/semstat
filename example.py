#!/usr/bin/python3

import sys
import argparse
import nltk
from semeval_util import xmlextract
from textstat import *

parser = argparse.ArgumentParser(description='Parse, explore and make statistics on a SemEval xml file from task 3')

# positionnal arguments
parser.add_argument('source', metavar='source.xml', type=str, nargs=1,
                    help='the file to explore or analyse')

# optionnal arguments
parser.add_argument('--display',
                    choices=['related', 'original', 'comments'],
                    default='original',
                    help="choose what will be displayed")

arguments = parser.parse_args()

source_filename = arguments.source[0]
tabulator='   '

print('source:', source_filename)

extractor = xmlextract(source_filename)



# for subject in extractor.get_org_subjects():
#     print('\t', subject.text)
    
# for body in extractor.get_org_bodies():
#     print('\t', body.text)

question_ids=extractor.get_org_questions_ids()
print("number of ids:", len(question_ids))

lost=[4,8,15,16,23,42]
my_selection = [ extractor.find_path_from_org_id('.', question_ids[offset] ) for offset in lost ]

def display_related(related_thread, tabulator):
    """Display the related questions.
    
    Parameters
    ----------
    related_thread : ET.Element
        Element tree to display.
    """
    relquestion = related_thread.find('./RelQuestion')
    print( tabulator, '#', relquestion.find('./RelQSubject').text,
           '# ID:', relquestion.attrib['RELQ_ID'],
           ', ', relquestion.attrib['RELQ_RELEVANCE2ORGQ'],
           '\n', tabulator*2, relquestion.find('./RelQBody').text, '\n', sep='')

def display_comments(related_thread, tabulator):
    """Display the related comments.
    
    Parameters
    ----------
    related_thread : ET.Element
        Element tree to display.
    """
    comments = related_thread.findall('./RelComment')
    for comment in comments:
        print(tabulator*3, '# ID:',
              comment.attrib['RELC_ID'],
              ', ', comment.attrib['RELC_RELEVANCE2ORGQ'], ' to org',
              ', ', comment.attrib['RELC_RELEVANCE2RELQ'], ' to rel',
              '\n', tabulator*3, comment.find('./RelCText').text, '\n', sep='')


for question in my_selection:
    question_id = question.attrib['ORGQ_ID']
    print( '#', question.find('./OrgQSubject').text,
           '# ID:', question_id,
           '\n', tabulator, question.find('./OrgQBody').text, '\n' , sep='')

    # related questions
    if arguments.display == 'related' or arguments.display == 'comments':
        related_questions = extractor.findall_path_from_org_id(
            './Thread', question_id)
        # forced to use the extractor because original questions are duplicated in the tree structure chosen by SemEval
        for rel in related_questions:
            display_related(rel, tabulator)
            if(arguments.display == 'comments'):
                display_comments(rel, tabulator)
    

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
