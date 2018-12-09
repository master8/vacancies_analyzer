from flask import Flask, request
from flask import render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Profstandard

# @app.route('/')
# def hello_world():
#     user = {'username': 'Michael'}
#     return render_template('index.html', title="Hello", user=user)

@app.route('/')
def home():
    professions = [
        {
            'id': 1,
            'name': 'Администратор баз данных'
        },
        {
            'id': 2,
            'name': 'Специалист по информационным системам'
        },
        {
            'id': 3,
            'name': 'Менеджер продуктов в области информационных технологий'
        },
        {
            'id': 4,
            'name': 'Менеджер по информационным технологиям'
        },
        {
            'id': 5,
            'name': 'Руководитель проектов в области информационных технологий'
        },
        {
            'id': 6,
            'name': 'Руководитель разработки программного обеспечения'
        },
        {
            'id': 7,
            'name': 'Технический писатель (специалист по технической документации в области информационных технологий)'
        },
        {
            'id': 8,
            'name': 'Системный аналитик'
        },
        {
            'id': 9,
            'name': 'Специалист по дизайну графических и пользовательских интерфейсов'
        },
        {
            'id': 10,
            'name': 'Системный администратор информационно-коммуникационных систем'
        },
        {
            'id': 11,
            'name': 'Специалист по администрированию сетевых устройств информационно-коммуникационных систем'
        },
        {
            'id': 12,
            'name': 'Системный программист'
        },
        {
            'id': 14,
            'name': 'Программист'
        },
        {
            'id': 15,
            'name': 'Инженер-радиоэлектронщик'
        },
        {
            'id': 16,
            'name': 'Специалист по информационным ресурсам'
        },
        {
            'id': 17,
            'name': 'Архитектор программного обеспечения'
        },
        {
            'id': 18,
            'name': 'Специалист по тестированию в области информационных технологий'
        },
        {
            'id': 19,
            'name': 'Разработчик Web и мультимедийных приложений'
        },
        {
            'id': 20,
            'name': 'Инженер-проектировщик в области связи (телекоммуникаций)'
        },
        {
            'id': 21,
            'name': 'Специалист по интеграции прикладных решений'
        },
    ]
    return render_template('index.html', title='home', professions=professions)


@app.route('/analyze')
def analyze():
    pr = Profstandard.query.get(14)
    return 'analyze results ' + str(request.args) + ' ' + pr.name


if __name__ == '__main__':
    app.run()
