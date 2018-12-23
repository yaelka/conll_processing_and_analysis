from conllu import parse_incr
import re
import os
import optparse


"""
assamptions for input .conll10 files:  every sentence ends with punctuation

the main function is parse_conll() which received a path and processes all sentences.
It outputs a .conll10 file with the same name + '_out'
"""

# tokens that have a separator and should be left like that
not_to_split = ['qfic-qfoc', 'qfic_qfoc', 'çiq_çaʔq', 'Kvāy_kvēks',
                'ʔaxarēy', 'ʔoy_wey', 'hōqus_pōqus', 'le','ʔet', 'šel']

# tokens that are split by '_', '+' or '-' and should not be split at all
non_split_to_unite = ['sūper_mārqeṭ']

# tokens that don't have a separator but should be split
to_split = ['leʕacmāh', 'leʕacmī', 'leʕacmō', 'ba', 'svivā', 'bešum', 'xemdatī',
            'ledaʕatī','beʕacmēḳ', 'beʔemēt', 'bezehirūt']

# words that have some error and should be changed
to_change = {'na#hexlīf':'naxlīf', 'na#ʕavār':'naʕavōr',
             'ya#higīd':'yagīd', 'ya#baʔ':'yavōʔ', 'te#sipēr':'tesaprī',
             'ta#hiškīv':'taškīv', 'la#xašāv':'laxšōv', 'le#nisā':'lenasōt',
             'yi#hayā':'tihiyī', 'na#ʕaṣā':'naʕaṣē', 'na#herʔā':'narʔē',
             'ni#qarāʔ':'niqrāʔ', 'ti#laqāx':'tilqāx', 'li#katāv':'liḳtōv',
             'ni#pagāš':'nifgōš', 'la#ʕaṣā':'laʕaṣōt', 'ti#hayā':'tihiyī',
             'li#qarāʔ':'liqrōʔ', 'ta#ṣam':'taṣīmi', 'to#ʔaḳāl':'toʔḳlī',
             'ti#racā':'tircī', 'ni#raxāc':'nirxāc', 'ne#yašāv':'nešēv',
             'ta#hifsīq':'tafsīqi', 'ni#qanā':'niqnē', 'te#qilēf':'teqalēf',
             'na#hilbīš':'nalbīš', 'ti#zarāq':'tizarēq', 'no#horīd':'norīd',
             'ta#higīd':'tagīdi', 'na#hitxīl':'natxīl', 'ti#natān':'titēn',
             'ne#ṣixēq':'neṣaxēq', 'le#hevīʔ':'lehavīʔ','ta#hevīʔ':'tavīʔi',
             'ti#lavāš':'titlabšī', 'ti#raʔā':'tirʔē', 'yi#macāc':'yimacōc',
             'ti#qarāʕ':'tiqrāʕ', 'ti#gamār':'tigmerī', 'yi#šaḳāv':'yišḳevū',
             'le#kisā':'lekasōt', 'yi#yašān':'yišān', 'yi#qarāʔ':'yiqrāʔ',
             'ti#hitkasā':'titkasī', 'ne#halāḳ':'nelēḳ', 'ne#sipēr':'nesapēr',
             'li#tafās':'litfōs', 'ti#naʕāl':'tinʕalī', 'ta#baʔ':'tavōʔi',
             'ti#histakēl':'tistaklī', 'le#hitraxēc':'lehitraxēc',
             'ne#ciyēr':'necayēr', 'le#qibēl':'leqabēl', 'ta#ʕaṣā':'taʕaṣī',
             'ti#laxāc':'tilxacī', 'te#yišēr':'teyiašrī', 'ti#matāx':'timtexī',
             'ya#ʕazār':'yaʕazōr', 'ya#ʕamād':'yaʕamōd', 'ta#hidbīq':'tadbiqī',
             'na#hidbīq':'nadbīq', 'ne#sidēr':'nesadēr', 'to#horīd':'torīdi',
             'ti#yašāv':'tišvī', 'na#ṣam':'naṣīm', 'ni#raʔā':'nirʔē',
             'ti#hištamēš':'tištamšī', 'le#higīd':'lehagīd',
             'ti#raxāc':'tirxāc', 'li#daxāf':'lidxōf', 'ni#šaʔāl':'nišʔāl',
             'ye#gerēd':'yegarēd', 'ta#hexzīq':'taxziqī', 'na#hiqlīṭ':'naqlīṭ',
             'ta#herʔā':'tarʔī', 'ta#himšīḳ':'tamšiḳī',
             'te#nigēv':'tenagevī', 'ta#hevīn':'tavīni', 'ti#daxāf':'tidxafī',
             'ti#safār':'tisperī', 'to#ʔamār':'tʔomrī', 'ni#natān':'nitēn',
             'ta#ʕamād':'taʕamdī', 'na#rac':'narūc', 'ya#hitʔīm':'yatʔīm',
             'te#kisā':'tekasī', 'te#ciyēr':'tecayrī', 'ti#šatāq':'tišteqī',
             'ti#marāx':'timrexī', 'ne#dibēr':'nedabēr',
             'ni#hitqašēr':'nitqašēr', 'ni#hitkonēn':'nitkonēn',
             'le#hišqā':'lehašqōt', 'ne#yadāʕ':'nedāʕ',
             'ti#šaḳāv':'tiškevī', 'no#ʔaḳāl':'noʔḳāl',
             'ti#hicṭarēḳ':'ticṭarḳī', 'li#darāḳ':'lidrōḳ',
             'te#sidēr':'tesadrī', 'la#nagāʕ':'lagāʕat', 'yi#raxāc':'yirxāc',
             'te#yarād':'terdī', 'te#niqā':'tenaqī', 'yi#ṭarāf':'yiṭrōf',
             'te#tiqēn':'tetaqnī', 'ti#yašān':'tišān', 'te#liqēq':'telaqēq',
             'te#yašāv':'tešavī', 'ta#ʕaf':'taʕūf', 'li#cavāʕ':'licvōʕ',
             'yi#natān':'yitēn', 'ta#hišxīl':'tašxilī', 'ne#kiftēr':'nekaftēr',
             'la#natān':'latēt', 'te#xiyēḳ':'texayḳī'}

# words that might come with 'ha_' in the beginning and need to be separated from it
he_hayedia_list = ['pēṭel', 'yam', 'ʔōḳel', 'ʕērev', 'sōhar', 'šimūš',
                   'yeladīm', 'malōn', 'bōqer', 'ʕērev', 'cohorāyim', 'šēxi',
                   'kavōd', 'xof', 'ʔārec', 'sēfer', 'miṭʕān', 'hulēdet']

wrong_words = set() # for check

def check_inds(parsed_sent):
    """
    Checks that the parsed sentence has all the indices
    """
    indices = [int(x[0]) for x in parsed_sent]
    return set(indices) == set(range(1,max(indices)+1))


def parse_conll(filename):
    """
    extract data from filename (conll format) and convert it into a conll-dictionary
    format, then process it
    :param filename:
    :return: list of all sentences, each sentence is in conll-dictionary
    format
    """
    file = open(filename, "r", encoding="utf-8")
    data = parse_incr(file)
    all_sents = []

    for j, sentence in enumerate(data):
        passed_ids = []
        cur_indx = 1  # index of
        while cur_indx < len(sentence.tokens):
            for i in range(len(sentence.tokens)):
                id = i+1
                cur_indx = id
                word = sentence[i]['form']

                if id in passed_ids:
                    continue

                # if word is written differently than it should
                if word in to_change:
                    sentence[i]['form'] = to_change[word]
                    word = to_change[word]

                # case of not separated token
                if "ADP+PRON" in sentence[i]['upostag']:
                    if word in not_to_split:
                        passed_ids.append(id)
                    else:
                        adp_part, pron_part = create_split_tokens(sentence.pop(i), id)
                        sentence.insert(i, adp_part)
                        sentence.insert(i+1, pron_part)
                        increase_ids_dependencies(id, sentence, [id, id+1])
                    break

                # replace the upostag of the negation words from 'adv' to 'PART'
                if word == 'loʔ' or word == 'ʔal':
                    if sentence[i]['upostag'] == 'ADV':
                        sentence[i]['upostag'] = 'PART'

                # case of empty_pronoun
                if "empty_pronoun" in word:
                    form_1, lemma_1, form_2, lemma_2, _ = separate_token(
                        sentence[i-1]['form'])
                    sentence[i-1]['form'], sentence[i-1]['lemma'] = form_1, lemma_1
                    sentence[i]['form'], sentence[i]['lemma'] = form_2, lemma_2
                    break

                # case of not separated tokens - special cases
                if (("_" in word  or '-' in word or '+' in word) and not word
                in not_to_split) or word in to_split:
                    if i+1 >= len(sentence.tokens) or not sentence[i+1]['form'] == 'empty_pronoun':
                        if word in non_split_to_unite:
                            new_word_sep = re.split('_|-|\+', word)
                            new_word = new_word_sep[0]+new_word_sep[1]
                            sentence[i]['form'], sentence[i]['lemma'] = \
                                new_word, new_word
                        else:
                            order = split_2_tokens(sentence, id)
                            increase_ids_dependencies(id, sentence, [id, id+1], order=order)
                        break

                # find all words with '#' in them
                if '#' in word and not word in to_change and not word in wrong_words:
                    print('wrong word: ' + word + " " + sentence.tokens.__str__())
                    wrong_words.add(word)

                # change 'iobj' to 'nmod', only if token has a dependent with label 'case'
                if sentence[i]['deprel'] == "iobj":
                    for token in sentence.tokens:
                        if token['head'] == sentence[i]['id'] and token['deprel'] == \
                                "case":
                            sentence[i]['deprel'] = "nmod"
                            break



        all_sents.append(sentence.serialize())

    # write corrected data to output file
    name_indx = filename.find('.conll10')
    out_file_name = filename[:name_indx] + '_out' + '.conll10'

    with open(out_file_name, 'w', encoding="utf-8") as file:
        for sent in all_sents:
            file.write(sent)

    # return the corrected data to enable one-file corrections
    return all_sents


def remove_token_from_sent(sent, id):
    """
    removes the token with the given id and updates the dependencies
    :param sent:
    :param id: id of the token to remove
    """
    sent.pop(id-1)
    for token in sent.tokens:
        if token['id'] > id:
            token['id'] -= 1
        if str(token['head']).isnumeric()and token['head'] > id:
            token['head'] -= 1


def check_dependent(sent, id):
    """
    check if any token in the given sentence has the specified id as
    it's head
    :param sent: sentence to search in
    :param id:
    :return: true if a dependency on id is found
    """
    for token in sent.tokens:
        if token['head'] == id:
            return True
    return False


def split_2_tokens(sent, id):
    """
    splits a token that has '_', '-' or '+' in it. Also splits special cases
    :param sent: sentence to split
    :param id: id of the original token to split
    :return:
    """
    orig_word = sent[id - 1]['form']
    orig_lemma = sent[id-1]['lemma']
    words_list = []
    if '_' in orig_word or '-' in orig_word or '+' in orig_word:
        words_list = re.split('_|-|\+', orig_word)
        word_1, word_2 = words_list[0], words_list[1]
    else:
        word_1, word_2 = orig_word, ""
    missing = False
    if len(words_list) > 2:
        missing = True

    upostag_1, upostag_2 = sent[id - 1]['upostag'], sent[id - 1]['upostag']
    xpostag_1, xpostag_2 = sent[id - 1]['xpostag'], sent[id - 1]['xpostag']
    deprel_1, deprel_2 = sent[id - 1]['deprel'], sent[id - 1]['deprel']
    form_1, lemma_1 = word_1, word_1
    form_2, lemma_2 = word_2, word_2
    """ order=1 means first token of the 2 depends on the second. order=2
    means that second token depends on the first. order=3 means that second
    token depends on a former verb in the sentence. order=4 means that first
    token depends on a former verb in the sentence. order=5 means that all
    tokens depend on the original head."""
    order = 1

    if word_1 == 'ha':
        upostag_1, xpostag_1 = 'DET', 'det'
        deprel_1 = 'det'
        if word_2=='ze' or word_2=='zoʔt' or word_2 == 'zōʔti' or word_2=='zo' or \
                        word_2=='ʔēle' or word_2 == 'zu':
            upostag_2, xpostag_2 = 'PRON', 'pro:dem'
        elif word_2 == 'yeladīm':
            lemma_2 = 'yēled'
        elif word_2 == 'baʔ':
            upostag_2, xpostag_2 = 'ADJ', 'adj'
        elif word_2 == 'baʔā':
            lemma_2 = 'baʔ'
            upostag_2, xpostag_2 = 'ADJ', 'adj'
        elif word_2 == 'šināyim':
            lemma_2 = 'šen'
        elif word_2 not in he_hayedia_list:
            print(word_1 + "***" + word_2 + " ERROR - unknown words to split!")

    elif word_1 == 'Yaʕēl' and word_2 == 'meṭayēlet':
        upostag_1, xpostag_1 = 'PROPN', 'n:prop'
        deprel_1 = 'nmod'
        form_2, lemma_2 = 'meṭayēlet', 'tiyēl'
        upostag_2, xpostag_2 = 'VERB', 'part'
        deprel_2 = 'ccomp'
        order = 3
    elif word_1 == 'naḳōn' and word_2 == 'meʔōd':
        upostag_1, xpostag_1 = 'INTJ', 'co'
        upostag_2, xpostag_2 = 'ADV', 'adv'
        deprel_2 = 'advmod'
        order = 2
    elif word_1 == 'šum':
        upostag_1, xpostag_1 = 'DET', 'det'
        deprel_1 = 'det'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif word_1 == 'ʕod' and word_2 == 'pāʕam':
        upostag_1, xpostag_1 = 'DET', 'X'
        upostag_2, xpostag_2 = 'NOUN', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'kol' and word_2 == 'pāʕam':
        upostag_1, xpostag_1 = 'DET', 'X'
        deprel_1 = 'discourse'
        upostag_2, xpostag_2 = 'NOUN', 'X'
    elif word_1 == 'kol' and word_2 == 'kaḳ':
        upostag_1, xpostag_1 = 'ADV', 'X'
        upostag_2, xpostag_2 = 'ADV', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'ʔaxār' and word_2 == 'kaḳ':
        upostag_1, xpostag_1 = 'ADV', 'X'
        upostag_2, xpostag_2 = 'ADV', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'ʔēyze' and word_2 == 'yōfi':
        upostag_1, xpostag_1 = 'DET', 'que'
        deprel_1 = 'det'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif word_1 == 'todā' and word_2 == 'rabā':
        upostag_1, xpostag_1 = 'INTJ', 'X'
        upostag_2, xpostag_2 = 'ADJ', 'X'
        deprel_2 = 'amod'
        order = 2
    elif word_1 == 'kedēy' and word_2 == 'še':
        upostag_1, xpostag_1 = 'PRON', 'X'
        upostag_2, xpostag_2 = 'SCONJ', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'ma' and word_2 == 'pitʔōm':
        upostag_1, xpostag_1 = 'PRON', 'X'
        upostag_2, xpostag_2 = 'ADV', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'yom' and word_2 == 'ʔexād':
        upostag_1, xpostag_1 = 'NOUN', 'X'
        upostag_2, xpostag_2 = 'ADJ', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'ʔaf' and word_2 == 'ʔexād':
        upostag_1, xpostag_1 = 'DET', 'qn'
        upostag_2, xpostag_2 = 'PRON', 'num'
        deprel_2 = 'compound'
        order = 2
    elif word_1 == 'telēḳ' and word_2 == 'leʔibūd':
        lemma_1 = 'halāḳ'
        upostag_1, xpostag_1 = 'VERB', 'X'
        upostag_2, xpostag_2 = 'NOUN', 'X'
        deprel_2 = 'compound:prt'
        order = 2
    elif word_1 == 'ʕod' and word_2 == 'meʕāṭ':
        upostag_1, xpostag_1 = 'DET', 'X'
        upostag_2, xpostag_2 = 'DET', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'ʕal' and word_2 == 'yad':
        upostag_1, xpostag_1 = 'ADP', 'prep'
        upostag_2, xpostag_2 = 'ADP', 'n'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'kmo' and word_2 == 'še':
        upostag_1, xpostag_1 = 'ADP', 'X'
        upostag_2, xpostag_2 = 'SCONJ', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'taʔ' and word_2 == 'ha' and len(words_list) > 2 and words_list[2].startswith('miṭʕān'):
        form_2, lemma_2 = 'ha_miṭʕān', 'ha_miṭʕān'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
        missing = False
    elif word_1 == 'gam' and word_2 == 'ken':
        upostag_1, xpostag_1 = 'DET', 'X'
        upostag_2, xpostag_2 = 'ADV', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'ʔaxrēy' or word_1 == 'ʔaxrē(y)' or word_1 == 'ʔaxarēy':
        upostag_1, xpostag_1 = 'ADP', 'prep'
        if word_2 == 'ha':
            deprel_1 = 'case'
            upostag_2, xpostag_2 = 'DET', 'det'
            if len(words_list) > 2:
                if words_list[2] == 'cohorāyim':
                    form_2, lemma_2 = 'ha_cohorāyim', 'ha_cohorāyim'
                    upostag_2, xpostag_2 = 'NOUN', 'n'
                else:
                    print('ERROR: one more word ' + words_list[2])
                missing = False
        elif word_2 == 'še':
            deprel_1 = 'case'
            upostag_2, xpostag_2 = 'SOCNJ', 'conj:subor'
            order = 5
        elif word_2 == 'ḳen':
            upostag_2, xpostag_2 = 'PRON', 'pro'
            deprel_2 = 'fixed'
            order = 2
        elif word_2 == 'ze':
            upostag_1, xpostag_1 = 'ADP', 'prep'
            upostag_2, xpostag_2 = 'PRON', 'X'
            deprel_2 = 'mwe'
            order = 2
        else:
            print(word_1 + "****" + word_2 + " ERROR - unknown words to split!")
    elif word_1 == 'ʔi' and word_2 == 'ʔefšār':
        upostag_1, xpostag_1 = 'ADV', 'X'
        deprel_1 = 'neg'
        upostag_2, xpostag_2 = 'AUX', 'X'
    elif word_1 == 'reʔšīt' and word_2 == 'kol':
        upostag_1, xpostag_1 = 'ADv', 'X'
        upostag_2, xpostag_2 = 'PRON', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'kol' and word_2 == 'minēy':
        upostag_1, xpostag_1 = 'DET', 'X'
        upostag_2, xpostag_2 = 'DET', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'yom' and 'hulēdet' in orig_lemma:
        lemma_2, form_2 = 'hulēdet', 'hulēdet'
        if 'ha' in orig_lemma:
            lemma_2, form_2 = 'ha_hulēdet', 'ha_hulēdet'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
        missing = False
    elif 'ʔaruxā' in orig_lemma:
        form_1, lemma_1 = 'ʔaruxāt', 'ʔaruxā'
        if 'cohorāyim' in orig_lemma:
            form_2, lemma_2 = 'cohorāyim', 'cohorāyim'
        elif 'bōqer' in orig_lemma:
            form_2, lemma_2 = 'bōqer', 'bōqer'
        elif 'ʕērev' in orig_lemma:
            form_2, lemma_2 = 'ʕērev', 'ʕērev'
        elif 'minxā' in orig_lemma:
            form_2, lemma_2 = 'minxā', 'minxā'
        else:
            print(orig_word + "ERROR: unknown words to split")
        missing = False
        if 'ha' in orig_lemma:
            form_2, lemma_2 = 'ha_' + form_2, 'ha_' + lemma_2
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'beyt':
        lemma_1 = 'bāyit'
        if 'yeladīm' in orig_lemma:
            form_2, lemma_2 = 'yeladīm', 'yelēd'
        elif 'sōhar' in orig_lemma:
            form_2, lemma_2 = 'sōhar', 'sōhar'
        elif 'šimūš' in orig_lemma:
            form_2, lemma_2 = 'šimūš', 'šimūš'
        elif word_2 == 'malōn':
            form_2, lemma_2 = 'malōn', 'malōn'
        elif 'šēxi' in orig_lemma:
            form_2, lemma_2 = 'šēxi', 'šēxi'
        elif 'sēfer' in orig_lemma:
            form_2, lemma_2 = 'sēfer', 'sēfer'
        else:
            print('ERROR: ' + orig_word + ' was not split')
        missing = False
        if word_2.startswith('ha'):
            form_2, lemma_2 = 'ha_' + form_2, 'ha_' + lemma_2
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'xadār' and 'ʔōḳel' in orig_lemma:
        lemma_1 = 'xēder'
        form_2, lemma_2 = 'ʔōḳel', 'ʔōḳel'
        if word_2.startswith('ha'):
            form_2, lemma_2 = 'ha_' + form_2, 'ha_' + lemma_2
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
        missing = False
    elif orig_lemma == 'pinā+xay':
        form_1, lemma_1 = 'pināt', 'pinā'
        form_2, lemma_2 = 'xay', 'xay'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
        missing = False
    elif orig_lemma == 'ner+šabāt':
        form_1, lemma_1 = 'nerōt', 'ner'
        form_2, lemma_2 = 'šabāt', 'šabāt'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
        missing = False
    elif word_1 == 'Qol' and word_2 == 'dodī':
        upostag_1, xpostag_1 = 'NOUN', 'qn'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'xuc' and (word_2 == 'me' or word_2 == 'mi'):
        upostag_1, xpostag_1 = 'ADV', 'adv'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'ADP', 'prep'
        deprel_2 = 'case'
        order = 5
    elif (word_1 == 'ben' or word_1 == 'bat') and (word_2.startswith('dod') or word_2
        == 'dōda'):
        lemma_2, form_2 = 'dod', 'dod'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif (word_1 == 'ṣfat' or word_1 == 'xof') and word_2.startswith('ha'):
        lemma_1 = 'ṣafā'
        if word_1 == 'xof':
            lemma_1 = 'xof'
        if len(words_list) > 2 and words_list[2].startswith('yam'):
            form_2, lemma_2 = 'ha_yam', 'ha_yam'
        else:
            print(orig_word + " ERROR - unknown words to split!")
        missing = False
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'mic' and word_2.startswith('pēṭel'):
        lemma_2, form_2 = 'pēṭel', 'pēṭel'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'mic' and word_2 == 'ha':
        upostag_1, xpostag_1 = 'NOUN', 'n'
        if len(words_list) > 2:
            form_2, lemma_2 = 'ha_pēṭel', 'ha_pēṭel'
            upostag_2, xpostag_2 = 'NOUN', 'n'
            deprel_2 = 'nmod:smixut'
            order = 2
        else:
            print(orig_word + " ERROR: uknown words to split")
        missing = False
    elif word_1 == 'neyār' and word_2.startswith('ṭuʔalēṭ'):
        form_2, lemma_2 = 'ṭuʔalēṭ', 'ṭuʔalēṭ'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'ʕad' and word_2 == 'še':
        upostag_1, xpostag_1 = 'ADP', 'adp'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'SCONJ', 'conj:subor'
        deprel_2 = 'mark'
        order = 5
    elif word_1 == 'midēy' and word_2 == 'pāʕam':
        upostag_1, xpostag_1 = 'ADV', 'adv'
        upostag_2, xpostag_2 = 'ADV', 'adv'
        deprel_2 = 'dep'
        order = 2
    elif word_1 == 'ʕod' and word_2 == 'qcat':
        upostag_1, xpostag_1 = 'ADV', 'qn'
        upostag_2, xpostag_2 = 'ADV', 'qn'
        deprel_2 = 'advmod'
        order = 2
    elif word_1 == 'bišvīl' and word_2 == 'še':
        upostag_1, xpostag_1 = 'SCONJ', 'X'
        upostag_2, xpostag_2 = 'SCONJ', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'ʕod' and word_2 == 'loʔ':
        upostag_1, xpostag_1 = 'ADV', 'X'
        upostag_2, xpostag_2 = 'ADV', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'kos' and word_2.startswith('te'):
        form_2, lemma_2 = 'te', 'te'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'šuv' and word_2 == 'pāʕam':
        upostag_1, xpostag_1 = 'ADV', 'X'
        upostag_2, xpostag_2 = 'NOUN', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'rofēʔ' and word_2 == 'ha':
        missing = False
        if len(words_list) > 2 and sent[id-1]['lemma'] == 'rofēʔ+ha+šen':
            upostag_1, xpostag_1 = 'NOUN', 'n'
            form_2, lemma_2 = 'ha_šināyim', 'ha_šināyim'
            upostag_2, xpostag_2 = 'NOUN', 'n'
            deprel_2 = 'nmod:smixut'
            order = 2
        else:
            print(orig_word + " ERROR - unknown words to split!")
        missing = False
    elif word_1 == 'ha' and word_2.startswith('šināyim'):
        form_1, lemma_1 = 'šenāyim', 'šen'
        upostag_1, xpostag_1 = 'DET', 'det'
        deprel_1 = 'det'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif word_1 == 'rofēʔ' and word_2.startswith('šen'):
        form_2, lemma_2 = 'šenāyim', 'šen'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
        missing = False
    elif word_1 == 'lifnēy' and word_2 == 'še':
        upostag_1, xpostag_1 = 'ADP', 'prep'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'SCONJ', 'X'
        order = 5
    elif word_1 == 'ba' and word_2 == 'makom':
        upostag_1, xpostag_1 = 'ADP', 'prep'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif word_1 == 'lamrōt' and word_2 == 'še':
        upostag_1, xpostag_1 = 'ADP', 'prep'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'SCONJ', 'conj:subor'
        order = 5
    elif word_1 == 'yafē' and word_2 == 'meʔōd':
        upostag_1, xpostag_1 = 'ADV', 'X'
        upostag_2, xpostag_2 = 'ADV', 'X'
        deprel_2 = 'advmod'
        order = 2
    elif word_1 == 'ben' and word_2 == 'ʔadām':
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'ʔaf' and word_2 == 'pāʕam':
        upostag_1, xpostag_1 = 'DET', 'X'
        upostag_2, xpostag_2 = 'NOUN', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'gvinā' and word_2 == 'cehubā':
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'ADJ', 'adj'
        deprel_2 = 'compound'
        order = 2
    elif word_1 == 'yotēr' and word_2 == 'midāy':
        upostag_1, xpostag_1 = 'ADV', 'adv'
        upostag_2, xpostag_2 = 'ADV', 'adv'
        deprel_2 = 'dep'
        order = 2
    elif word_1 == 'xuc' and word_2 == 'mizē':
        form_1, lemma_1 = 'xuc_mi', 'xuc_mi'
        upostag_1, xpostag_1 = 'ADV', 'adv'
        deprel_1 = 'case'
        form_2, lemma_2 = 'ze', 'ze'
        upostag_2, xpostag_2 = 'PRON', 'pro'
    elif word_1 == 'lāyla' and word_2 == 'ṭov':
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'X', 'X'
        deprel_2 = 'mwe'
        order = 2
    elif word_1 == 'tapuxēy' and word_2 == 'ʔadamā':
        form_1, lemma_1 = 'tapuxēy', 'tapūax'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'halāḳ' and word_2 == 'leʔibūd':
        upostag_1, xpostag_1 = 'VERb', 'X'
        upostag_2, xpostag_2 = 'NOUN', 'X'
        deprel_2 = 'compound:prt'
        order = 2
    elif word_1 == 'zḳuḳīt' and word_2 == 'magdēlet':
        upostag_1, xpostag_1 = 'NOUN', 'X'
        upostag_2, xpostag_2 = 'NOUN', 'X'
        deprel_2 = 'nmod'
        order = 2
    elif ((word_1 == 'ʔaxāt' or word_1 == 'šeš') and word_2 == 'ʕeṣrē') or (word_1
            == 'tšaʕ' and word_2 == 'meʔōt'):
        upostag_1, xpostag_1 = 'NUM', 'num'
        upostag_2, xpostag_2 = 'NUM', 'num'
        deprel_2 = 'flat'
        order = 2
    elif word_1 == 'raq' and word_2 == 'rēgaʕ':
        upostag_1, xpostag_1 = 'ADV', 'adv'
        deprel_1 = 'advmod'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif word_1 == 'pāʕam' and word_2 == 'ʔaxāt':
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NUM', 'num'
        deprel_2 = 'nummod'
        order = 2
    elif word_1 == 'biglāl' and word_2 == 'še':
        upostag_1, xpostag_1 = 'ADP', '_'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'SCONJ', 'conj:subor'
        deprel_2 = 'mark'
        order = 5
    elif word_1 == 'beḳōl' and word_2 == 'zoʔt':
        form_1, lemma_1 = 'be', 'be'
        form_2, lemma_2 = 'ḳōl_zoʔt', 'ḳōl_zoʔt'
        upostag_1, xpostag_1 = 'ADP', '_'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'PRON', 'pro'
    elif word_1 == 'ḳōl' and word_2 == 'zoʔt':
        upostag_1, xpostag_1 = 'DET', 'det'
        deprel_1 = 'dep'
        upostag_2, xpostag_2 = 'PRON', 'pro'
    elif word_1 == 'Dirā' and word_2 == 'lehaṣkīr':
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'VERB', '_'
        deprel_2 = 'advmod:inf'
        order = 2
    elif word_1 == 'mocēʔ' and word_2 == 'xen':
        upostag_1, xpostag_1 = 'VERB', '_'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'obj'
        order = 2
    elif (word_1 == 'ṣamt' or word_1 == 'taṣīmi' or word_1 == 'laṣīm') and word_2 == 'lev':
        upostag_1, xpostag_1 = 'VERB', '_'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'obj'
        order = 2
    elif word_1 == 'kol' and word_2 == 'ha' and len(words_list) > 2 and words_list[2] == 'kavōd':
        form_2, lemma_2 = 'ha_kavōd', 'ha_kavōd'
        upostag_1, xpostag_1 = 'DET', 'det'
        deprel_1 = 'det'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        missing = False
    elif word_1 == 'ʔasirēy' and word_2 == 'todā':
        lemma_2 = 'ʔasirīm'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'ʔeyḳ' and word_2 == 'še':
        upostag_1, xpostag_1 = 'ADV', 'adv'
        upostag_2, xpostag_2 = 'SCONJ', 'conj:subor'
        deprel_2 = 'dep'
        order = 2
    elif word_1 == 'kāma' and word_2 == 'še':
        upostag_1, xpostag_1 = 'DET', 'det'
        upostag_2, xpostag_2 = 'SCONJ', 'conj:subor'
        deprel_2 = 'dep'
        if sent[sent[id-1]['head']-1]['upostag'] == 'VERB':
            deprel_2 = 'mark'
        order = 5
    elif word_1 == 'gan' and word_2.startswith('šaʕašuʕīm'):
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'compound'
        order = 2
    elif word_1 == 'kadūr' and word_2.startswith('ha'):
        if len(words_list) > 2 and words_list[2] == 'ʔārec':
            form_2, lemma_2 = 'ha_ʔārec', 'ha_ʔārec'
        else:
            print(orig_word + " ERROR - unknown words to split!")
        missing = False
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'bedēreḳ' and word_2 == 'klal':
        form_1, lemma_1 = 'be', 'be'
        form_2, lemma_2 = 'dēreḳ_klal', 'dēreḳ_klal'
        upostag_1, xpostag_1 = 'ADP', '_'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'fixed'
        order = 2
    elif word_1 == 'dēreḳ' and word_2 == 'klal':
        upostag_1, xpostag_1 = 'ADP', '_'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_1, deprel_2 = 'fixed', 'fixed'
        order = 5
    elif word_1 == 'keywān' and word_2 == 'še':
        upostag_1, xpostag_1 = 'SCONJ', '_'
        upostag_2, xpostag_2 = 'SCONJ', '_'
        deprel_1, deprel_2 = 'case', 'dep'
        if sent[sent[id-1]['head']-1]['upostag'] == 'VERB':
            deprel_2 = 'mark'
        order = 5
    elif word_1 == 'ma' and word_2 == 'zoʔt' and len(words_list) > 2 and words_list[2] \
            == 'ʔomēret':
        form_1, lemma_1 = 'ma_zoʔt', 'ma_zoʔt'
        form_2, lemma_2 = 'ʔomēret', 'ʔomēret'
        upostag_1, xpostag_1 = 'ADV', '_'
        upostag_2, xpostag_2 = 'VERB', '_'
        deprel_2 = 'nsubj'
        order = 2
        missing = False
    elif word_1 == 'ma' and word_2 == 'zoʔt':
        upostag_1, xpostag_1 = 'ADV', '_'
        upostag_2, xpostag_2 = 'PRON', '_'
        deprel_1, deprel_2 = 'obj', 'nsubj'
        order = 5
    elif word_1 == 'Gan' and word_2 == 'bīlu':
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'be' and word_2 == 'sofō':
        if len(words_list) > 2:
            if 'šel' in words_list and 'davār' in words_list:
                form_1, lemma_1 = 'be_sofō', 'be_sofō'
                form_2, lemma_2 = 'šel_davār', 'šel_davār'
                upostag_1, xpostag_1 = 'Noun', 'n'
                upostag_2, xpostag_2 = 'NOUN', 'n'
                deprel_2 = 'nmod:poss'
                order = 2
            else: print(orig_word + " ERROR: unknown words to split")
        else:
            form_1, lemma_1 = 'ba', 'ba'
            form_2, lemma_2 = 'sof_šelō', 'sof_šelō'
            upostag_1, xpostag_1 = 'ADP', '_'
            deprel_1 = 'case'
            upostag_2, xpostag_2 = 'NOUN', 'n'
        missing = False
    elif word_1 == 'šel' and word_2 == 'davār':
        upostag_1, xpostag_1 = 'PART', '_'
        deprel_1 = 'case:gen'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif word_1 == 'sof' and word_2 == 'šelō':
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'ADP+PRON', 'prep:pro'
        deprel_2 = 'nmod:poss'
        order = 2
    elif word_1 == 'ʔēlaʔ' and word_2 == 'še':
        upostag_1, xpostag_1 = 'CCONJ', '_'
        upostag_2, xpostag_2 = 'SCONJ', '_'
        deprel_1, deprel_2 = 'cc', 'mark'
        order = 5
    elif word_1 == 'me' and word_2 == 'hatxalā':
        upostag_1, xpostag_1 = 'ADP', '_'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif (orig_word == 'Beyt_Lēxem' or orig_word == 'Nevē_cēdeq' or orig_word ==
        'ʕeyn_xarōd'):
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod:smixut'
        order = 2
    elif word_1 == 'la' and word_2 == 'deʕā':
        upostag_1, xpostag_1 = 'ADP', ''
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif word_1 == 'xuc' and word_2 == 'le' and len(words_list) > 2 and words_list[2] \
            == 'ʔārec':
        form_2, lemma_2 = 'la_ʔārec', 'la_ʔārec'
        upostag_1, xpostag_1 = 'NOUN', 'n'
        upostag_2, xpostag_2 = 'NOUN', 'n'
        deprel_2 = 'nmod'
        order = 2
        missing = False
    elif word_1 == 'la' and word_2 == 'ʔārec':
        form_1, lemma_1 = 'le_ha', 'le_ha'
        upostag_1, xpostag_1 = 'ADP', '_'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'NOUN', 'n'
    elif word_1 == 'le' and word_2 == 'ha':
        form_2, lemma_2 = '~ha', '~ha'
        upostag_1, xpostag_1 = 'ADP', '_'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'DET', 'det'
        deprel_2 = 'det:def'
        order = 5
    elif word_1 == 'halōḳ' and word_2 == 'we' and len(words_list) > 2 and words_list[
        2] == 'xazōr':
        form_2, lemma_2 = 'we_xazōr', 'we_xazōr'
        upostag_1, xpostag_1 = 'ADV', 'adv'
        upostag_2, xpostag_2 = 'ADV', 'adv'
        deprel_2 = 'conj'
        order = 2
        missing = False
    elif word_1 == 'we' and word_2 == 'xazōr':
        upostag_1, xpostag_1 = 'CCONJ', '_'
        deprel_1 = 'cc'
        upostag_2, xpostag_2 = 'ADV', 'adv'
    elif word_1 == 'mi' and word_2 == 'mizmān':
        upostag_1, xpostag_1 = 'ADP', '_'
        upostag_2, xpostag_2 = 'ADV', 'adv'
        deprel_2 = 'fixed'
        order = 2
    elif word_1 == 'še' and word_2 == 'kmotēḳ':
        form_2, lemma_2 = 'kmo_ʔat', 'kmo_ʔat'
        upostag_1, xpostag_1 = 'SCONJ', '_'
        upostag_2, xpostag_2 = 'SCONJ', '_'
        deprel_1 = 'mark'
        deprel_2 = 'case'
        order = 5
    elif word_1 == 'kmo' and word_2 == 'ʔat':
        upostag_1, xpostag_1 = 'ADP', 'prep'
        deprel_1 = 'case'
        upostag_2, xpostag_2 = 'PRON', 'pro'


    elif word_2 == "":
        if word_1 == 'leʕacmāh' or word_1 == 'leʕacmī' or word_1 == 'leʕacmō':
            form_1, lemma_1 = 'le', 'le'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            deprel_1 = 'case'
            form_2, lemma_2 = word_1[2:], word_1[2:]
            upostag_2, xpostag_2 = 'PRON', 'pro'
        elif word_1 == 'ba':
            form_1, lemma_1 = 'be', 'be'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            form_2, lemma_2 = '~ha', '~ha'
            upostag_2, xpostag_2 = 'DET', 'det'
            deprel_2 = 'det'
            order = 5
        elif word_1 == 'svivā':
            form_1, lemma_1 = 'sviv', 'sviv'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            deprel_1 = 'case'
            form_2, lemma_2 = 'hi?', 'hi?'
            upostag_2, xpostag_2 = 'PRON', 'pro'
        elif word_1 == 'bešum':
            form_1, lemma_1 = 'be', 'be'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            deprel_1 = 'case'
            form_2, lemma_2 = 'šum', 'šum'
            upostag_2, xpostag_2 = 'ADP', 'X'
        elif word_1 == 'xemdatī':
            form_1, lemma_1 = 'xemdā', 'xemdā'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            form_2, lemma_2 = 'šelī', 'šelī'
            upostag_2, xpostag_2 = 'ADP+PRON', 'prep:pro'
            deprel_2 = 'nmod:poss'
            order = 2
        elif word_1 == 'ledaʕatī':
            form_1, lemma_1 = 'la_deʕā', 'la_deʕā'
            form_2, lemma_2 = 'šelī', 'šelī'
            upostag_1, xpostag_1 = 'NOUN', 'n'
            upostag_2, xpostag_2 = 'ADP+PRON', 'prep:pro'
            deprel_2 = 'nmod:poss'
            order = 2
        elif word_1 == 'beʕacmēḳ':
            form_1, lemma_1 = 'be', 'be'
            form_2, lemma_2 = 'ʕacmēḳ', 'ʕacmēḳ'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            deprel_1 = 'case'
            upostag_2, xpostag_2 = 'PRON', 'pro'
        elif word_1 == 'beʔemēt':
            form_1, lemma_1 = 'be', 'be'
            form_2, lemma_2 = 'ʔemēt', 'ʔemēt'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            deprel_1 = 'case'
            upostag_2, xpostag_2 = 'NOUN', 'n'
        elif word_1 == 'beteʔavōn':
            form_1, lemma_1 = 'be', 'be'
            form_2, lemma_2 = 'ʔemēt', 'ʔemēt'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            deprel_1 = 'case'
            upostag_2, xpostag_2 = 'NOUN', 'n'
        elif word_1 == 'beteʔavōn':
            form_1, lemma_1 = 'be', 'be'
            form_2, lemma_2 = 'teʔavōn', 'teʔavōn'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            deprel_1 = 'case'
            upostag_2, xpostag_2 = 'NOUN', 'n'
        elif word_1 == 'bezehirūt':
            form_1, lemma_1 = 'be', 'be'
            form_2, lemma_2 = 'zehirūt', 'zehirūt'
            upostag_1, xpostag_1 = 'ADP', 'prep'
            upostag_2, xpostag_2 = 'NOUN', 'n'
            deprel_2 = 'mwe'
            order = 2

        else:
            print(orig_word + " ERROR - unknown words to split!")
    else:
        print(orig_word + " ERROR - unknown words to split!")
    if missing:
        print('Might have missing word: ' + orig_lemma)

    # create new tokens and remove the original token
    token_1 = sent.pop(id-1)
    token_2 = token_1.copy()

    token_1['lemma'] = lemma_1
    token_1['form'] = form_1
    token_1['upostag'] = upostag_1
    token_1['xpostag'] = xpostag_1
    token_1['deprel'] = deprel_1

    if order == 1 or order == 3:
        token_1['head'] = id + 1
    elif order == 4:
        token_1['head'] = get_verb_id(sent)
    if str(token_1['head']).isnumeric() and token_1['head'] > id and not (order == 1 or
                 order == 3):
        token_1['head'] += 1

    token_2['lemma'] = lemma_2
    token_2['form'] = form_2
    token_2['upostag'] = upostag_2
    token_2['xpostag'] = xpostag_2
    token_2['id'] = id + 1
    token_2['deprel'] = deprel_2

    if order == 2 or order == 4:
        token_2['head'] = id
    elif order == 3:
        token_2['head'] = get_verb_id(sent)
    else:
        if str(token_2['head']).isnumeric() and token_2['head'] > id and not (order==2
                                                      or order == 4):
            token_2['head'] += 1

    sent.insert(id-1, token_1)
    sent.insert(id, token_2)
    return order


def get_verb_id(sent):
    """
    :param sent: sentence
    :return: id of first verb in the sentence
    """
    for token in sent.tokens:
        if token['upostag'] == 'VERB':
            return token['id']


def increase_ids_dependencies(id, sentence, ids_to_ignore, order=1):
    """
    to use in case of one token that was added. Increases all relevant id-s
    and dependencies
    :param id: id of the row after which another row was added
    :param order: if order=1 then every token that depended on id will now depend on
    id+1. if order=2 then id will stay the head of every token that depended on it.
    """
    for i in range(len(sentence.tokens)):
        # change id for relevant tokens
        if i > id:
            sentence[i]['id'] += 1
        # change dependencies for relevant tokens
        if sentence[i]['head'] != None and str(sentence[i]['head']).isnumeric():
            if order == 1 and sentence[i]['head'] >= id and not i+1 in ids_to_ignore:
                # everyone that depended on id will now depend on id+1
                sentence[i]['head'] += 1
            elif order == 2 and sentence[i]['head'] > id and not i+1 in ids_to_ignore:
                # id stays the main head for everyone that depended on it
                sentence[i]['head'] += 1

def create_split_tokens(token, id):
    """
    creates two tokens given a token that has to be split by 'ADP+PRON'
    :param token: the original token that should be split
    :param id: the id of the token to split
    :return: first token, second token
    """
    adp_part = token.copy()
    pron_part = adp_part.copy()
    parameters = separate_token(token['form'])

    adp_part['upostag'] = 'ADP'
    adp_part['xpostag'] = 'prep'
    adp_part['head'] = id + 1
    adp_part['deprel'] = parameters[4]
    adp_part['form'], adp_part['lemma'] = parameters[0], parameters[1]

    pron_part['upostag'] = 'PRON'
    pron_part['xpostag'] = 'pro:person'
    pron_part['form'], pron_part['lemma'] = parameters[2], parameters[3]
    pron_part['id'] += 1
    if str(pron_part['head']).isnumeric() and pron_part['head'] > id:
        pron_part['head'] += 1

    return adp_part, pron_part


def separate_token(token):
    """
    separates prepositions that include possessive pronouns and should be split
    :param token: tokens that are labeled as "ADP+PRON"
    :return: list of 5 elements with the following order: [form1, lemma1,
    form2, lemma2, deprel_1]. The elements ending with 1 refer to
    the first part of the split token, and the elements ending with 2 refer
    to the second.
    """
    str_token = token
    dict_le = {'laḳ':'ʔat', 'li':'ʔanī', 'lo':'huʔ', 'lahēm':'hem',
                     'lahēn':'hen', 'lah':'hiʔ', 'leḳā':'ʔatā', 'lānu':'ʔanāxnu',
                     'laḳēm':'ʔatēm'}
    if str_token in dict_le:
        return ['le', 'le', dict_le[str_token], dict_le[str_token], 'case']

    dict_bishvil = {'bišvilō':'huʔ', 'bišvilēḳ':'ʔat', 'bišvilḳā':'ʔatā',
                    'bišvilāh':'hiʔ'}
    if str_token in dict_bishvil:
        return ['bišvil', 'bišvil', dict_bishvil[str_token], dict_bishvil[str_token], 'case']

    dict_leacmo = {'leʕacmāh':'ʕacmāh', 'leʕacmō':'ʕacmō', 'leʕacmī':'ʕacmī'}
    if str_token in dict_leacmo:
        return ['le', 'le', dict_leacmo[str_token], dict_leacmo[str_token], 'case']

    dict_shel = {'šelō':'huʔ', 'šelāḳ':'ʔat', 'šelānu':'ʔanāxnu',
                 'šelī':'ʔanī', 'šelāh':'hiʔ', 'šelahēm':'hemʔ',
                 'šelaḳēm':'ʔatēm'}
    if str_token in dict_shel:
        return ['šel', 'šel', dict_shel[str_token], dict_shel[str_token], 'case']

    dict_be = {'bahēm':'hem', 'bo':'huʔ', 'baḳ':'ʔat', 'bah':'hiʔ', 'bi':'ʔanī' }
    if str_token in dict_be:
        return ['be', 'be', dict_be[str_token], dict_be[str_token], 'case']

    dict_im = {'ʔitō':'huʔ', 'ʔitī':'ʔanī', 'ʔitāh':'hiʔ', 'ʔitāḳ':'ʔat',
               'ʔitḳēm':'ʔatēm', 'ʔitānu':'ʔanāxnu'}
    if str_token in dict_im:
        return ['ʕim', 'ʕim', dict_im[str_token], dict_im[str_token], 'case:gen']

    dict_el = {'ʔelāyiḳ':'ʔat','ʔelāyw':'huʔ', 'ʔelāy':'ʔanī','ʔelēynu':'ʔanāxnu'}
    if str_token in dict_el:
        return ['ʔel', 'ʔel', dict_el[str_token], dict_el[str_token], 'case']

    dict_me = {'mimēḳ':'ʔatēm','mimēno':'huʔ','mimēni':'ʔanī','mimēna':'hiʔ',
               'mimḳā':'ʔatā', 'mimēnu':'huʔ'}
    if str_token in dict_me:
        return ['me', 'me', dict_me[str_token], dict_me[str_token], 'case']

    dict_al = {'ʕalāyiḳ':'ʔat','ʕalāy':'ʔanī','ʕalēyha':'hiʔ','ʕalāyw':'huʔ','ʕaleyhēn':'hen'}
    if str_token in dict_al:
        return ['ʕal', 'ʕal', dict_al[str_token], dict_al[str_token], 'case']

    dict_et = {'ʔotō':'huʔ','ʔotām':'hem', 'ʔotān':'hen', 'ʔotāh':'hiʔ',
               'ʔotī':'ʔanī','ʔotāḳ':'ʔat', 'ʔotḳā':'ʔatā','ʔotānu':'ʔanāxnu',}
    if str_token in dict_et:
        return ['ʔet', 'ʔet', dict_et[str_token], dict_et[str_token], 'case']

    dict_al_yad = {'ʕal_yadāh':'hiʔ', 'ʕal_yadēḳ':'ʔat', 'ʕal_yadī':'ʔanī',}
    if str_token in dict_al_yad:
        return ['ʕal_yad', 'ʕal_yad', dict_al_yad[str_token], dict_al_yad[str_token], 'case']

    dict_beyn = {'beyneyhēm':'hem','beynēnu':'ʔanāxnu'}
    if str_token in dict_beyn:
        return ['beyn', 'beyn', dict_beyn[str_token], dict_beyn[str_token], 'case']

    dict_ecel = {'ʔeclī':'ʔanī','ʔeclō':'huʔ','ʔeclēnu':'ʔanāxnu',
                 'ʔecleḳēm':'ʔatēm', 'ʔeclēḳ':'ʔat'}
    if str_token in dict_ecel:
        return ['ʔecēl', 'ʔecēl', dict_ecel[str_token], dict_ecel[str_token], 'case']

    dict_micad = {'micidēḳ':'ʔat', 'micidō':'huʔ'}
    if str_token in dict_micad:
        return ['micād', 'micād', dict_micad[str_token], dict_micad[str_token], 'case']

    if str_token == 'bimqomō':
        return ['bimqōm', 'bimqōm', 'huʔ', 'huʔ', 'nmod']

    if str_token == 'svivō':
        return ['sviv', 'sviv', 'huʔ', 'huʔ', 'case']

    if str_token == 'mulēḳ':
        return ['mul', 'mul', 'ʔat', 'ʔat', 'case']

    if str_token == 'kamōhu':
        return ['kmo', 'kmo', 'huʔ', 'huʔ', 'case']

    if str_token == 'letoḳō':
        return ['letōḳ', 'letōḳ', 'huʔ', 'huʔ', 'case']

    else:
        print(str(str_token) + " ERROR - unknown token to split!")
        return [str_token, str_token] + ['error']*3


def parse_directory(dir_name):
    """
    activate the processing function on each conll10 file in the directory dir
    :param dir_name: the directory to search files
    """
    for filename in os.listdir(dir_name):
        if filename.endswith('.conll10') and not filename.endswith('out.conll10'):
            parse_conll(os.path.join(dir_name, filename))


def main():
    optparser = optparse.OptionParser()
    optparser.add_option("-d", "--dir", dest="path",
                         default="manually_annotated\Heb\in", help="directory with the "
                                                               ".conll10 files to "
                                                               "process, or a .conll10 "
                                                               "file")
    optparser.add_option("-i", "--is_dir", dest="is_dir", default=True, help="true if "
                                                                             "the input path is a directory")
    (opts, _) = optparser.parse_args()
    if opts.is_dir:
        parse_directory(opts.path)
    else:
        parse_conll(opts.path)


if __name__ == "__main__":
    main()