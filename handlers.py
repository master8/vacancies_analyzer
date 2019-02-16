import numpy as np
import seaborn as sns
import pandas as pd
import codecs
import os
import pymorphy2
from collections import Counter
from string import ascii_lowercase, digits, whitespace
from models import  Function, ProfstandardPart,  GeneralFunction, Profstandard
sns.set(style="whitegrid")

def general_function_tree(prof_id, matched_parts):
    tree = []
    query = GeneralFunction.query.filter_by(profstandard_id=prof_id)
    parts = 0
    for each in query:
        functions, function_weight, parts_count = function_branch(each.id, matched_parts)
        sorting_functions = pd.DataFrame(functions)
        functions = sorting_functions.sort_values('weight', ascending=False).to_dict('r')
        general_function_branch = {
            'weight': round(function_weight, 2),
            'name': each.name,
            'functions': functions,
            'count': parts_count,
            'level': each.qualification_level
        }
        tree.append(general_function_branch)
        parts += parts_count
    return tree, parts


def function_branch(general_id, matched_parts):
    branch = []
    weight = 0
    counts = 0
    query = Function.query.filter_by(general_function_id=general_id)
    for each in query:
        parts, vacancy_weight, parts_count = parts_vacancies_leafs(each.id, matched_parts)
        sorting_parts = pd.DataFrame(parts)
        parts = sorting_parts.sort_values('weight', ascending=False).to_dict('r')
        function_parts_branch = {
            'weight': round(vacancy_weight, 2),
            'name': each.name,
            'parts': parts,
            'count': parts_count
        }
        branch.append(function_parts_branch)
        weight += vacancy_weight
        counts += parts_count
    return branch, weight, counts


def parts_vacancies_leafs(function_id, matched_parts):
    leaf = []
    query = ProfstandardPart.query.filter_by(function_id=function_id)
    weight = 0
    count = 0
    monogram = 'none'
    for each in query:
        parts_weight = 0
        parts_count = 0
        vacancy_parts = matched_parts[each.id]
        sorting_parts = pd.DataFrame(vacancy_parts)
        if sorting_parts.empty:
            vacancy_parts = sorting_parts.to_dict('r')
        else:
            parts_count = len(vacancy_parts)
            parts_weight = sorting_parts.similarity.sum()
            sorting_parts['lemmatized'] = sorting_parts['vacancy_part'].apply(lambda i: process_text(i))

            vacancy_parts = sorting_parts.sort_values('similarity', ascending=False).to_dict('r')  #Части

            bag = ''
            for i in sorting_parts['vacancy_part']:
                bag += i + ' '

            bag = bag.split(' ')
            monogram = [i[0] for i in Counter(bag).most_common(5)]


        leaf_parts = {
            'weight': round(parts_weight, 2),
            'standard_part': each.text,
            'vacancy_parts': vacancy_parts, #вакансии
            'count': parts_count,
            'monogram': monogram,
            'bigram': each.text
        }
        leaf.append(leaf_parts)
        weight += parts_weight
        count += parts_count
    return leaf, weight, count


def plot_search(professions):  #график
    t = []
    num = []
    for i in professions:
        t.append(str(i['code']))
        num.append(i['count'])
    x = np.array(t)
    y = np.array(num)

    diagram = sns.barplot(x=x, y=y)
    diagram.clear()
    diagram = sns.barplot(x=x, y=y)
    dia = diagram.get_figure()

    dia.savefig('./static/diagram/test_diagram.svg')
    diagram_link = '../static/diagram/test_diagram.svg'
    return diagram_link


def plot_stat(count_labels): #график
    t = []
    num = []
    professions = []
    for key, value in count_labels.items():
        profession = Profstandard.query.get(key)
        professions.append({
            'profession': profession,
            'count': value
        })
        t.append('| ' + profession.code)
        num.append(value)
    x = np.array(t, dtype=str)
    y = np.array(num)
    diagram = sns.barplot(x=y, y=x)
    diagram.clear()
    diagram = sns.barplot(x=y, y=x)
    dia = diagram.get_figure()

    dia.savefig('./static/diagram/test_diagram2.svg')
    diagram_link = '../static/diagram/test_diagram2.svg'
    return diagram_link, professions


''''''
morph = pymorphy2.MorphAnalyzer()

cyrillic = u"абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

allowed_characters = ascii_lowercase + digits + cyrillic + whitespace

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

    return lemmatized_text_pos_tags

