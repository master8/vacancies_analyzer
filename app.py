from flask import Flask, request
from flask import render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import seaborn as sns

sns.set(style="whitegrid")
import pandas as pd
from collections import defaultdict

import numpy as np
from datetime import datetime

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Profstandard, Source, Region, Vacancy, ClassifiedVacancy, VacancyPartType, ProfstandardPost
from models import GeneralFunction, Function, ProfstandardPart, MatchPart, VacancyPart


@app.route('/')
def home():
    professions = Profstandard.query.all()
    regions = Region.query.all()
    sources = Source.query.all()
    return render_template('index.html', title='home', professions=professions, regions=regions, sources=sources)


@app.route('/search')
def search():
    reg_id = request.args.get('region')
    region = Region.query.get(reg_id)

    source_id = request.args.get('source')
    source = Source.query.get(source_id)

    sdate = request.args.get('sdate')
    edate = request.args.get('edate')
    dt_sdate = datetime.strptime(sdate, "%Y-%m-%d")
    dt_edate = datetime.strptime(edate, "%Y-%m-%d")

    period = 'from: ' + str(sdate) + ' to: ' + str(edate)  # месяц - день - год

    prof_id_list = request.args.getlist('prof')

    professions = []
    total = Vacancy.query \
        .filter(ClassifiedVacancy.profstandard_id.in_(prof_id_list)) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= dt_edate) \
        .filter(Vacancy.create_date >= dt_sdate) \
        .filter_by(region_id=reg_id) \
        .filter_by(source_id=source_id).count()

    for prof_id in prof_id_list:
        vacancy = Vacancy.query \
            .filter(ClassifiedVacancy.profstandard_id == prof_id) \
            .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
            .filter(Vacancy.create_date <= dt_edate) \
            .filter(Vacancy.create_date >= dt_sdate) \
            .filter_by(region_id=reg_id) \
            .filter_by(source_id=source_id)

        rate = vacancy.count() * 100 / total
        prof_dict = {
            'profstandard_id': prof_id,
            'code': Profstandard.query.get(prof_id).code,
            'name': Profstandard.query.get(prof_id).name,
            'count': vacancy.count(),
            'rate': str(round(rate, 2)) + '%'
        }
        professions.append(prof_dict)

    if not professions:
        professions = [{
            'profstandard_id': 0,
            'code': '',
            'name': 'Профессия не выбрана',
            'count': 0,
            'rate': 0
        }]

    diagram_link = plot_search(professions)

    return render_template('results.html',
                           title='results',
                           region=region,
                           source=source,
                           period=period,
                           professions=professions,
                           diagram_link=diagram_link,
                           sdate=request.args['sdate'],
                           edate=request.args['edate'],
                           total=total)


@app.route('/profession')
def profession():
    reg_id = request.args.get('region')

    source_id = request.args.get('source')
    prof_id = request.args.get('id')
    sdate = request.args.get('sdate')
    edate = request.args.get('edate')
    dt_sdate = datetime.strptime(sdate, "%Y-%m-%d")
    dt_edate = datetime.strptime(edate, "%Y-%m-%d")

    query = db.session.query(Vacancy, ClassifiedVacancy) \
        .filter(ClassifiedVacancy.profstandard_id == prof_id) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= dt_edate) \
        .filter(Vacancy.create_date >= dt_sdate) \
        .filter_by(region_id=reg_id) \
        .filter_by(source_id=source_id) \
        .order_by(ClassifiedVacancy.probability)

    best_vacancies = []
    worst_vacancies = []

    for vacancy, classified_vacancy in query[:10]:
        worst_vacancy = {
            'id': vacancy.id,
            'name': vacancy.name,
            'probability': classified_vacancy.probability
        }
        worst_vacancies.append(worst_vacancy)

    for vacancy, classified_vacancy in reversed(query[-10:]):
        best_vacancy = {
            'id': vacancy.id,
            'name': vacancy.name,
            'probability': classified_vacancy.probability
        }
        best_vacancies.append(best_vacancy)

    query = db.session.query(MatchPart, VacancyPart) \
        .filter(MatchPart.vacancy_part_id == VacancyPart.id) \
        .filter(VacancyPart.vacancy_id == Vacancy.id) \
        .filter(ClassifiedVacancy.profstandard_id == prof_id) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= dt_edate) \
        .filter(Vacancy.create_date >= dt_sdate) \
        .filter(Vacancy.region_id == reg_id) \
        .filter(Vacancy.source_id == source_id)

    matched_parts = defaultdict(list)

    for match_part, vacancy_part in query:
        matched_parts[match_part.profstandard_part_id].append({
            'similarity': round(match_part.similarity, 3),
            'vacancy_part': vacancy_part.text
        })

    general_functions, count = general_function_tree(prof_id, matched_parts)
    sorting_generals = pd.DataFrame(general_functions)
    general_functions = sorting_generals.sort_values('weight', ascending=False).to_dict('r')

    posts = defaultdict(list)
    general_functions_by_level = defaultdict(list)

    for post in ProfstandardPost.query.filter_by(profstandard_id=prof_id):
        posts[post.qualification_level].append(post)

    for function in general_functions:
        general_functions_by_level[function['level']].append(function)

    branches = []

    for key, value in general_functions_by_level.items():
        branches.append({
            'level': key,
            'posts': posts[key],
            'general_functions': value
        })

    classified_vacancies = db.session.query(ClassifiedVacancy) \
        .filter(ClassifiedVacancy.profstandard_id == prof_id) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= dt_edate) \
        .filter(Vacancy.create_date >= dt_sdate) \
        .filter(Vacancy.region_id == reg_id) \
        .filter(Vacancy.source_id == source_id)

    vacancies_id = list(map(lambda x: x.vacancy_id, classified_vacancies.all()))

    count_labels = defaultdict(int)

    for row in ClassifiedVacancy.query.filter(ClassifiedVacancy.vacancy_id.in_(vacancies_id)):

        if str(row.profstandard_id) != prof_id:
            count_labels[row.profstandard_id] += 1

    diagram_link, professions = plot_stat(count_labels)

    return render_template('profession.html',
                           title='profession',
                           best_vacancies=best_vacancies,
                           worst_vacancies=worst_vacancies,
                           profession=Profstandard.query.get(prof_id).name,
                           branches=branches,
                           count=count,
                           profession_id=prof_id,
                           region=source_id,
                           source=reg_id,
                           sdate=request.args['sdate'],
                           edate=request.args['edate'],
                           diagram_link=diagram_link,
                           professions=professions)


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
            vacancy_parts = sorting_parts.sort_values('similarity', ascending=False).to_dict('r')[:5]
        leaf_parts = {
            'weight': round(parts_weight, 2),
            'standard_part': each.text,
            'vacancy_parts': vacancy_parts,
            'count': parts_count
        }
        leaf.append(leaf_parts)
        weight += parts_weight
        count += parts_count

    return leaf, weight, count


@app.route('/vacancy')
def vacancy():
    vacancy = Vacancy.query.get(request.args['id'])
    return render_template('vacancy.html', vacancy=vacancy, VacancyPartType=VacancyPartType)


@app.route('/vacancies')
def all_vacancy():
    reg_id = request.args.get('region')
    source_id = request.args.get('source')
    profession_id = request.args.get('prof')

    sdate = request.args.get('sdate')
    edate = request.args.get('edate')
    dt_sdate = datetime.strptime(sdate, "%Y-%m-%d")
    dt_edate = datetime.strptime(edate, "%Y-%m-%d")

    vacancies = db.session.query(Vacancy, ClassifiedVacancy) \
        .filter(ClassifiedVacancy.profstandard_id == profession_id) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= dt_edate) \
        .filter(Vacancy.create_date >= dt_sdate) \
        .filter_by(region_id=reg_id) \
        .filter_by(source_id=source_id) \
        .order_by(ClassifiedVacancy.probability)

    vacancies = reversed(vacancies.all())

    return render_template('all_vacancy.html', vacancies=vacancies)


@app.route('/split/vacancies')
def split_vacancies():
    reg_id = request.args.get('region')
    source_id = request.args.get('source')
    profession_id = request.args.get('prof')

    sdate = request.args.get('sdate')
    edate = request.args.get('edate')
    dt_sdate = datetime.strptime(sdate, "%Y-%m-%d")
    dt_edate = datetime.strptime(edate, "%Y-%m-%d")

    vacancies = db.session.query(Vacancy, ClassifiedVacancy) \
        .filter(ClassifiedVacancy.profstandard_id == profession_id) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= dt_edate) \
        .filter(Vacancy.create_date >= dt_sdate) \
        .filter_by(region_id=reg_id) \
        .filter_by(source_id=source_id) \
        .filter(VacancyPart.vacancy_id == Vacancy.id) \
        .order_by(ClassifiedVacancy.probability)

    vacancies = reversed(vacancies.all())

    return render_template('all_vacancy.html', vacancies=vacancies)


def plot_search(professions):
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


def plot_stat(count_labels):
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


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(debug=True)
