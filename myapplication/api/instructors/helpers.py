import re

def check_date_activities(date: str) -> bool:
    regex = "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}-[0-9]{2}$"
    date = str(date)
    if re.search(regex, date):
        return True
    else:
        return False


def check_int(**kwargs):
    """Purpose of this function is to check requested values if they are really int
        PARAMETERS:
            **kwargs
        RETURNS:
            IF val is not int:
                (bool, {key_form: val_form})
            IF every single val is int:
                bool
    """
    for key, val in kwargs.items():
        if not isinstance(val, int):
            return False, {key: val}

    return True, {}