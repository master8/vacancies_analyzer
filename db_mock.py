import pandas as pd
from app import db
from models import Region
from datetime import datetime
from models import ClassifiedVacancy, Vacancy

print(datetime.utcnow())

# cl_value = ClassificatedVacancy(id=1, vacancy_id=1, profstandard_id=14, probability=0.7)
# value=Vacancy(id=1, name='Программист', region_id=1, source_id=1, create_date = datetime.utcnow())

date = datetime.now()
gdate = date.strftime("%m-%d-%Y")
print(gdate)

fdate = '12-20-2009'
vgdate = datetime.strptime(fdate,"%m-%d-%Y")
vvgdate = vgdate.strftime("%m-%d-%Y")



# db.session.add(value)
# db.session.add(cl_value)

# cl_value = ClassificatedVacancy(id=2, vacancy_id=1, profstandard_id=12, probability=0.6)
value=Vacancy(id=3, name='Программист', region_id=2, source_id=1, create_date = gdate)
cl_value = ClassifiedVacancy(id=4, vacancy_id=3, profstandard_id=14, probability=0.6)

print('готово')
db.session.add(value)
db.session.add(cl_value)


db.session.commit()