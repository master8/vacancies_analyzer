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
    return 'analyze results ' + str(request.args) + ' ' + pr.name


if __name__ == '__main__':
    app.run()
