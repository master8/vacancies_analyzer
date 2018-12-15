import pandas as pd
import numpy as np

v = pd.read_csv('data/u_vacancies_parts.csv')
v['ind'] = v['id_vacancy_part']
vr = pd.DataFrame()
vr['vacancy_id'] = v.id
vr['id'] = pd.Series(range(1, vr.vacancy_id.count() + 1), index=vr.index)
vr['text'] = v.text
tv = pd.read_csv('data/d_vacancies_parts_types.csv')
vr['type_id'] = v.type.apply(lambda x: np.array(tv[tv.name == x].id)[0])
t = pd.DataFrame()
t['id'] = vr.id
t['vacancy_id'] = vr.vacancy_id
t['text'] = vr.text
t['type_id'] = vr.type_id
vr['ind'] = v.ind
t.to_csv('data/t_vacancies_parts.csv', index=False)
vr.to_csv('data/u_vacancies_parts_t.csv', index=False)


p = pd.read_csv('data/u_standards_parts_t.csv')
v = pd.read_csv('data/u_vacancies_parts_t.csv')
s = pd.DataFrame()

