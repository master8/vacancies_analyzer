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

from models import Profstandard, Source, Region, Vacancy, ClassificatedVacancy


# @app.route('/')
# def hello_world():
#     user = {'username': 'Michael'}
#     return render_template('index.html', title="Hello", user=user)

@app.route('/')
def home():
    professions = Profstandard.query.all()
    regions = Region.query.all()
    sources = Source.query.all()
    return render_template('index.html', title='home', professions=professions, regions=regions, sources=sources)


@app.route('/analyze')
def analyze():
    pr = Profstandard.query.get(14)
    return 'analyze results ' + str(request.args.getlist('prof')) + ' ' + pr.name

@app.route('/search')
def search():
    reg_id = request.args.get('region')
    region = Region.query.filter_by(id= reg_id).first().name

    source_id =request.args.get('source')
    source = Source.query.filter_by(id= source_id).first().name

    sdate = request.args.get('sdate')
    edate = request.args.get('edate')

    dt_sdate = datetime.strptime(sdate,"%Y-%m-%d")
    dt_edate = datetime.strptime(edate,"%Y-%m-%d")

    period = 'from: ' + str(sdate)+' to: '+str(edate) #месяц - день - год

    prof_id_list = request.args.getlist('prof')


    professions = []


    for prof_id in prof_id_list:
        count = 0

        class_vacancy = ClassificatedVacancy.query.filter_by(profstandard_id = prof_id)
        for sample in class_vacancy:
            vacancy = Vacancy.query.filter_by(id=sample.vacancy_id)\
                .filter(Vacancy.create_date <= dt_edate)\
                .filter(Vacancy.create_date >= dt_sdate)\
                .filter_by(region_id = reg_id)\
                .filter_by(source_id = source_id)
            for i in vacancy:
                count +=1


        prof_dict = {
            'profstandard_id': prof_id,
            'code': Profstandard.query.get(prof_id).code,
            'name': Profstandard.query.get(prof_id).name,
            'count': count
        }
        professions.append(prof_dict)


    if professions == []:
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
                           diagram_link=diagram_link)



def plot_search(professions):
    t = []
    num = []
    for i in professions:
        t.append(i['code'])
        num.append(i['count'])
    x = np.array(t)
    y = np.array(num)

    diagram = sns.barplot(x=x, y=y, palette="rocket")
    dia = diagram.get_figure()
    dia.savefig('./static/diagram/test_diagram.svg')
    
    diagram_link = '../static/diagram/test_diagram.svg'
    #diagram_link = 'test_diagram.svg'
    return diagram_link



if __name__ == '__main__':
    app.run(debug = True)