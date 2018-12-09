import pandas as pd
from app import db
from models import Region
from models import Profstandard

# Накатывать на чистую базу

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