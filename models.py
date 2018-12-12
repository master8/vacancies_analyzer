from app import db


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    vacancies = db.relationship('Vacancy', backref='region', lazy='dynamic')

    def __repr__(self):
        return '<Region {}>'.format(self.name)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))
    name = db.Column(db.String(64))
    create_date = db.Column(db.DateTime, index=True)

    vacancy_part = db.relationship('VacancyPart', backref='vacancy', lazy='dynamic')

    def __repr__(self):
        return '<Vacancy {}>'.format(self.name)


class ClassifiedVacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancy.id'))
    profstandard_id = db.Column(db.Integer, db.ForeignKey('profstandard.id'))
    probability = db.Column(db.Float)

    def __repr__(self):
        return '<ClassifiedVacancy {}>'.format(self.name)


class VacancyPart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vac_id = db.Column(db.Integer, db.ForeignKey('vacancy.id'))
    competence_id = db.Column(db.Integer, db.ForeignKey('competence.id'))
    similarity = db.Column(db.Float)
    text = db.Column(db.Text) 
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirement.id'))

    competences = db.relationship('Competence', backref ='vac_part', lazy ='dynamic')

    def __repr__(self):
        return '<VacancyPart {}>'.format(self.text)

class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    vacancies = db.relationship('VacancyPart', backref ='requirement', lazy ='dynamic') #хз так или нет

    def __repr__(self):
        return '<Requirement {}>'.format(self.name)

# class Competence(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(128), index=True)
#     comp_type = db.Column(db.String(64), index=True)
#     function_id = db.Column(db.Integer, db.ForeignKey('function.id'))

#     vacancy_parts = db.relationship('VacancyPart', backref='competence', lazy='dynamic')

#     def __repr__(self):
#         return '<Competence {}>'.format(self.name)


# class Function(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(128), index=True, unique=True)
#     general_id = db.Column(db.Integer, db.ForeignKey('general.id'))

#     competences = db.relationship('Competence', backref='function', lazy='dynamic')

#     def __repr__(self):
#         return '<Function {}>'.format(self.name)

# class General(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(128), index=True, unique=True)
#     stand_code = db.Column(db.Integer, db.ForeignKey('profstandard.id'))

#     functions = db.relationship('Function', backref='general_function', lazy='dynamic')

#     def __repr__(self):
#         return '<General {}>'.format(self.name)


class Profstandard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(128), index=True, unique=True)
    is_support = db.Column(db.Boolean)

    # generals = db.relationship('General', backref='profstandard', lazy='dynamic')
    vacancies = db.relationship('ClassifiedVacancy', backref ='profstandard', lazy ='dynamic')

    def __repr__(self):
        return '<Profstandard {}>'.format(self.name)


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    is_support = db.Column(db.Boolean)

    vacancies = db.relationship('Vacancy', backref ='source', lazy ='dynamic')

    def __repr__(self):
        return '<Source {}>'.format(self.name)
