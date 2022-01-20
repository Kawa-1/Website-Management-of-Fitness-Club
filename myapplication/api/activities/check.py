import re

def check_date_format(date):
    regex = "^[0-9]{4}[-][0-9]{2}[-][0-9]{2}$"
    date = str(date)
    if re.search(regex, date) and len(date) == 10:
        return True
    else:
        return False
