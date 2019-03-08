from pipeline import similarity
import pandas as pd

vacancies = pd.read_csv('../data/vacancy_parts_for_matching.csv')
profstandards = pd.read_csv('../data/profstandard_parts_for_matching.csv')

data = similarity.matching_parts(vacancies, profstandards)
data.to_csv('savings.csv')
