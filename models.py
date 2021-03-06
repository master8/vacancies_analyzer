from app import db


class Profstandard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(128), index=True, unique=True)
    is_support = db.Column(db.Boolean)

    general_funcions = db.relationship('GeneralFunction', backref='profstandard', lazy='dynamic')
    classified_vacancies = db.relationship('ClassifiedVacancy', backref='profstandard', lazy='dynamic')

    def __repr__(self):
        return '<Profstandard {}>'.format(self.name)


class GeneralFunction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64))
    profstandard_id = db.Column(db.Integer, db.ForeignKey('profstandard.id'), index=True)
    name = db.Column(db.String(128), index=True, unique=True)
    qualification_level = db.Column(db.Integer)

    functions = db.relationship('Function', backref='general_function', lazy='dynamic')

    def __repr__(self):
        return '<GeneralFunction {}>'.format(self.name)


class Function(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    code = db.Column(db.String(64))
    general_function_id = db.Column(db.Integer, db.ForeignKey('general_function.id'), index=True)
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
    part_type_id = db.Column(db.Integer, db.ForeignKey('profstandard_part_type.id'), index=True)
    function_id = db.Column(db.Integer, db.ForeignKey('function.id'), index=True)

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
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancy.id'), index=True)
    profstandard_id = db.Column(db.Integer, db.ForeignKey('profstandard.id'), index=True)
    probability = db.Column(db.Float)

    def __repr__(self):
        return '<ClassifiedVacancy {}>'.format(self.vacancy_id)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), index=True)
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'), index=True)
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
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancy.id'), index=True)
    text = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey('vacancy_part_type.id'), index=True)

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
    vacancy_part_id = db.Column(db.Integer, db.ForeignKey('vacancy_part.id'), index=True)
    profstandard_part_id = db.Column(db.Integer, db.ForeignKey('profstandard_part.id'), index=True)
    similarity = db.Column(db.Float, index=True)
    enriched_text = db.Column(db.Text)

    def __repr__(self):
        return '<MatchPart {}>'.format(self.enriched_text)


class ProfstandardPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    profstandard_id = db.Column(db.Integer, db.ForeignKey('profstandard.id'), index=True)
    qualification_level = db.Column(db.Integer)

    def __repr__(self):
        return '<ProfstandardPost {}>'.format(self.name)


class ProfstandardEducation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    profstandard_id = db.Column(db.Integer, db.ForeignKey('profstandard.id'), index=True)
    qualification_level = db.Column(db.Integer)

    def __repr__(self):
        return '<ProfstandardEducation {}>'.format(self.name)


class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    program = db.Column(db.String(128))

    def __repr__(self):
        return '<University {}>'.format(self.name)


class EducationProgram(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    university_id = db.Column(db.Integer())
    name = db.Column(db.String(128))
    annotation = db.Column(db.String(255))
    know = db.Column(db.String(255))
    can = db.Column(db.String(255))
    own = db.Column(db.String(255))
    themes = db.Column(db.String(255))

    def __repr__(self):
        return '<EducationProgram {}>'.format(self.name)


class ZYN(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    university_id = db.Column(db.Integer())
    discipline_name = db.Column(db.String(128))
    know = db.Column(db.String(255))
    can = db.Column(db.String(255))
    own = db.Column(db.String(255))

    def __repr__(self):
        return '<ZYN {}>'.format(self.name)


class Parts(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    university_id = db.Column(db.Integer())
    discipline_name = db.Column(db.String(128))
    parts_id = db.Column(db.Integer())
    parts_name = db.Column(db.String(255))

    def __repr__(self):
        return '<parts {}>'.format(self.name)


class PartsThemes(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    university_id = db.Column(db.Integer())
    discipline_name = db.Column(db.String(128))
    parts_id = db.Column(db.Integer())
    themes = db.Column(db.String(255))

    def __repr__(self):
        return '<parts_themes {}>'.format(self.name)
