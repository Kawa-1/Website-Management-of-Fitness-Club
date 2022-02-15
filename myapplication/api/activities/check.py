import re

def check_date_format(date):
    regex = "^[0-9]{4}[-][0-9]{2}[-][0-9]{2}$"
    date = str(date)
    if re.search(regex, date) and len(date) == 10:
        return True
    else:
        return False

def check_year_format(year):
    regex = "^[0-9]{4]"
    year = str(year)
    if re.search(regex, year):
        return True
    else:
        return False

def check_month_format(month):
    regex = "^[0-9]{4}[-][0-9]{2}$"
    month = str(month)
    if re.search(regex, month):
        return True
    else:
        return False

def limit_parameter(f):
    def decorator(*args, **kwargs):
        pass

