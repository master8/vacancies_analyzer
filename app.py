from flask import Flask, request
from flask import render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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
    count = 0
    prof = request.args.getlist('prof')
    for pid in prof:
        profstandard = Profstandard.query.get(pid)
        class_vacancy = ClassificatedVacancy.query.filter_by(profstandard_id = pid)
    
        for sample in class_vacancy:
            
            vacancy = Vacancy.query.filter_by(id=sample.vacancy_id)
            count +=1
            
    return render_template('results.html',
                           title='results',
                           region=region,
                           source=source,
                           period=period,
                           professions=professions,
                           diagram_link=diagram_link)


    # arguments = request.args
    # profstandards = arguments.getlist('prof')
    # region = arguments.get('region')
    # source = arguments.get('source')
    # sdate = arguments.get('sdate')
    # edate = arguments.get('edate')

    # for pid in profstandards:
    #     profstandard = Profstandard.query.get(id)
    #     prof_name = profstandard.name
    #     class_vacancy = ClassificatedVacancy.query.filter_by(profstandard_id = pid).all()
    #     for sample in class_vacancy:
    #         vac = Vacancy.query.filter_by(id=sample.vacancy_id).first()
    #         vac_count =0 
    #         vac_count +=1
    #         link = 'NULL'
    # prof_id = profstandards


    # obj = {'profstandard_id': prof_id, 'name':prof_name, 'count': vac_count, 'link_diagram':link}
    # return str(priofstandards) #render_template('search.html', title='search', obj=obj)

if __name__ == '__main__':
    app.run(debug = True)