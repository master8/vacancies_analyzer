from models import *
from datetime import datetime


class Competence:
    def __init__(self,
                 code: str,
                 name: str):
        super().__init__()

        self.code = code
        self.name = name


class Params:
    def __init__(self,
                 region: Region,
                 source: Source,
                 start_date: datetime,
                 end_date: datetime,
                 profession_ids: list) -> None:
        super().__init__()

        self.region = region
        self.source = source
        self.start_date = start_date
        self.end_date = end_date
        self.profession_ids = profession_ids

    def dict(self):
        return {
            'region': self.region.id,
            'source': self.source.id,
            'start_date': datetime.strftime(self.start_date, "%Y-%m-%d"),
            'end_date': datetime.strftime(self.end_date, "%Y-%m-%d"),
            'profession_ids': self.profession_ids
        }

    def get_query(self):
        return '?' + '&'.join(['prof=' + str(prof) for prof in self.profession_ids]) \
               + f'&region={self.region.id}&sdate={datetime.strftime(self.start_date, "%Y-%m-%d")}' \
                 f'&edate={datetime.strftime(self.end_date, "%Y-%m-%d")}&source={self.source.id}'


class SelectedItems:
    def __init__(self,
                 profession_id,
                 general_fun_ids,
                 fun_ids,
                 part_ids) -> None:
        super().__init__()

        self.profession_id = profession_id
        self.general_fun_ids = general_fun_ids
        self.fun_ids = fun_ids
        self.part_ids = part_ids

    def dict(self):
        return {
            'profession_id': self.profession_id,
            'general_fun_ids': self.general_fun_ids,
            'fun_ids': self.fun_ids,
            'part_ids': self.part_ids
        }


class Selected:
    def __init__(self) -> None:
        super().__init__()
        self.items = {}
