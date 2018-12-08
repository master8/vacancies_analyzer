from datetime import datetime
from app import db

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Region {}>'.format(self.name)

class Vacancies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.relationship('Profstandard', backref ='vacancy', lazy ='dynamic')
    accuracy = db.Column(db.Float)
    region_id = db.relationship('Region', backref ='vacancy', lazy ='dynamic')
    name = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Vacancies {}>'.format(self.name)

class VacancyPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vac_id = db.relationship('Vacancies', backref ='vac_part', lazy ='dynamic')
    competence = db.relationship('Competence', backref ='vac_part', lazy ='dynamic')
    simularity = db.Column(db.Float)
    text = db.Column(db.MediumText) #? длина части вакансии или формат
    requirements_id = db.relationship('Requirements', backref ='vac_part', lazy ='dynamic')

    def __repr__(self):
        return '<VacancyPart {}>'.format(self.text)

class Requirements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Requirements {}>'.format(self.name)

class Competence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    comp_type = db.Column(db.String(64), index=True)
    function_id = db.relationship('Function', backref ='competence', lazy ='dynamic')

    def __repr__(self):
        return '<Competence {}>'.format(self.name)


class Function(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    general_id = db.relationship('General', backref ='competence', lazy ='dynamic')

    def __repr__(self):
        return '<Function {}>'.format(self.name)

class General(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    stand_code = db.relationship('Profstandard', backref ='competence', lazy ='dynamic')

    def __repr__(self):
        return '<General {}>'.format(self.name)

class Profstandard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    label = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Profstandard {}>'.format(self.name)

    