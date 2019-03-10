from sklearn.metrics.pairwise import cosine_similarity
# from gensim import corpora, models
import collections
import pandas as pd
import numpy as np
# import smart_open
import pymorphy2
import pickle
import random
import gensim
import json
import os

def save_pickle(path, data):
    with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_pickle(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)

# full_df = pd.read_csv('./searcher/data/full_df_rpd_with_sr_courses_wo_str.csv')
#
# tfidfmodel = load_pickle('./searcher/models/tfidfmodel.pkl')
# tfidfdictionary = load_pickle('./searcher/models/tfidfdictionary.pkl')
# waw2vmodel = load_pickle('./searcher/models/waw2vmodel.pkl')
#
# w2vvectors = load_pickle('./searcher/vectors/w2vvectors.pkl')
# w2vvectors_weighted = load_pickle('./searcher/vectors/w2vvectors_weighted.pkl')
# # tfidf_vectors = load_pickle('./searcher/vectors/tfidf_vectors.pkl')
#
# dict_vectors_struct_w2w = load_pickle('./searcher/vectors/dict_vectors_struct_w2w.pkl')
# # dict_vectors_struct_tfidf = load_pickle('./searcher/vectors/dict_vectors_struct_tfidf.pkl')
# dict_vectors_struct_w2widf = load_pickle('./searcher/vectors/dict_vectors_struct_w2widf.pkl')
#
# dict_rpd_id_struct = load_pickle('./searcher/data/dict_rpd_id_struct.pkl')

def get_russian_lemma(token, lemmatizer):
    lemma = lemmatizer.parse(token.lower())[0]
    return lemma.normal_form

def get_lemmatized_sequence(sequence, lemmatizer):
    lemmas = []
    for token in sequence:
        lemma = get_russian_lemma(token, lemmatizer)
        if lemma.strip() != "":
            lemmas.append(lemma)
    return ' '.join(lemmas)

def get_lemmatized_document(text, lemmatizer):
    text = str(text)
    return get_lemmatized_sequence(gensim.utils.simple_preprocess(text.replace('\n', ' ')), lemmatizer)

def get_lemmatized_documents(texts, lemmatizer, only_tokens):
    for text in texts:
        lemm_text = get_lemmatized_document(text, lemmatizer)
        if only_tokens:
            yield gensim.utils.simple_preprocess(lemm_text)
        else:
            yield lemm_text

def GetVectors(model, dictionary, dimensionality, corpus):
    dim_sum = 0
    vectors = []
    for i in range(0, len(corpus)):        
        prevector = model[dictionary.doc2bow(corpus[i])]
        dim_sum += len(prevector)
        vector = [0]*dimensionality
        for k,v in prevector:
            vector[k]=v
        vectors.append(vector)
    return vectors

def GetAverageW2Vector(model, doc, dimensionality):
    wordcount = 0
    docvector = [0]*dimensionality
    for word in doc:
        if word in model.wv.vocab:
            wordcount+=1
            docvector=[x + y for x, y in zip(docvector, model[word])]
    if wordcount != 0:
        docvector=[x / wordcount for x in docvector]
    return docvector

def GetAverageW2VectorsCorpus(model, corpus, dimensionality):
    vectors = []
    for doc in corpus:
        vectors.append(GetAverageW2Vector(model, doc, dimensionality))
    return vectors

def GetWeightedAverageW2Vector(model, weights, dictionary, doc, dimensionality):
    wordcount = 0
    docvector = [0]*dimensionality
    
    d = dict(weights[dictionary.doc2bow(doc)])

    for word in doc:
        if 1==1:
            weight=dictionary.doc2bow([word])
            #if (word in model.vocab) and (len(weight)>0):
            if (word in model.wv.vocab) and (len(weight)>0):
                wordcount+=1
                w=weight[0][0]
                if not (w in d):
                    w=0
                else:
                    w=d[w]
                docvector=[(x + (y*w)) for x, y in zip(docvector, model[word])]
#     if wordcount == 0:
#         docvector=[x / wordcount for x in docvector]
    return docvector

def GetWeightedAverageW2VectorsCorpus(model, weights, dictionary, corpus, dimensionality):
    vectors = []
    for doc in corpus:
        vectors.append(GetWeightedAverageW2Vector(model, weights, dictionary, doc, dimensionality))
    return vectors

def most_similar(inferred_vector, vectors, topn=10):
    sims=[]
    
    for i in range(0, len(vectors)):
        sim = cosine_similarity(np.reshape(vectors[i], (1,-1)), np.reshape(inferred_vector, (1,-1)))[0][0]
        sims.append((i, sim))
                    
    similar_docs=sorted(sims, key=lambda x: x[1], reverse=True)

    return similar_docs[:topn]

def get_most_sim_for_models(model_names, query, topn=10, dimensionality=300):
    results = {}
    for model_name in model_names:
        if model_name == "w2widf":
            inferred_vector = GetWeightedAverageW2VectorsCorpus(waw2vmodel, tfidfmodel, tfidfdictionary, [query], dimensionality)
            vectors = w2vvectors_weighted
            lesson_dict = dict_vectors_struct_w2widf
        if model_name == "w2w":
            inferred_vector = GetAverageW2VectorsCorpus(waw2vmodel, [query], dimensionality)
            vectors = w2vvectors
            lesson_dict = dict_vectors_struct_w2w
        if model_name == "tfidf":
            inferred_vector = GetVectors(tfidfmodel, tfidfdictionary, len(tfidfdictionary), [query])[0]
            vectors = tfidf_vectors
            lesson_dict = dict_vectors_struct_tfidf
        most_sim = most_similar(inferred_vector=inferred_vector, vectors=vectors, topn=topn)
        
        model = []
        for course_id, sim in most_sim:
            most_sim_lesson = []
            if course_id in lesson_dict:
                lesson_vectors = lesson_dict[course_id]
                most_sim_lesson = most_similar(inferred_vector=inferred_vector, vectors=lesson_vectors, topn=3)
            model.append((course_id, sim, most_sim_lesson))
            
        
        results[model_name] = model
    return results


def get_model_for_show(result_dict, top_lesson=3):
    result = []
    for model_name, model_results in result_dict.items():
        for course_id, sim, lesson_sim in model_results:
            lessons = []
            if len(lesson_sim) != 0:
                for lesson_id, lesson_sim in lesson_sim:
                    lesson_name = str(dict_rpd_id_struct[course_id][lesson_id])
                    lessons.append([lesson_name, lesson_sim])
            
            course_df = full_df.loc[course_id]
            model = {"resultId": course_id, 
                     "url": str(course_df['Url']),
                     "title": course_df['CourseName'],
                     "markValue": 5,
                     "modelName": model_name,
                     "description": str(course_df['full_text'])[:300],
                     "lessons": lessons}
            result.append(model)
    return result
