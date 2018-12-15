import pandas as pd
from app import db
from models import *
from datetime import datetime

# Накатывать на чистую базу

first_source = Source(id=1, name='HeadHunter', is_support=True)
second_source = Source(id=2, name='SuperJob', is_support=False)

db.session.add(first_source)
db.session.add(second_source)

db.session.commit()

regions = pd.read_csv('data/d_regions.csv')

for index, region in regions.iterrows():
    value = Region(id=region['area_id'], name=region['area_name'])
    db.session.add(value)

db.session.commit()


vacancies_parts_types = pd.read_csv('data/d_vacancies_parts_types.csv')

for index, type in vacancies_parts_types.iterrows():
    value = VacancyPartType(id=type['id'], name=type['name'])
    db.session.add(value)

db.session.commit()


standards_parts_types = pd.read_csv('data/d_standards_parts_types.csv')

for index, type in standards_parts_types.iterrows():
    value = ProfstandardPartType(id=type['id'], name=type['name'])
    db.session.add(value)

db.session.commit()


standards = pd.read_csv('data/d_standards.csv', dtype='str')
standards['id'] = standards['id'].astype('int')
standards['is_support'] = standards['is_support'].apply(lambda v: v == 'True')

for index, pr in standards.iterrows():
    value = Profstandard(id=pr['id'], name=pr['name'], code=pr['code'], is_support=pr['is_support'])
    db.session.add(value)

db.session.commit()

vacancies = pd.read_csv('data/t_vacancies.csv')

for index, vacancy in vacancies.iterrows():
    value = Vacancy(id=vacancy['id'],
                    name=vacancy['name'],
                    region_id=vacancy['region_id'],
                    source_id=vacancy['source_id'],
                    create_date=datetime.strptime(vacancy['create_date'], "%Y-%m-%dT%H:%M:%S%z"),
                    text=vacancy['text'],
                    link=vacancy['link'])
    db.session.add(value)

db.session.commit()

classified_vacancies = pd.read_csv('data/t_classified_vacancies.csv')

for index, vacancy in classified_vacancies.iterrows():

    labels = vacancy['predict_labels'].split(',')  # or labels
    for label in list(map(str.strip, labels)):
        value = ClassifiedVacancy(
            vacancy_id=vacancy['vacancy_id'],
            profstandard_id=label,
            probability=vacancy[str(label)]  # or 'p' + ...
        )
        db.session.add(value)

db.session.commit()


vacancies_parts = pd.read_csv('data/t_vacancies_parts.csv')

for index, part in vacancies_parts.iterrows():
    value = VacancyPart(id=part['id'], vacancy_id=part['vacancy_id'], text=part['text'], type_id=part['type_id'])
    db.session.add(value)

db.session.commit()


general_functions = pd.read_csv('data/d_standards_general_functions.csv')

for index, function in general_functions.iterrows():
    value = GeneralFunction(id=function['id'],
                            code=function['code'],
                            profstandard_id=function['profstandard_id'],
                            name=function['name'],
                            qualification_level=function['qualification_level'])
    db.session.add(value)

db.session.commit()


functions = pd.read_csv('data/d_standards_functions.csv')

for index, function in functions.iterrows():
    value = Function(id=function['id'],
                     name=function['name'],
                     code=function['code'],
                     general_function_id=function['general_function_id'],
                     qualification_level=function['qualification_level'])
    db.session.add(value)

db.session.commit()


standards_parts = pd.read_csv('data/d_standards_parts.csv')

for index, part in standards_parts.iterrows():
    value = ProfstandardPart(id=part['id'],
                             text=part['text'],
                             part_type_id=part['part_type_id'],
                             function_id=part['function_id'])
    db.session.add(value)

db.session.commit()


match_parts = pd.read_csv('data/t_match_parts.csv')

for index, part in match_parts.iterrows():
    value = MatchPart(vacancy_part_id=part['vacancy_part_id'],
                      profstandard_part_id=part['profstandard_part_id'],
                      similarity=part['similarity'],
                      enriched_text=part['enriched_text'])
    db.session.add(value)

db.session.commit()
