import os
from random import random

from flask import Flask, request, session, redirect, url_for
from flask import render_template
from flask_session import Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

from datetime import datetime

from config import Config
from utils import get_date

import json

app = Flask(__name__)
app.config.from_object(Config)
Session(app=app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import MatchPart, VacancyPart, ProfstandardPost, VacancyPartType, Profstandard,\
    Source, Region, Vacancy, ClassifiedVacancy

from dto import Params

from handlers import general_function_tree, plot_search, plot_stat

@app.route('/')
def home():
    professions = Profstandard.query.all()
    regions = Region.query.all()
    sources = Source.query.all()
    return render_template('index.html', title='home', professions=professions, regions=regions, sources=sources)


@app.route('/results')
def results():
    reg_id = request.args.get('region')
    region = Region.query.get(reg_id)

    source_id = request.args.get('source')
    source = Source.query.get(source_id)

    sdate = request.args.get('sdate')
    edate = request.args.get('edate')
    dt_sdate = get_date(sdate)
    dt_edate = get_date(edate)

    period = 'C: ' + str(sdate) + ' По: ' + str(edate)  # месяц - день - год

    prof_id_list = request.args.getlist('prof')

    session['params'] = Params(region, source, dt_sdate, dt_edate, prof_id_list)

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
                           params=session['params'],
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


@app.route('/save', methods=['POST'])
def save_selection():
    return redirect('/')





@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(debug=True)
