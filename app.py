# -*- coding: utf-8 -*-
from flask import Flask, request, session, redirect, url_for, jsonify
from flask import render_template
from flask_session import Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
import pandas as pd
import matplotlib
import pymorphy2
# import searcher
import ast
import similarity


matplotlib.use('agg')
import matplotlib.pyplot as plt

from config import Config
from utils import get_date

app = Flask(__name__)
app.config.from_object(Config)
Session(app=app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

morph = pymorphy2.MorphAnalyzer()

from models import MatchPart, VacancyPart, ProfstandardPost, VacancyPartType, Profstandard, Source, Region, Vacancy, \
    ClassifiedVacancy, University, EducationProgram, ProfstandardPart, GeneralFunction, Function

from dto import Params, SelectedItems, Selected

from handlers import general_function_tree, plot_search, plot_stat, common_words, unique

@app.route('/searcher')
def root():
    return render_template("searcher.html")

@app.route('/courses')
def get_result():
    amount = request.args.get('amount', default=5, type=int)
    query_text = request.args.get('query_text', type=str)
    dev_mode = request.args.get('enableDevMode', default=False, type=bool)
    model_names = request.args.get('modelName').split(',')
    
    query_token = list(searcher.get_lemmatized_documents([query_text], morph, only_tokens=True))[0]

    most_sim_courses = searcher.get_most_sim_for_models(model_names, query_token, topn=amount)
    model = searcher.get_model_for_show(most_sim_courses)
    
    json_result = jsonify(model)
    return json_result

@app.route('/')
def home():
    professions = Profstandard.query.all()
    regions = Region.query.all()
    sources = Source.query.all()

    if 'params' in session:
        session.pop('params')

    if 'competence' in session:
        session.pop('competence')

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
    if 'params' in session:
        params = session['params']
    else:
        raise ValueError("ОТВАЛИЛАСЬ СЕССИЯ")
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

    text = []
    for branch in branches:
        for gen in branch['general_functions']:
            for gen_text in gen['gen_text']:
                text.append(gen_text)
    text = unique(text)
    top_bigrams = common_words(text, 2, topn=20)
    top_words = common_words(text, 1, topn=25,bigram=top_bigrams)
    return render_template('profession.html',
                           title='profession',
                           best_vacancies=best_vacancies,
                           worst_vacancies=worst_vacancies,
                           profession=Profstandard.query.get(prof_id).name,
                           branches=branches,
                           count=count,
                           top_words=top_words,
                           top_bigrams=top_bigrams,
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
    if 'selected' in session:
        session['selected'].items[profession_id] = SelectedItems(
            profession_id,
            list(map(int, request.form.getlist('gf'))),
            list(map(int, request.form.getlist('f'))),
            list(map(int, request.form.getlist('p')))
        )
    return redirect('/selected')


@app.route('/selected', methods=["GET", "POST"])
def selected():

    if request.method == "POST":
        codes = request.form.getlist('code')
        names = request.form.getlist('codename')
        competence = []

        for i in range(len(codes)):
            standards = []
            for index in request.form.getlist(codes[i]):

                standards.append(ProfstandardPart.query.get(index[5:]).text if index[:4] == 'part' else
                      GeneralFunction.query.get(index[5:]).name if index[:4] == 'gene' else
                      Function.query.get(index[5:]).name if index[:4] == 'func' else index)
            competence.append([codes[i], names[i], standards])
        session['competence'] = competence

    if 'selected' in session:
        params = session['params']
        professions = []

        for prof_id in session['selected'].items:

            selected_items = session['selected'].items[prof_id]

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

            professions.append({
                'name': Profstandard.query.get(prof_id).name,
                'branches': branches
            })

        period = 'C: ' + str(params.start_date) + ' По: ' + str(params.end_date)  # месяц - день - год


        return render_template('selected.html',
                               params=params,
                               period=period,
                               professions=professions,
                               competences=session['competence'] if 'competence' in session else []
                               )
    else:
        params = {"region":{"name":""},"source":{"name":""}}
        period = ''
        professions = []
        return render_template('selected.html',
                               params=params,
                               period=period,
                               professions=professions,
                               competences=session['competence'] if 'competence' in session else []
                               )


@app.route('/universities')
def universities():
    universities = University.query.all()
    return render_template('universities.html', title='universities', universities=universities)


@app.route('/education_program/<id_program>', methods=['GET'])
def education_program(id_program):
    # education_program = list(db.session.query(EducationProgram).filter(EducationProgram.university_id == id_program))
    program = EducationProgram.query.filter_by(university_id=id_program)
    program_name = '09.03.01 Информатика и вычислительная техника'
    names = [['Знать', 'know'], ['Уметь', 'can'], ['Владеть', 'own']]

    know, can, own = [], [], []
    program_tree = []
    program_df = pd.read_sql(program.statement, db.engine)

    competences = session['competence'] if 'competence' in session else []
    full_comp = []
    for comp in competences:
        full_comp.append(comp[1])
        pass

    gg = similarity.matching_parts(full_comp, program_df, part='know').to_html()

    for row in program:
        program_tree.append({'know': row.know.split('\n'),
                                'can': row.can.split('\n'),
                                'own': row.own.split('\n'),
                                'name': row.name,
                                'annotation': row.annotation,
                                'theme': row.themes.split('\n')})

    return render_template('education_program.html',
                           title='education program',
                           education_program=program_tree,
                           names=names,
                           program_name=program_name,
                           gg=gg)




@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(debug=True)
