#!/usr/bin/python3

import argparse
from nltk.tokenize import word_tokenize
from semeval_util import *
from textstat import *
from helper_functions import *

parser = argparse.ArgumentParser(
    description='Parse, explore and make statistics on a SemEval xml file from task 3')

tokenizer_dispatcher = {'delimiter_tokenizer': delimiter_tokenizer,
                        'nltk_tokenizer': word_tokenize}


normalizer_dispatcher = {'normalize': normalized_ratio,
                         'off': lambda x, y: x / y}

########################
# positional arguments #
########################
parser.add_argument('source',
                    metavar='source.xml',
                    type=str,
                    help='the file to explore or analyse')

######################
# optional arguments #
######################
parser.add_argument('--stat',
                    choices=['wordfreq', 'org2rel_len'],
                    nargs='+',
                    help='statistics to show about the selection')

parser.add_argument('--tokenization',
                    choices=tokenizer_dispatcher.keys(),
                    default='delimiter_tokenizer',
                    type=str,
                    help='tokenization function to use')

parser.add_argument('--normalization',
                    choices=normalizer_dispatcher.keys(),
                    default='normalize',
                    help='normalization function to use')

# todo: add filter option (like remove errors, ignore articles...)

parser.add_argument('--print',
                    choices=['original', 'related', 'comments', 'dump_text'],
                    default='original',
                    help='choose what will be printed')

# element selection
selection = parser.add_mutually_exclusive_group()
selection.add_argument('--indexes',
                       type=int, nargs='+',
                       help='list of the 0-based indexes of the desired *original* questions')

# selection.add_argument('--ids',
#                        type=str, nargs='+',
#                        help='list of the ids of the desired elements')

selection.add_argument('--lost', action='store_true',
                       help='equivalent to `--indexes 4 8 15 16 23 42`')

arguments = parser.parse_args()

# parameters initialisation
source_filename = arguments.source
printstyle = arguments.print
tabulator = '   '
tokenizer_function = tokenizer_dispatcher[arguments.tokenization]
normalizer_function = normalizer_dispatcher[arguments.normalization]

extractor = xmlextract(source_filename)
question_ids = extractor.get_org_questions_ids()

######################
# question selection #
######################
# indexes
index_list = []
if arguments.indexes is not None:
    index_list = arguments.indexes
if arguments.lost:
    index_list = [4, 8, 15, 16, 23, 42]

my_selection = [
    extractor.find_path_from_org_id('.', question_ids[offset])
    for offset in index_list
]

#########################
# statistics processing #
#########################
print(arguments)

if arguments.stat is not None:
    printstyle = None  # don't print raw text if stats were demanded

    score_function = len
    split_function = get_semeval_relevance_orgq
    stat_roots = extractor.merged_root.findall('OrgQuestion')

    score_accumulator = dict()
    org_scores = {}

    for orgq in stat_roots:
        org_scores[get_semeval_id(orgq)] = score_function(
            tokenizer_function(get_semeval_content(orgq)))

        splitted_relqs = split_container(
            orgq.findall('./Thread/RelQuestion'),
            split_function
        )

        # calculating the scores
        splitted_scores = {}
        for key in splitted_relqs.keys():
            splitted_scores[key] = [
                score_function(tokenizer_function(get_semeval_content(el)))
                for el in splitted_relqs[key]
            ]

        # relevance_translation = {'PerfectMatch': 'perf',
        #                          'Relevant': 'rlvt',
        #                          'Irrelevant': 'irlvt'}

        # print('question', get_semeval_id(orgq), '\t',
        #       {relevance_translation[i]:
        #        normalizer_function(org_score, average(splitted_scores[i]))
        #        for i in splitted_scores.keys()})

        score_accumulator[get_semeval_id(orgq)] = splitted_scores

    # computing the stats

    # stat_accumulator = {
    #     orgq_id: {
    #         relevance: average(score_accumulator[orgq_id][relevance])
    #         for relevance in score_accumulator[orgq_id],
    #     }
    #     for orgq_id in score_accumulator
    # }

    stat_accumulator = {}
    normalized_accumulator = {}

    for orgq_id in score_accumulator:
        stat_accumulator[orgq_id] = {}
        normalized_accumulator[orgq_id] = {}

        for relevance in score_accumulator[orgq_id]:
            stat_accumulator[orgq_id][relevance] = average(
                score_accumulator[orgq_id][relevance])

            normalized_accumulator[orgq_id][relevance] = normalizer_function(
                stat_accumulator[orgq_id][relevance], org_scores[orgq_id])

    def pretty_print_stat(dic, id, tag):
        if tag in dic[id]:
            return ' %0.2f |' % dic[id][tag]
        return '       |'

    for org_id in stat_accumulator:
        print(org_id, ':', "%-8s|" % org_scores[org_id],
              pretty_print_stat(stat_accumulator, org_id, 'PerfectMatch'),
              pretty_print_stat(stat_accumulator, org_id, 'Relevant'),
              pretty_print_stat(stat_accumulator, org_id, 'Irrelevant'),
              '||',
              pretty_print_stat(normalized_accumulator,
                                org_id, 'PerfectMatch'),
              pretty_print_stat(normalized_accumulator, org_id, 'Irrelevant'),
              pretty_print_stat(normalized_accumulator, org_id, 'Relevant'),
              )

    def access_if_exists(container, key, otherwise):
        if key in container:
            return container[key]
        else:
            return otherwise

    print('moyenne globale:')
    perfect_values = []
    relevant_values = []
    irrelevant_values = []

    merged_normalized_accumulator = defaultdict(list)
    for id in normalized_accumulator:
        for relevance in ['PerfectMatch', 'Relevant', 'Irrelevant']:
            if relevance in normalized_accumulator[id]:
                merged_normalized_accumulator[relevance].append(
                    normalized_accumulator[id][relevance])

    for relevance in merged_normalized_accumulator:
        print(relevance, ':', average(merged_normalized_accumulator[relevance]))

    quit()
    if 'wordfreq' in arguments.stat:
        txt = '\n'.join(extractor.get_all_text())
        tokens = tokenizer_function(txt)

        patterns = count_patterns(
            tokens,
            lambda x: x)

        for pattern in sorted_dict(patterns)[:20]:
            print(pattern, '-->', patterns[pattern])

    if 'org2rel_len' in arguments.stat:
        orgquestions = extractor.merged_root.findall('OrgQuestion')
        org2rel_lens = list()
        for orgq in orgquestions:
            orglen = len(tokenizer_function(get_semeval_content(orgq)))

            rellens = [
                len(tokenizer_function(get_semeval_content(relq)))
                for relq in orgq.findall('./Thread/RelQuestion')
            ]
            org2rel_lens.append(
                normalizer_function(orglen, sum(rellens) / len(rellens)))
            print('len ratio for question', get_semeval_id(
                orgq), '=', org2rel_lens[-1])
        print('mean len ratio =', (sum(org2rel_lens) / len(org2rel_lens)))

######################
# selection printing #
######################

if printstyle in ['original', 'related', 'comments']:
    for question in my_selection:
        question_id = question.attrib['ORGQ_ID']
        print('#', question.find('./OrgQSubject').text,
              '# ID:', question_id,
              '\n', tabulator, question.find('./OrgQBody').text, '\n', sep='')
        # related questions
        if printstyle == 'related' or printstyle == 'comments':
            related_questions = extractor.findall_path_from_org_id(
                './Thread', question_id)
            # forced to use the extractor because original questions are duplicated in the tree structure chosen by SemEval
            for rel in related_questions:
                print_related(rel, tabulator)
                if(printstyle == 'comments'):
                    print_comments(rel, tabulator)
if printstyle == 'dump_text':
    print('\n'.join(extractor.get_all_text()))


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
