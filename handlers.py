import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

from dto import SelectedItems
from models import Function, ProfstandardPart, GeneralFunction, Profstandard


def general_function_tree(prof_id, matched_parts, selected: SelectedItems = None):
    tree = []
    query = GeneralFunction.query.filter_by(profstandard_id=prof_id)
    parts = 0
    just_selected = []
    for each in query:

        functions, function_weight, parts_count, selected_parts = function_branch(each.id, matched_parts, selected)

        if len(functions) > 0:
            sorting_functions = pd.DataFrame(functions)
            functions = sorting_functions.sort_values('weight', ascending=False).to_dict('r')

        if selected is not None and each.id not in selected.general_fun_ids and (
                len(functions) > 0 or len(selected_parts) > 0):
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
        top_bigram = common_words(vacancies_text, 2, topn=15)
        top_word = common_words(vacancies_text, 1, topn=20, bigram=top_bigram)

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
            'gen_text': vacancies_text
        }

        parts += parts_count

        if selected is None or each.id in selected.general_fun_ids:
            tree.append(general_function_branch)

    return tree, parts, just_selected


def function_branch(general_id, matched_parts, selected: SelectedItems = None):
    branch = []
    weight = 0
    counts = 0
    selected_parts = []
    query = Function.query.filter_by(general_function_id=general_id)
    for each in query:

        parts, vacancy_weight, parts_count = parts_vacancies_leafs(each.id, matched_parts, selected)

        if len(parts) > 0:
            sorting_parts = pd.DataFrame(parts)
            parts = sorting_parts.sort_values('weight', ascending=False).to_dict('r')

        if selected is not None and each.id not in selected.fun_ids and len(parts) > 0:
            selected_parts = selected_parts + parts

        vacancies_text = []
        for part in parts:
            for vacancy in part['vacancy_parts']:
                vacancies_text.append(vacancy['vacancy_part'])

        vacancies_text = unique(vacancies_text)
        top_bigram = common_words(vacancies_text, 2, topn=10)
        top_word = common_words(vacancies_text, 1, topn=15, bigram=top_bigram)

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

        weight += vacancy_weight
        counts += parts_count

        if selected is None or each.id in selected.fun_ids:
            branch.append(function_parts_branch)

    return branch, weight, counts, selected_parts


def parts_vacancies_leafs(function_id, matched_parts, selected: SelectedItems = None):
    leaf = []
    weight = 0
    query = ProfstandardPart.query.filter_by(function_id=function_id).filter(
        ProfstandardPart.part_type_id.in_([4, 5, 6]))
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
            vacancy_parts = sorting_parts.sort_values('similarity', ascending=False).to_dict('r')  # Части

            # MOST COMMON

            top_bigram = common_words(sorting_parts['vacancy_part'].dropna(), 2, topn=5)
            top_word = common_words(sorting_parts['vacancy_part'].dropna(), 1, topn=10, bigram=top_bigram)

        leaf_parts = {
            'id': each.id,
            'weight': round(parts_weight, 2),
            'name': each.text,
            'vacancy_parts': vacancy_parts,  # вакансии
            'count': parts_count,
            'monogram': top_word,
            'bigram': top_bigram
        }
        weight += parts_weight
        count += parts_count

        if selected is None or each.id in selected.part_ids:
            leaf.append(leaf_parts)

    return leaf, weight, count


def common_words(text, n_gram, topn=5, bigram=[]):
    #bigram = bigram.split(', ')
    lst = []
    top_word = []
    tfidf_vec = TfidfVectorizer(ngram_range=(n_gram, n_gram), stop_words=['по', 'опыт', 'на', 'результат', 'хорошее', 'знание'])

    try:
        text = pd.Series(text).apply(lambda row: row.lower())
        transformed = tfidf_vec.fit_transform(raw_documents=list(text))
        index_value = {i[1]: i[0] for i in tfidf_vec.vocabulary_.items()}
    except ValueError:
        transformed = []
        index_value = {}

    fully_indexed = []
    for row in transformed:
        fully_indexed.append({index_value[column]: value for column, value in zip(row.indices, row.data)})
    for i in fully_indexed:
        for key, value in i.items():
            lst.append((value, key))
    lst = unique(lst, bigram)
    lst = sorted(lst, key=lambda x: x[0], reverse=True)
    for i in lst[:topn:]:
        if i not in top_word:
            top_word.append((i[1], i[0]))

    return [i[0] for i in sorted(top_word, key=lambda x: x[1], reverse=True)] #', '.join([i[0] for i in sorted(top_word, key=lambda x: x[1], reverse=True)])


# prof_bag = ' ' #рабботало
# for row in Function.query:
#     prof_bag += str(row.name)+' '
# for row in GeneralFunction.query:
#     prof_bag += str(row.name)+' '
# for row in ProfstandardPart.query:
#     prof_bag += str(row.text)+' '
# for row in Profstandard.query:
#     prof_bag += str(row.name)+' '

# prof_bag = []
# for row in Function.query:
#     prof_bag.extend(row.name.split(' '))
# for row in GeneralFunction.query:
#     prof_bag.extend(row.name.split(' '))
# for row in ProfstandardPart.query:
#     try:
#         prof_bag.extend(row.text.split(' '))
#     except:pass
# for row in Profstandard.query:
#     prof_bag.extend(row.name.split(' '))


print('loaded')


def unique(lst, bigram=[]):
    answer = []
    for i in lst:
        if [wrd for wrd in bigram if i[1] in wrd] == []:
            # if type(i) == list:
            #     if i[1] not in prof_bag:
            #         answer.append(i)
            #     else:
            #         pass
            # else:
            #     answer.append(i)
            answer.append(i)
    answer = set(answer)
    answer = list(answer)
    return answer


def plot_stat(count_labels):  # график
    professions = []
    if len(count_labels) > 0:
        for key, value in count_labels.items():
            profession = Profstandard.query.get(key)
            professions.append({
                'profstandard_id': profession.id,
                'id': profession.id,
                'name': profession.name,
                'code': profession.code,
                'count': value
            })
    return professions
