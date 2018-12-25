# conll_processing_and_analysis

analyze_parses.py
This file runs analysis for .conll files. The analysis includes:
- count of each dependency-relationship (deprel) for each language
- the percentage of each deprel among all deprels, for each language
- the percentage of sentences that include each deprel, for each language.
The above statistics are also calculated for unique cases, such as negation,
raising/control, relative clauses and we questions.


post_processing_parser.py
This file does post-processing for .conll10 files. This includes:
- Correction of tokenizing: splitting unsplit tokens and assigning them correct lables.
- Correction of words with errors, such as 'na#hexlīf' --> 'naxlīf'
- Replace the tag of negation from ADV to PART
- Correction of 'empty_pronoun' cases.
- Splitting pronouns.
- Change 'iobj' to 'nmod', only if token has a dependent with label 'case'.
The output is .conll10 file(s) with the same name + '_out'.
Assamptions for input .conll10 files: every sentence ends with punctuation
