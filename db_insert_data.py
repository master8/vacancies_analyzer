import pandas as pd
from app import db
from models import Region
from models import Profstandard
from models import Vacancy
from models import Source
from models import ClassificatedVacancy
from datetime import datetime

#Накатывать на чистую базу

first_source = Source(id=1,name='HeadHunter',is_support=True)
second_source = Source(id=2,name='SuperJob',is_support=False)

db.session.add(first_source)
db.session.add(second_source)

db.session.commit()

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    is_support = db.Column(db.Boolean)

    vacancies = db.relationship('Vacancy', backref ='source', lazy ='dynamic')

    def __repr__(self):
        return '<Source {}>'.format(self.name)


regions = pd.read_csv('data/regions.csv')

for index, region in regions.iterrows():
    value = Region(id=region['area_id'], name=region['area_name'])
    db.session.add(value)

db.session.commit()


profstandards = pd.read_csv('data/profstandards.csv', dtype='str')
profstandards['id'] = profstandards['id'].astype('int')
profstandards['is_support'] = profstandards['is_support'].apply(lambda v: v == 'True')

for index, pr in profstandards.iterrows():
    value = Profstandard(id=pr['id'], name=pr['name'], code=pr['code'], is_support=pr['is_support'])
    db.session.add(value)

db.session.commit()


vacancies = pd.read_csv('data/vacancies.csv')

for index, vacancy in vacancies.iterrows():
    value = Vacancy(id=vacancy['id'],
                    name=vacancy['name'],
                    region_id=vacancy['region_id'],
                    source_id=vacancy['source_id'],
                    create_date=datetime.strptime(vacancy['create_date'], "%Y-%m-%dT%H:%M:%S%z"))
    db.session.add(value)

db.session.commit()


classified_vacancies = pd.read_csv('data/classified_vacancies.csv')

for index, vacancy in classified_vacancies.iterrows():

    labels = vacancy['labels'].split(',')
    for label in list(map(str.strip, labels)):
        value = ClassificatedVacancy(
            vacancy_id=vacancy['vacancy_id'],
            profstandard_id=label,
            probability=vacancy['p' + str(label)]
        )
        db.session.add(value)

db.session.commit()
