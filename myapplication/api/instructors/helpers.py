

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

    return True