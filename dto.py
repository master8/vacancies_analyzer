from models import *
from datetime import datetime


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
