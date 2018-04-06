#!/usr/bin/env bash
reference=scorer/SemEval2017-Task3-CQA-QL-test.xml.subtaskB.relevancy
prediction=$1
python2 scorer/ev.py $reference $prediction | head -n 25 | tail -n 4 | sed -e 's/://' -e 's/ *IR/\tIR/'
