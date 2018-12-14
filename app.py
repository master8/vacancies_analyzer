from flask import Flask, request
from flask import render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import seaborn as sns

import numpy as np
from datetime import datetime

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Profstandard, Source, Region, Vacancy, ClassifiedVacancy


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

    for prof_id in prof_id_list:
        vacancy = Vacancy.query \
            .filter(ClassifiedVacancy.profstandard_id == prof_id) \
            .filter(Vacancy.id == ClassifiedVacancy.vacancy_id) \
            .filter(Vacancy.create_date <= dt_edate) \
            .filter(Vacancy.create_date >= dt_sdate) \
            .filter_by(region_id=reg_id) \
            .filter_by(source_id=source_id)

        prof_dict = {
            'profstandard_id': prof_id,
            'code': Profstandard.query.get(prof_id).code,
            'name': Profstandard.query.get(prof_id).name,
            'count': vacancy.count()
        }
        professions.append(prof_dict)

    if not professions:
        professions = [{
            'profstandard_id': 0,
            'code': '',
            'name': 'Профессия не выбрана',
            'count': 0
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
                           edate=request.args['edate'])


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
            'name': vacancy.name + 'govno',
            'probability': str(classified_vacancy.probability)[:6]
        }
        worst_vacancies.append(worst_vacancy)

    for vacancy, classified_vacancy in reversed(query[-10:]):
        best_vacancy = {
            'id': vacancy.id,
            'name': vacancy.name + 'govno',
            'probability': str(classified_vacancy.probability)[:6]
        }
        best_vacancies.append(best_vacancy)

    parts = [
        {
            'similarity': 0.4353,
            'standard_part': 'Внутренние нормативные документы, регламентирующие требования к программному коду, порядок отражения изменений в системе контроля версий',
            'vacancy_part': 'Автоматизация процессов, установка обновлений операционной системы и критических обновлений для ПО Oracle'
        },
        {
            'similarity': 0.4353,
            'standard_part': 'Внутренние нормативные документы, регламентирующие требования к программному коду, порядок отражения изменений в системе контроля версий',
            'vacancy_part': 'Автоматизация процессов, установка обновлений операционной системы и критических обновлений для ПО Oracle'
        },
        {
            'similarity': 0.4353,
            'standard_part': 'Внутренние нормативные документы, регламентирующие требования к программному коду, порядок отражения изменений в системе контроля версий',
            'vacancy_part': 'Автоматизация процессов, установка обновлений операционной системы и критических обновлений для ПО Oracle'
        }
    ]

    functions = [
        {
            'weight': 2.34,
            'name': 'Прием платежей за коммунальные и другие услуги',
            'parts': parts
        },
        {
            'weight': 5.35,
            'name': 'Прием платежей за коммунальные и другие услуги',
            'parts': parts
        },
        {
            'weight': 5.45,
            'name': 'Прием платежей за коммунальные и другие услуги',
            'parts': parts
        }
    ]

    general_functions = [
        {
            'weight': 35.345,
            'name': 'Обслуживание абонентского (терминального) телекоммуникационного оборудования',
            'functions': functions
        },
        {
            'weight': 35.345,
            'name': 'Производство, сервисное обслуживание и ремонт средств защиты информации',
            'functions': functions
        },
        {
            'weight': 35.345,
            'name': 'Выполнение работ по монтажу телекоммуникационного оборудования',
            'functions': functions
        },
        {
            'weight': 35.345,
            'name': 'Управление развитием средств и систем защиты СССЭ от НСД',
            'functions': functions
        },
        {
            'weight': 35.345,
            'name': 'Руководство продажами организации, формирование сбытовой политики в части инфокоммуникационных систем и/или их составляющих',
            'functions': functions
        }
    ]

    return render_template('profession.html',
                           title='profession',
                           best_vacancies=best_vacancies,
                           worst_vacancies=worst_vacancies,
                           profession=Profstandard.query.get(prof_id).name,
                           general_functions=general_functions)


@app.route('/vacancy')
def vacancy():
    return 'vacancy ' + str(request.args['id'])


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


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(debug=True)
