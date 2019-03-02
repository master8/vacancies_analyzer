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


@app.route('/education_program')
def profession():
    #мне сюда приходит id
    return render_template('education_program.html',
                           title='education program',
                           disciplines=["Программирование", "Базы данных", "Алгоритмы и анализ сложности",
                                        "Анализ данных"],
                           zyn=["Знать", "Уметь", "Владеть"],
                           parts=["Блок-схема алгоритма", "Введение в язык программирования СИ"],
                           themes=["Блок-схема алгоритма", "Массивы -одномерные. Алгоритмы работы с массивами"])


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


if __name__ == '__main__':
    app.run(debug=True)
