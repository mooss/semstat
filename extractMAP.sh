#!/usr/bin/env bash
prediction=$1

if echo $prediction | grep --quiet "2016"
then
    reference=scorer/SemEval2016-Task3-CQA-QL-test.xml.subtaskB.relevancy
else
    if echo $prediction | grep --quiet "2017"
    then
        reference=scorer/SemEval2017-Task3-CQA-QL-test.xml.subtaskB.relevancy
    else
        reference=scorer/SemEval2016-debug.relevancy
    fi
fi

python2 scorer/ev.py $reference $prediction | grep "^MAP" | sed 's/ \+/;/g' | cut -f 4 -d ';'
