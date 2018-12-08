from datetime import datetime
from app import db

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    vacancies = db.relationship('Vacancies', backref='region', lazy='dynamic')

    def __repr__(self):
        return '<Region {}>'.format(self.name)

class Vacancies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.Integer, db.ForeignKey('profstandard.label'))
    accuracy = db.Column(db.Float)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    name = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True)

    vacancy_part = db.relationship('VacancyPart', backref='vacancy', lazy='dynamic')
    profstandards = db.relationship('Profstandard', backref='vacancy', lazy='dynamic')

    def __repr__(self):
        return '<Vacancies {}>'.format(self.name)

class VacancyPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vac_id = db.Column(db.Integer, db.ForeignKey('vacancies.id'))
    competence = db.Column(db.Integer, db.ForeignKey('competence.id'))
    simularity = db.Column(db.Float)
    text = db.Column(db.Text) #? длина части вакансии или формат
    requirements_id = db.Column(db.Integer, db.ForeignKey('requirements.id'))

    competences = db.relationship('Competence', backref ='vac_part', lazy ='dynamic')

    def __repr__(self):
        return '<VacancyPart {}>'.format(self.text)

class Requirements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    vacancies = db.relationship('VacancyPart', backref ='requirement', lazy ='dynamic') #хз так или нет

    def __repr__(self):
        return '<Requirements {}>'.format(self.name)

class Competence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    comp_type = db.Column(db.String(64), index=True)
    function_id = db.Column(db.Integer, db.ForeignKey('function.id'))

    vacancy_parts = db.relationship('VacancyPart', backref='competence', lazy='dynamic')

    def __repr__(self):
        return '<Competence {}>'.format(self.name)


class Function(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    general_id = db.Column(db.Integer, db.ForeignKey('general.id'))

    competences = db.relationship('Competence', backref='function', lazy='dynamic')

    def __repr__(self):
        return '<Function {}>'.format(self.name)

class General(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    stand_code = db.Column(db.Integer, db.ForeignKey('profstandard.code'))

    functions = db.relationship('Function', backref='general_function', lazy='dynamic')

    def __repr__(self):
        return '<General {}>'.format(self.name)

class Profstandard(db.Model):
    code = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    label = db.Column(db.Integer, primary_key=True)

    generals = db.relationship('General', backref='profstandard', lazy='dynamic')
    vacancies = db.relationship('Vacancies', backref ='profstandard', lazy ='dynamic')

    def __repr__(self):
        return '<Profstandard {}>'.format(self.name)

    