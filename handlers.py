import numpy as np
import seaborn as sns
import pandas as pd
import codecs
import os
from sklearn.feature_extraction.text import TfidfVectorizer

from dto import SelectedItems
from models import  Function, ProfstandardPart,  GeneralFunction, Profstandard
sns.set(style="whitegrid")


def general_function_tree(prof_id, matched_parts, selected: SelectedItems = None):
    tree = []
    query = GeneralFunction.query.filter_by(profstandard_id=prof_id)
    parts = 0
    just_selected = []
    for each in query:

        function_weight = 0

        functions, parts_count, selected_parts = function_branch(each.id, matched_parts, selected)

        if len(functions) > 0:
            sorting_functions = pd.DataFrame(functions)
            function_weight = sorting_functions.weight.sum()
            functions = sorting_functions.sort_values('weight', ascending=False).to_dict('r')

        if selected is not None and each.id not in selected.general_fun_ids and (len(functions) > 0 or len(selected_parts) > 0):
            just_selected.append({
                'level': each.qualification_level,
                'functions': functions,
                'parts': selected_parts
            })



        vacancies_text = []

        for function_text in functions:
            for text in function_text['texts']:
                vacancies_text.append(text)
        vacancies_text = unique(vacancies_text)
        top_word = common_words(vacancies_text, 1, topn=10)
        top_bigram = common_words(vacancies_text, 2)

        general_function_branch = {
            'id': each.id,
            'weight': round(function_weight, 2),
            'name': each.name,
            'functions': functions,
            'count': parts_count,
            'level': each.qualification_level,
            'monogram': top_word,
            'bigram': top_bigram,
            'selected_parts': selected_parts,
            'gen_text':vacancies_text
        }

        parts += parts_count

        if selected is None or each.id in selected.general_fun_ids:
            tree.append(general_function_branch)

    return tree, parts, just_selected


def function_branch(general_id, matched_parts, selected: SelectedItems = None):
    branch = []
    counts = 0
    selected_parts = []
    query = Function.query.filter_by(general_function_id=general_id)
    for each in query:

        vacancy_weight = 0

        parts, parts_count = parts_vacancies_leafs(each.id, matched_parts, selected)

        if len(parts) > 0:
            sorting_parts = pd.DataFrame(parts)
            vacancy_weight = sorting_parts.weight.sum()
            parts = sorting_parts.sort_values('weight', ascending=False).to_dict('r')

        if selected is not None and each.id not in selected.fun_ids and len(parts) > 0:
            selected_parts = selected_parts + parts

        vacancies_text = []
        for part in parts:
            for vacancy in part['vacancy_parts']:
                vacancies_text.append(vacancy['vacancy_part'])

        vacancies_text = unique(vacancies_text)
        top_word = common_words(vacancies_text, 1, topn=10)
        top_bigram = common_words(vacancies_text, 2)

        function_parts_branch = {
            'id': each.id,
            'weight': round(vacancy_weight, 2),
            'name': each.name,
            'parts': parts,
            'texts': vacancies_text,
            'count': parts_count,
            'monogram': top_word,
            'bigram': top_bigram
        }

        counts += parts_count

        if selected is None or each.id in selected.fun_ids:
            branch.append(function_parts_branch)

    return branch, counts, selected_parts


def parts_vacancies_leafs(function_id, matched_parts, selected: SelectedItems = None):
    leaf = []
    query = ProfstandardPart.query.filter_by(function_id=function_id)
    count = 0
    for each in query:

        parts_weight = 0
        parts_count = 0

        top_word = []
        top_bigram = []
        vacancy_parts = matched_parts[each.id]
        sorting_parts = pd.DataFrame(vacancy_parts)
        if sorting_parts.empty:
            vacancy_parts = sorting_parts.to_dict('r')
        else:
            parts_count = len(vacancy_parts)
            parts_weight = sorting_parts.similarity.sum()
            vacancy_parts = sorting_parts.sort_values('similarity', ascending=False).to_dict('r')  #Части

            # MOST COMMON
            top_word = common_words(sorting_parts['vacancy_part'].dropna(), 1, topn=10)
            top_bigram = common_words(sorting_parts['vacancy_part'].dropna(), 2)

        leaf_parts = {
            'id': each.id,
            'weight': round(parts_weight, 2),
            'standard_part': each.text,
            'vacancy_parts': vacancy_parts, #вакансии
            'count': parts_count,
            'monogram': top_word,
            'bigram': top_bigram
        }
        count += parts_count

        if selected is None or each.id in selected.part_ids:
            leaf.append(leaf_parts)

    return leaf, count


def common_words(text, n_gram, topn = 5):
    lst = []
    top_word = []
    tfidf_vec = TfidfVectorizer(ngram_range=(n_gram, n_gram))
    try:
        transformed = tfidf_vec.fit_transform(raw_documents=text)
        index_value = {i[1]: i[0] for i in tfidf_vec.vocabulary_.items()}
    except ValueError:
        transformed = []
        index_value = {}

    fully_indexed = []
    for row in transformed:
        fully_indexed.append({index_value[column]: value for column, value in zip(row.indices, row.data)})

    for i in fully_indexed:
        for key, value in i.items():
            lst.append([value, key])

    lst.sort(reverse=True)
    lst = unique(lst)

    for i in lst[:topn:]:
        if i not in top_word:
            top_word.append(i[1])

    return top_word


def unique(lst):
    answer = []
    for i in lst:
        if i not in answer:
            answer.append(i)
    return answer


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




