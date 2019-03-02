from flask import Flask, request
import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
from flask import render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import seaborn as sns
from collections import defaultdict

import numpy as np
from datetime import datetime

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
db.create_all()
migrate = Migrate(app, db)

from models import University


@app.route('/')
def home():
    universities = University.query.all()
    return render_template('index.html', title='home', universities=universities)


@app.route('/edprogram')
def profession():
    reg_id = request.args.get('region')
    # query = db.session.query(Vacancy, ClassifiedVacancy) \
    #     .filter(ClassifiedVacancy.profstandard_id == prof_id) \
    #     .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
    #     .filter(Vacancy.create_date <= dt_edate) \
    #     .filter(Vacancy.create_date >= dt_sdate) \
    #     .filter_by(region_id=reg_id) \
    #     .filter_by(source_id=source_id) \
    #     .order_by(ClassifiedVacancy.probability)
    #
    # best_vacancies = []
    # worst_vacancies = []
    #
    # for vacancy, classified_vacancy in query[:10]:
    #     worst_vacancy = {
    #         'id': vacancy.id,
    #         'name': vacancy.name,
    #         'probability': str(classified_vacancy.probability)[:6]
    #     }
    #     worst_vacancies.append(worst_vacancy)
    #
    # for vacancy, classified_vacancy in reversed(query[-10:]):
    #     best_vacancy = {
    #         'id': vacancy.id,
    #         'name': vacancy.name,
    #         'probability': str(classified_vacancy.probability)[:6]
    #     }
    #     best_vacancies.append(best_vacancy)
    #
    # query = db.session.query(MatchPart, VacancyPart) \
    #     .filter(MatchPart.vacancy_part_id == VacancyPart.id) \
    #     .filter(VacancyPart.vacancy_id == Vacancy.id) \
    #     .filter(ClassifiedVacancy.profstandard_id == prof_id) \
    #     .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
    #     .filter(Vacancy.create_date <= dt_edate) \
    #     .filter(Vacancy.create_date >= dt_sdate) \
    #     .filter(Vacancy.region_id == reg_id) \
    #     .filter(Vacancy.source_id == source_id)
    #
    # matched_parts = defaultdict(list)
    #
    # for match_part, vacancy_part in query:
    #     matched_parts[match_part.profstandard_part_id].append({
    #         'similarity': match_part.similarity,
    #         'vacancy_part': vacancy_part.text
    #     })
    #
    # general_functions = general_function_tree(prof_id, matched_parts)

    return render_template('profession.html',
                           title='profession',
                           education_program=["09.03.01. Информатика и вычислительная техника"],
                           disciplines = ["Программирование", "Базы данных", "Алгоритмы и анализ сложности", "Анализ данных"],
                           zyn = ["ОПК-1", "ПК-1", "ПК-2"],
                           parts = ["Блок-схема алгоритма", "Введение в язык программирования СИ"],
                           themes = ["Блок-схема алгоритма", "Массивы -одномерные. Алгоритмы работы с массивами"])


# def general_function_tree(prof_id, matched_parts):
#     tree = []
#     query = GeneralFunction.query.filter_by(profstandard_id=prof_id)
#     for each in query:
#         functions, function_weight = function_branch(each.id, matched_parts)
#         general_function_branch = {
#             'weight': function_weight,
#             'name': each.name,
#             'functions': functions
#         }
#         tree.append(general_function_branch)
#     return tree
#
#
# def function_branch(general_id, matched_parts):
#     branch = []
#     weight = 0
#     query = Function.query.filter_by(general_function_id=general_id)
#     for each in query:
#         parts, vacancy_weight = parts_vacancies_leafs(each.id, matched_parts)
#         function_parts_branch = {
#             'weight': vacancy_weight,
#             'name': each.name,
#             'parts': parts
#         }
#         branch.append(function_parts_branch)
#         weight += vacancy_weight
#     return branch, weight
#
#
# def parts_vacancies_leafs(function_id, matched_parts):
#     leaf = []
#     query = ProfstandardPart.query.filter_by(function_id=function_id)
#     weight = 0
#     for each in query:
#         vacancy_parts = matched_parts[each.id]
#         parts_weight = len(vacancy_parts)
#         leaf_parts = {
#             'weight': parts_weight,
#             'standard_part': each.text,
#             'vacancy_parts': vacancy_parts
#         }
#         leaf.append(leaf_parts)
#         weight += parts_weight
#
#     return leaf, weight
#
#
# @app.route('/vacancy')
# def vacancy():
#     return 'vacancy ' + str(request.args['id'])
#
#
# def plot_search(professions):
#     t = []
#     num = []
#
#     for i in professions:
#         t.append(str(i['code']))
#         num.append(i['count'])
#     x = np.array(t)
#     y = np.array(num)
#
#     diagram = sns.barplot(x=x, y=y)
#     diagram.clear()
#     diagram = sns.barplot(x=x, y=y)
#     dia = diagram.get_figure()
#
#     dia.savefig('./static/diagram/test_diagram.svg')
#     diagram_link = '../static/diagram/test_diagram.svg'
#
#     return diagram_link
#

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(debug=True)
