import pandas as pd
from app import db
from models import *
from datetime import datetime

# Накатывать на чистую базу

# first_source = Source(id=1, name='HeadHunter', is_support=True)
# second_source = Source(id=2, name='SuperJob', is_support=False)
#
# db.session.add(first_source)
# db.session.add(second_source)
#
# db.session.commit()
#
# regions = pd.read_csv('data/regions.csv')
#
# for index, region in regions.iterrows():
#     value = Region(id=region['area_id'], name=region['area_name'])
#     db.session.add(value)
#
# db.session.commit()


vacancies_parts_types = pd.read_csv('data/vacancies_parts_types.csv')

for index, type in vacancies_parts_types.iterrows():
    value = VacancyPartType(id=type['id'], name=type['name'])
    db.session.add(value)

db.session.commit()


standards_parts_types = pd.read_csv('data/standards_parts_types.csv')

for index, type in standards_parts_types.iterrows():
    value = ProfstandardPartType(id=type['id'], name=type['name'])
    db.session.add(value)

db.session.commit()


# profstandards = pd.read_csv('data/profstandards.csv', dtype='str')
# profstandards['id'] = profstandards['id'].astype('int')
# profstandards['is_support'] = profstandards['is_support'].apply(lambda v: v == 'True')
#
# for index, pr in profstandards.iterrows():
#     value = Profstandard(id=pr['id'], name=pr['name'], code=pr['code'], is_support=pr['is_support'])
#     db.session.add(value)
#
# db.session.commit()
#
# vacancies = pd.read_csv('data/vacancies.csv')
#
# for index, vacancy in vacancies.iterrows():
#     value = Vacancy(id=vacancy['id'],
#                     name=vacancy['name'],
#                     region_id=vacancy['region_id'],
#                     source_id=vacancy['source_id'],
#                     create_date=datetime.strptime(vacancy['create_date'], "%Y-%m-%dT%H:%M:%S%z"))
#     db.session.add(value)
#
# db.session.commit()
#
# classified_vacancies = pd.read_csv('data/classified_vacancies.csv')
#
# for index, vacancy in classified_vacancies.iterrows():
#
#     labels = vacancy['labels'].split(',')
#     for label in list(map(str.strip, labels)):
#         value = ClassifiedVacancy(
#             vacancy_id=vacancy['vacancy_id'],
#             profstandard_id=label,
#             probability=vacancy['p' + str(label)]
#         )
#         db.session.add(value)
#
# db.session.commit()
