import pandas as pd
import numpy as np

# v = pd.read_csv('data/u_vacancies_parts.csv')
# v['ind'] = v['id_vacancy_part']
# vr = pd.DataFrame()
# vr['vacancy_id'] = v.id
# vr['id'] = pd.Series(range(1, vr.vacancy_id.count() + 1), index=vr.index)
# vr['text'] = v.text
# tv = pd.read_csv('data/d_vacancies_parts_types.csv')
# vr['type_id'] = v.type.apply(lambda x: np.array(tv[tv.name == x].id)[0])
# t = pd.DataFrame()
# t['id'] = vr.id
# t['vacancy_id'] = vr.vacancy_id
# t['text'] = vr.text
# t['type_id'] = vr.type_id
# vr['ind'] = v.ind
# t.to_csv('data/t_vacancies_parts.csv', index=False)
# vr.to_csv('data/u_vacancies_parts_t.csv', index=False)
from app import db
from models import MatchPart

v = pd.read_csv('data/u_vacancies_parts_t.csv')
p = pd.read_csv('data/u_standards_parts_t.csv')
s = pd.DataFrame()
co = pd.read_csv('data/sim.csv')
co = co[co.id_profstandard_part.notna()]
co.id_profstandard_part = co.id_profstandard_part.astype('int')


def getProfstandard_id(x):
    temp = np.array(p[p.ind == x].id)
    if len(temp) > 0:
        return temp[0]
    else:
        return None


s['profstandard_part_id'] = co.id_profstandard_part.apply(getProfstandard_id)
s = s[s.profstandard_part_id.notna()]
s['vacancy_part_id'] = co.id_vacancy_part.apply(lambda x: np.array(v[v.ind == x].id)[0])
s['similarity'] = co.sc
s['enriched_text'] = co.prof_text
t = pd.DataFrame()
t['vacancy_part_id'] = s.vacancy_part_id
t['profstandard_part_id'] = s.profstandard_part_id
t['similarity'] = s.similarity
t['enriched_text'] = s.enriched_text
t.to_csv('data/t_match_parts.csv', index=False)

match_parts = pd.read_csv('data/t_match_parts.csv')

for index, part in match_parts.iterrows():
    value = MatchPart(vacancy_part_id=part['vacancy_part_id'],
                      profstandard_part_id=part['profstandard_part_id'],
                      similarity=part['similarity'],
                      enriched_text=part['enriched_text'])
    db.session.add(value)

db.session.commit()
