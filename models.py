from app import db


class Profstandard(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(128), index=True, unique=True)
    is_support = db.Column(db.Boolean)

    general_funcions = db.relationship('GeneralFunction', backref='profstandard', lazy='dynamic')
    classified_vacancies = db.relationship('ClassifiedVacancy', backref='profstandard', lazy='dynamic')

    def __repr__(self):
        return '<Profstandard {}>'.format(self.name)


class GeneralFunction(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64))
    profstandard_id = db.Column(db.Integer, db.ForeignKey('profstandard.id'))
    name = db.Column(db.String(128), index=True, unique=True)
    qualification_level = db.Column(db.Integer)

    functions = db.relationship('Function', backref='general_function', lazy='dynamic')

    def __repr__(self):
        return '<GeneralFunction {}>'.format(self.name)


class Function(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    code = db.Column(db.String(64))
    general_function_id = db.Column(db.Integer, db.ForeignKey('general_function.id'))
    qualification_level = db.Column(db.Integer)

    parts = db.relationship('ProfstandardPart', backref='function', lazy='dynamic')

    def __repr__(self):
        return '<Function {}>'.format(self.name)


class ProfstandardPartType(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    vacancy_parts = db.relationship('ProfstandardPart', backref='part_type', lazy='dynamic')  # хз так или нет

    def __repr__(self):
        return '<ProfstandardPartType {}>'.format(self.name)


class ProfstandardPart(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    part_type_id = db.Column(db.Integer, db.ForeignKey('profstandard_part_type.id'))
    function_id = db.Column(db.Integer, db.ForeignKey('function.id'))

    matched_parts = db.relationship('MatchPart', backref='competence', lazy='dynamic')

    def __repr__(self):
        return '<Competence {}>'.format(self.text)


class Region(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    vacancies = db.relationship('Vacancy', backref='region', lazy='dynamic')

    def __repr__(self):
        return '<Region {}>'.format(self.name)


class Source(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    is_support = db.Column(db.Boolean)

    vacancies = db.relationship('Vacancy', backref='source', lazy='dynamic')

    def __repr__(self):
        return '<Source {}>'.format(self.name)


class ClassifiedVacancy(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancy.id'))
    profstandard_id = db.Column(db.Integer, db.ForeignKey('profstandard.id'))
    probability = db.Column(db.Float)

    def __repr__(self):
        return '<ClassifiedVacancy {}>'.format(self.vacancy_id)


class Vacancy(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))
    name = db.Column(db.String(128))
    create_date = db.Column(db.DateTime, index=True)
    text = db.Column(db.Text)
    link = db.Column(db.String(128))

    vacancy_part = db.relationship('VacancyPart', backref='vacancy', lazy='dynamic')
    classification = db.relationship('ClassifiedVacancy', backref='vacancy', lazy='dynamic')

    def __repr__(self):
        return '<Vacancy {}>'.format(self.name)


class VacancyPart(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancy.id'))
    text = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey('vacancy_part_type.id'))

    matching = db.relationship('MatchPart', backref='vacancy_part', lazy='dynamic')

    def __repr__(self):
        return '<VacancyPart {}>'.format(self.text)


class VacancyPartType(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    vacancy_parts = db.relationship('VacancyPart', backref='type', lazy='dynamic')  # хз так или нет

    def __repr__(self):
        return '<VacancyPartType {}>'.format(self.name)


class MatchPart(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    vacancy_part_id = db.Column(db.Integer, db.ForeignKey('vacancy_part.id'))
    profstandard_part_id = db.Column(db.Integer, db.ForeignKey('profstandard_part.id'))
    similarity = db.Column(db.Float)
    enriched_text = db.Column(db.Text)

    def __repr__(self):
        return '<MatchPart {}>'.format(self.enriched_text)













