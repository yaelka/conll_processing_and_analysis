""" this file runs analysis for .conll files """

from conllu import parse_incr
import os
import re
import copy
import optparse

# key words for wh questions
HEB_WH_WORDS = ['ʔēyfo', 'ʔeyḳ', 'ʔēyze', 'ʔēyzo', 'ʔēyzu', 'kāma', 'lāma',
                'leʔān', 'leʔāyin', 'ma', 'madūaʕ', 'māhu', 'matāy',
                'ma_zoʔt_ʔomēret', 'meʔāyin', 'mi','mīhu', 'ʔayē']
ENG_WH_WORDS = ['where', 'when', 'why', 'who', 'what', 'how', 'which', 'whom', 'whose', ]


def analyze_all_languages(dirs, languages):
    """
    runs the analysis on each of the language and prints a table in csv format showing
    the results.
    :param dirs: list of directories paths
    """
    if not len(dirs) == len(languages):
        print("languages list should match directories list")
        return

    # initialize dictionaries
    deprels_count = {}
    deprels_sent_count = {}
    unique_cases_count = {'relative clauses': {}, 'wh_questions': {}, 'negation': {},
                          "raising/control": {}}
    unique_sent_count = copy.deepcopy(unique_cases_count)
    sent_count = {}
    for case in unique_cases_count.keys():
        for language in languages:
            unique_cases_count[case][language] = 0
            unique_sent_count[case][language] = 0

    for i, dir_name in enumerate(dirs):
        sent_count[languages[i]] = parse_conll(dir_name, languages[i], deprels_count,
                                 unique_cases_count,
                    deprels_sent_count, unique_sent_count, languages)

    unique_cases_count['negation'] = deprels_count['neg']
    unique_sent_count['negation'] = deprels_sent_count['neg']
    unique_cases_count['raising/control'] = deprels_count['xcomp']
    unique_sent_count['raising/control'] = deprels_sent_count['xcomp']

    columns_names = "dependency"
    columns_names += "".join(["\tdep_count({0})\tpercentage_of_dependencies({0})"
          "\tpercentage_of_sentences({0})".format(languages[i]) for i in range(len(
        languages))])
    print(columns_names)
    print_dict_as_csv(deprels_count, deprels_sent_count, languages, sent_count)
    print('\nInteresting Constructions:')
    print_dict_as_csv(unique_cases_count, unique_sent_count, languages, sent_count)


def parse_conll(dir_name, cur_lang, deprels_count, unique_cases_count,
                deprels_sent_count, unique_sent_count, languages):
    """
    parse directory with files (conll format) and analyze it. Analysis includes 1. count
    of each dependency relationship and it's percentage within all relationships and
    sentences, 2. count of unique cases, such as relative clauses, negation,
    wh questions and more
    :param dir_name: directory to parse
    :param cur_lang: language of files in directory
    :param deprels_count: deprels dictionary, as created in analyze_all_languages
    :param unique_cases_count: unique cases dictionary
    :param deprels_sent_count: deprels dictionary for count of sentences that have each deprel
    :param unique_sent_count: uniwue cases dictionary for count of sentences
    :param languages: a list of all languages to analyze
    :return: number of sentences in current language
    """
    if cur_lang == "heb":
        suffix = ".conll10"
        wh_words = HEB_WH_WORDS
    elif cur_lang == "eng":
        suffix = ".txt" # should be changed to ".conll10" if files have .conll suffix
        wh_words = ENG_WH_WORDS

    sent_count = 0
    filenames = sorted([file for file in os.listdir(dir_name) if file.endswith(
        suffix)], key=lambda x: int(re.split('(\d+)', x[:x.find('.')])[1]))

    for filename in filenames:
        file = open(os.path.join(dir_name, filename), "r", encoding="utf-8")
        data = parse_incr(file)
        for sent_indx, sentence in enumerate(data):
            sent_count += 1
            cur_sent_deprels = []
            cur_sent_unique = []
            if sentence[0]['lemma'] in wh_words and sentence[len(sentence) -1]['lemma']\
                    == "?":
                unique_cases_count['wh_questions'][cur_lang] += 1
                unique_sent_count['wh_questions'][cur_lang] += 1

            for word_indx, cur_token in enumerate(sentence.tokens):
                cur_dep = cur_token['deprel']
                if cur_dep == "acl:relcl_subj":
                    cur_dep = "acl:relcl:subj"
                elif cur_dep == "acl:relcl_obj":
                    cur_dep = "acl:relcl:obj"
                if cur_dep in deprels_count:
                    deprels_count[cur_dep][cur_lang] += 1
                    if not cur_dep in cur_sent_deprels:
                        cur_sent_deprels.append(cur_dep)
                        deprels_sent_count[cur_dep][cur_lang] += 1
                else:
                    deprels_count[cur_dep] = {}
                    deprels_sent_count[cur_dep] = {}
                    for lang in languages:
                        deprels_count[cur_dep][lang] = 0
                        deprels_sent_count[cur_dep][lang] = 0
                    deprels_count[cur_dep][cur_lang] = 1
                    deprels_sent_count[cur_dep][cur_lang] = 1
                    cur_sent_deprels.append(cur_dep)

                # count relative clauses
                # all sub categories: 'acl:relcl:obj', 'acl:relcl:subj',
                # 'acl:relcl:nsubj', 'acl:relcl:subjpass'
                if 'acl:relcl' in cur_dep:
                    unique_cases_count['relative clauses'][cur_lang] += 1
                    if not 'relative clauses' in cur_sent_unique:
                        unique_sent_count['relative clauses'][cur_lang] += 1
                        cur_sent_unique.append('relative clauses')

                """ uncomment to look for interesting cases and print sentences that
                 include them, marking the words that have the interesting
                 relationship between them."""
                # unique_deprel = 'acl:relcl:obj'
                # if unique_deprel == cur_dep:
                #     print("dep: " + cur_dep + ",\t" + cur_token['lemma'] + ' <- ' +
                #           (sentence[cur_token['head'] -1]['lemma'] if cur_token['head']
                #                                                      > 0 else "NONE"))
                #     print([cur_tok['lemma'] for cur_tok in sentence.tokens])

    return sent_count


def print_dict_as_csv(dict, sent_dict, languages, num_sentences):
    """
    print results of input dictionary in csv format
    :param dict: dict that counts appearances of deprels among all deprels
    :param sent_dict: dict that counts how many sentences have appearances of each deprel
    :param languages: list of languages
    :param num_sentences: dictionary with languages as keys
    """
    deprels_total_count = {}
    for language in languages:
        deprels_total_count[language] = sum([val[language] for val in dict.values()])
    sorted_dict = sorted(dict.items(), key=lambda x: x[1][languages[0]], reverse=True)
    for item in sorted_dict:
        key = item[0]
        print(key, end='')
        for language in languages:
            if language in dict[key]:
                word_count = str(dict[key][language])
                word_freq = str("{0:.3f}".format(int(word_count)/float(
                    deprels_total_count[language])))
                sent_count = str("{0:.3f}".format(sent_dict[key][language]/float(
                    num_sentences[language])))
            else:
                word_count = "0"
                word_freq = "0"
                sent_count = "0"
            print('\t' + word_count + '\t' + word_freq + '\t' + sent_count, end='')
        print('')


def main():
    heb_dir = "manually_annotated\\Heb\\out"
    eng_dir = "manually_annotated\\Eng"

    optparser = optparse.OptionParser()
    optparser.add_option("-d", "--dirs", dest="path",
                         default="{},{}".format(eng_dir, heb_dir),
                         help="list of directories-paths with conll files, separated by comma")
    optparser.add_option("-l", "--languages", dest="languages", default="eng,heb",
                         help="list of languages corresponding to dirs, separated by "
                              "comma")

    (opts, _) = optparser.parse_args()
    analyze_all_languages(opts.path.split(','), opts.languages.split(','))


if __name__ == "__main__":
    main()