from flask import Flask, request, session, redirect, url_for
from flask import render_template
from flask_session import Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
import pandas as pd

from config import Config
from utils import get_date

app = Flask(__name__)
app.config.from_object(Config)
Session(app=app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import MatchPart, VacancyPart, ProfstandardPost, VacancyPartType, Profstandard,\
    Source, Region, Vacancy, ClassifiedVacancy

from dto import Params, SelectedItems, Selected

from handlers import general_function_tree, plot_search, plot_stat


@app.route('/')
def home():
    professions = Profstandard.query.all()
    regions = Region.query.all()
    sources = Source.query.all()

    if 'params' in session:
        session.pop('params')

    session['selected'] = Selected()

    return render_template('index.html', title='home', professions=professions, regions=regions, sources=sources)


@app.route('/results')
def results():

    if 'params' in session:
        params = session['params']
    else:
        reg_id = request.args.get('region')
        region = Region.query.get(reg_id)

        source_id = request.args.get('source')
        source = Source.query.get(source_id)

        sdate = request.args.get('sdate')
        edate = request.args.get('edate')
        dt_sdate = get_date(sdate)
        dt_edate = get_date(edate)

        prof_id_list = request.args.getlist('prof')

        params = Params(region, source, dt_sdate, dt_edate, prof_id_list)
        session['params'] = params

    period = 'C: ' + str(params.start_date) + ' По: ' + str(params.end_date)  # месяц - день - год

    professions = []
    total = Vacancy.query \
        .filter(ClassifiedVacancy.profstandard_id.in_(params.profession_ids)) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= params.end_date) \
        .filter(Vacancy.create_date >= params.start_date) \
        .filter_by(region_id=params.region.id) \
        .filter_by(source_id=params.source.id).count()

    for prof_id in params.profession_ids:
        vacancy = Vacancy.query \
            .filter(ClassifiedVacancy.profstandard_id == prof_id) \
            .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
            .filter(Vacancy.create_date <= params.end_date) \
            .filter(Vacancy.create_date >= params.start_date) \
            .filter_by(region_id=params.region.id) \
            .filter_by(source_id=params.source.id)

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
                           params=params,
                           period=period,
                           professions=professions,
                           diagram_link=diagram_link,
                           total=total)


@app.route('/profession')
def profession():
    params = session['params']
    prof_id = request.args.get('id')

    query = db.session.query(Vacancy, ClassifiedVacancy) \
        .filter(ClassifiedVacancy.profstandard_id == prof_id) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= params.end_date) \
        .filter(Vacancy.create_date >= params.start_date) \
        .filter_by(region_id=params.region.id) \
        .filter_by(source_id=params.source.id) \
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
        .filter(Vacancy.create_date <= params.end_date) \
        .filter(Vacancy.create_date >= params.start_date) \
        .filter(Vacancy.region_id == params.region.id) \
        .filter(Vacancy.source_id == params.source.id)

    matched_parts = defaultdict(list)

    for match_part, vacancy_part in query:
        matched_parts[match_part.profstandard_part_id].append({
            'similarity': round(match_part.similarity, 3),
            'vacancy_part': vacancy_part.text
        })

    general_functions, count, just_selected = general_function_tree(prof_id, matched_parts)
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
        .filter(Vacancy.create_date <= params.end_date) \
        .filter(Vacancy.create_date >= params.start_date) \
        .filter(Vacancy.region_id == params.region.id) \
        .filter(Vacancy.source_id == params.source.id)

    vacancies_id = list(map(lambda x: x.vacancy_id, classified_vacancies.all()))

    count_labels = defaultdict(int)

    for row in ClassifiedVacancy.query.filter(ClassifiedVacancy.vacancy_id.in_(vacancies_id)):

        if str(row.profstandard_id) != prof_id:
            count_labels[row.profstandard_id] += 1

    diagram_link, professions = plot_stat(count_labels)

    if 'selected' in session and int(prof_id) in session['selected'].items:
        selected = session['selected'].items[int(prof_id)]
    else:
        selected = SelectedItems(int(prof_id), [], [], [])

    return render_template('profession.html',
                           title='profession',
                           best_vacancies=best_vacancies,
                           worst_vacancies=worst_vacancies,
                           profession=Profstandard.query.get(prof_id).name,
                           branches=branches,
                           count=count,
                           profession_id=prof_id,
                           params=params,
                           sdate=params.start_date,
                           edate=params.end_date,
                           diagram_link=diagram_link,
                           professions=professions,
                           selected=selected)


@app.route('/vacancy')
def vacancy():
    vacancy = Vacancy.query.get(request.args['id'])
    return render_template('vacancy.html', vacancy=vacancy, VacancyPartType=VacancyPartType)


@app.route('/vacancies')
def all_vacancy():
    params = session['params']
    profession_id = request.args.get('prof')

    vacancies = db.session.query(Vacancy, ClassifiedVacancy) \
        .filter(ClassifiedVacancy.profstandard_id == profession_id) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= params.end_date) \
        .filter(Vacancy.create_date >= params.start_date) \
        .filter_by(region_id=params.region.id) \
        .filter_by(source_id=params.source.id) \
        .order_by(ClassifiedVacancy.probability)
    vacancies = reversed(vacancies.all())
    return render_template('all_vacancy.html', vacancies=vacancies)


@app.route('/split/vacancies')
def split_vacancies():
    params = session['params']
    profession_id = request.args.get('prof')

    vacancies = db.session.query(Vacancy, ClassifiedVacancy) \
        .filter(ClassifiedVacancy.profstandard_id == profession_id) \
        .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
        .filter(Vacancy.create_date <= params.end_date) \
        .filter(Vacancy.create_date >= params.start_date) \
        .filter_by(region_id=params.region.id) \
        .filter_by(source_id=params.source.id) \
        .filter(VacancyPart.vacancy_id == Vacancy.id) \
        .order_by(ClassifiedVacancy.probability)

    vacancies = reversed(vacancies.all())

    return render_template('all_vacancy.html', vacancies=vacancies)


@app.route('/save', methods=['POST'])
def save_selection():
    profession_id = int(request.args.get('prof_id'))
    session['selected'].items[profession_id] = SelectedItems(
        profession_id,
        list(map(int, request.form.getlist('gf'))),
        list(map(int, request.form.getlist('f'))),
        list(map(int, request.form.getlist('p')))
    )
    return redirect('/selected')


@app.route('/selected')
def selected():
    if 'selected' in session:
        params = session['params']

        # prof_id = session['selected'].items.first()
        prof_id = 1

        if 'selected' in session and prof_id in session['selected'].items:
            selected_items = session['selected'].items[prof_id]
        else:
            selected_items = SelectedItems(prof_id, [], [], [])




        query = db.session.query(MatchPart, VacancyPart) \
            .filter(MatchPart.vacancy_part_id == VacancyPart.id) \
            .filter(VacancyPart.vacancy_id == Vacancy.id) \
            .filter(ClassifiedVacancy.profstandard_id == prof_id) \
            .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
            .filter(Vacancy.create_date <= params.end_date) \
            .filter(Vacancy.create_date >= params.start_date) \
            .filter(Vacancy.region_id == params.region.id) \
            .filter(Vacancy.source_id == params.source.id)

        matched_parts = defaultdict(list)

        for match_part, vacancy_part in query:
            matched_parts[match_part.profstandard_part_id].append({
                'similarity': round(match_part.similarity, 3),
                'vacancy_part': vacancy_part.text
            })

        general_functions, count, just_selected = general_function_tree(prof_id, matched_parts, selected_items)
        sorting_generals = pd.DataFrame(general_functions)
        general_functions = sorting_generals.sort_values('weight', ascending=False).to_dict('r')
        posts = defaultdict(list)
        general_functions_by_level = defaultdict(list)
        just_selected_by_level = defaultdict(list)

        for post in ProfstandardPost.query.filter_by(profstandard_id=prof_id):
            posts[post.qualification_level].append(post)

        for function in general_functions:
            general_functions_by_level[function['level']].append(function)

        for item in just_selected:
            just_selected_by_level[item['level']].append(item)
            if item['level'] not in general_functions_by_level:
                general_functions_by_level[item['level']] = []

        branches = []

        for key, value in general_functions_by_level.items():
            branches.append({
                'level': key,
                'posts': posts[key],
                'general_functions': value,
                'just_selected': just_selected_by_level[key]
            })



        period = 'C: ' + str(params.start_date) + ' По: ' + str(params.end_date)  # месяц - день - год

        return render_template('selected.html',
                               params=params,
                               period=period,
                               branches=branches,
                               count=count,
                               profession_id=prof_id,
                               selected=selected_items)
    else:
        return ''


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(debug=True)
