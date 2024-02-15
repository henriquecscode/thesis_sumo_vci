import datetime

file_datetime_format = "%Y-%m-%d-%H-%M-%S"

def get_current_time():
    return datetime.datetime.now()


def format_date_for_file(date: datetime.datetime) -> str:
    return date.strftime(file_datetime_format)

def get_current_time_file_format() -> str:
    return format_date_for_file(get_current_time()) 