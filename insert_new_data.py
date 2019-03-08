import pandas as pd
from app import db
from models import *
from datetime import datetime

regions = pd.read_csv('data/t_universities.csv')

for index, region in regions.iterrows():
    value = University(id=region['id'], name=region['name'], program=region['program'])
    db.session.add(value)
db.session.commit()

disciplines = pd.read_csv('data/bd.csv')
disciplines = disciplines.fillna('0')
for index, r in disciplines.iterrows():
    value = EducationProgram(id=r['id'], university_id=r['университет'], name=r['название дисциплины'], annotation=r['аннотации'], know=r['знать'], can=r['уметь'], own=r['владеть'], themes=r['описание разделов'])
    db.session.add(value)

db.session.commit()