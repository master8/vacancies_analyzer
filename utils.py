from datetime import datetime


def get_date(date: str) -> datetime:
    return datetime.strptime(date, "%Y-%m-%d")

