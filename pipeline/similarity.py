# -*- coding: utf-8 -*-
import pandas as pd

import codecs
import os
import pymorphy2
from string import ascii_lowercase, digits, whitespace
from sklearn.metrics.pairwise import cosine_similarity
import logging
import numpy as np
import gensim
from gensim.models import Word2Vec

os.getcwd()


morph = pymorphy2.MorphAnalyzer()

cyrillic = u"абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

allowed_characters = ascii_lowercase + digits + cyrillic + whitespace



word2vec = Word2Vec.load(os.getcwd()+"../../big_word2vec/big_word2vec_model_CBOW")
word2vec.wv.init_sims()

def complex_preprocess(text, additional_allowed_characters = "+#"):
    return ''.join([character if character in set(allowed_characters+additional_allowed_characters) else ' ' for character in text.lower()]).split()


def lemmatize(tokens, filter_pos):
    '''Produce normal forms for russion words using pymorphy2
    '''
    lemmas = []
    tagged_lemmas = []
    for token in tokens:
        parsed_token = morph.parse(token)[0]
        norm = parsed_token.normal_form
        pos = parsed_token.tag.POS
        if pos is not None:
            if pos not in filter_pos:
                lemmas.append(norm)
                tagged_lemmas.append(norm + "_" + pos)
        else:
            lemmas.append(token)
            tagged_lemmas.append(token+"_")

    return lemmas, tagged_lemmas


def process_text(full_text, filter_pos=("PREP", "NPRO", "CONJ")):
    '''Process a single text and return a processed version
    '''
    single_line_text = full_text.replace('\n',' ')
    preprocessed_text = complex_preprocess(single_line_text)
    lemmatized_text, lemmatized_text_pos_tags = lemmatize(preprocessed_text, filter_pos=filter_pos)

    return { "full_text" : full_text,
    "single_line_text": single_line_text,
    "preprocessed_text": preprocessed_text,
    "lemmatized_text": lemmatized_text,
    "lemmatized_text_pos_tags": lemmatized_text_pos_tags}


def process_text_documents(text_files_directory, filter_pos=("PREP", "NPRO", "CONJ")):
    for file in os.listdir(text_files_directory):
        if os.path.isfile(os.path.join(text_files_directory, file)):
            with codecs.open(os.path.join(text_files_directory, file), encoding='utf-8') as f:
                full_text = f.read()
                doc_dict = process_text(full_text)
                doc_dict["filename"] = file
                yield doc_dict


def word_averaging(wv, words):
    all_words, mean = set(), []

    for word in words:
        if isinstance(word, np.ndarray):
            mean.append(word)
        elif word in wv.vocab:
            mean.append(wv.syn0norm[wv.vocab[word].index])
            all_words.add(wv.vocab[word].index)

    if not mean:
        logging.warning("cannot compute similarity with no input %s", words)
        # FIXME: remove these examples in pre-processing
        return np.zeros(wv.vector_size, )

    mean = gensim.matutils.unitvec(np.array(mean).mean(axis=0)).astype(np.float32)
    return mean


def word_averaging_list(wv, text_list):
    return np.vstack([word_averaging(wv, review) for review in text_list])


def get_vectorized_avg_w2v_corpus(corpus, model):
    documents = corpus['processed_text'].tolist()

    document_vectors = [word_averaging(model, document) for document in documents]
    clean_corpus = corpus
    clean_corpus['vectors'] = pd.Series(document_vectors).values

    return clean_corpus


def most_similar(infer_vector, vectorized_corpus, own_code=[0], topn=10):
    if own_code[0] != 0:
        df_sim = pd.DataFrame()
        for label in own_code:
            df_sim_label = vectorized_corpus[vectorized_corpus['labels'] == label]
            df_sim = pd.concat([df_sim, df_sim_label], ignore_index=False)
            print('own=' + own[0])
    else:
        df_sim = vectorized_corpus

    df_sim['sc'] = vectorized_corpus['vectors'].apply(
        lambda v: cosine_similarity([infer_vector], [v.tolist()])[0, 0])
    df_sim = df_sim.sort_values(by='sc', ascending=False).head(n=topn)
    return df_sim


def similarity(vacancies, standards, own=True):
    df_result = pd.DataFrame(columns=['vac_text', 'prof_text', 'prof_type',
                                      'prof_code', 'sc', 'vector_sim', 'id_profstandard_part',
                                      'id_matching', 'id_vacancy_part'],
                             index=None)
    match_index = 0
    own_code = [0]
    for index, sample in tqdm(vacancies.iterrows()):
        if own is True:
            labels = sample['labels']
            own_code = labels.split(',')
        similar_docs = most_similar(sample['vectors'], standards, own_code, topn=5)[
            ['labels', 'text', 'full_text', 'type', 'kod_standard', 'sc', 'Unnamed: 0', 'name_sim_func']] # sc (близость нужна)
        #similar_docs['vacancy_text'] = sample['text']
        #similar_docs['vacancy_name'] = sample['name']
        #similar_docs['id_vacancy'] = sample['id']
        #similar_docs['vector_sim'] = 'Avg W2V'
        similar_docs['id_vacancy_part'] = index #нужно
        #similar_docs['id_matching'] = match_index

        similar_docs = similar_docs.rename(columns={
            'text': 'prof_text', #нужно
            'full_text': 'full_prof_text',
            'type': 'prof_type',
            'Unnamed: 0': 'id_profstandard_part', #нужно
            'kod_standard': 'prof_code'
        })
        df_result = pd.concat([df_result, similar_docs], ignore_index=True)
        match_index += 1
        print(index)
        print(match_index)
    return df_result

    # df_vacancies = get_vectorized_avg_w2v_corpus(df_vacancies, word2vec.wv)



def calculate(vacancies, profstandards, *args):
    '''
    make calculations

    :param vacancies: needs 'text' field
    :param profstandards: needs 'vectors' field
    :param args:
    :return:
    '''
    df_vacancies = vacancies['text'].apply(lambda text: process_text(text)['lemmatized_text_pos_tags'])  # лемматизируем
    df_vacancies = get_vectorized_avg_w2v_corpus(df_vacancies, word2vec.wv)  # получаем вектора

