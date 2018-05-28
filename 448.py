# needs to be executed after baseline_filters_comparison

original_question = 'Q424'
corpus_year = '2017'

total_removed = 0

for relk in doctrees[corpus_year][original_question].keys() - {'org'}:
    relv = doctrees[corpus_year][original_question][relk]
    removed = 0
    for tok in relv:
        if not all(filters[flt](str(tok)) for flt in bestmeth[corpus_year]):
            removed += 1
    print(relk, removed, 'tokens removed')
    total_removed += removed

print('total removed', total_removed)

def printpred(scoretree):
    sscores = list(map(
        lambda x: x,
        sorted(scoretree[original_question].items(), key=lambda x: x[1], reverse=True)
    ))
    spred = sorted_scores_from_semeval_relevancy(relevancy[corpus_year], scoretree)

    for question, relevance in zip(sscores, spred[original_question]):
        print(question, relevance)

print('baseline')
printpred(baselinescores[corpus_year])

print('best filters')
printpred(bestscores[corpus_year])

bestrelev = 'Q424_R68'



besttoks = []
rawtoks = []
orgq = apdiff[corpus_year][0][0]
for tok in doctrees[corpus_year][orgq]['org']:
    if all(filters[flt](str(tok)) for flt in bestmeth[corpus_year]):
        besttoks.append(str(tok))
    rawtoks.append(str(tok))

print()
print('orgq:', orgq)
print('tokenisation baseline', corpus_year)
print(' '.join(rawtoks))
print()
print('tokenisation meilleurs réponses', corpus_year)
print(' '.join(besttoks))
