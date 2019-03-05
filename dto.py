from models import *
from datetime import datetime


class Competence:
    def __init__(self,
                 code: str,
                 name: str ):
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

class Selected:
    def __init__(self) -> None:
        super().__init__()
        self.items = {}