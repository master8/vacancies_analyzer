from flask import Flask, request
from flask import render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Profstandard, Source, Region


@app.route('/')
def home():
    professions = Profstandard.query.all()
    regions = Region.query.all()
    sources = Source.query.all()
    return render_template('index.html', title='home', professions=professions, regions=regions, sources=sources)


@app.route('/search')
def search():

    region = 'Москва'
    source = 'HeadHunter'
    period = '12.08.2018 - 23.10.2018'

    professions = [
        {
            'profstandard_id': 14,
            'code': '06.086',
            'name': 'Программист',
            'count': 35
        },
        {
            'profstandard_id': 4,
            'code': '06.060',
            'name': 'Системный аналитик',
            'count': 11
        },
        {
            'profstandard_id': 5,
            'code': '06.076',
            'name': 'Менеджер по информационным технологиям',
            'count': 5
        }
    ]
    diagram_link = '../static/diagram/test_diagram.svg'

    return render_template('results.html',
                           title='results',
                           region=region,
                           source=source,
                           period=period,
                           professions=professions,
                           diagram_link=diagram_link)


@app.route('/profession')
def profession():
    return 'profession ' + str(request.args['id'])


if __name__ == '__main__':
    app.run()
