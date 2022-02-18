from functools import wraps
from flask import request, g
from bleach import clean
from datetime import datetime

timestamp = str(datetime.utcnow())

#TODO: Let's think upon decorator...
def limit_offset(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        limit_ = request.args.get("limit")
        offset_ = request.args.get("offset")
        g.limit = 5
        g.offset = 0
        if limit_ is not None and isinstance(limit_, int):
            try:
                g.limit = int(limit_)
            except Exception as e:
                err_resp = {"message": {
                    "description": "Something went wrong",
                    "status": 400, "name": "invalid format of parameter limit", "method": "GET",
                    "timestamp": timestamp}}
                return err_resp, 400

        if offset_ is not None and isinstance(offset_, int):
            try:
                g.offset = int(offset_)
            except Exception as e:
                err_resp = {"message": {
                    "description": "Something went wrong",
                    "status": 400, "name": "invalid format of parameter offset", "method": "GET",
                    "timestamp": timestamp}}
                return err_resp, 400

        return f(*args, **kwargs)
    return decorator

def valid_date_day(date: str) -> bool:
    """Check if such date exists in format: "%Y-%m-%d"""
    try:
        year, month, day = date.split('-')
        datetime(int(year), int(month), int(day))
        return True

    except Exception:
        return False

def valid_date_H_M(date: str) -> bool:
    """Check if such date exists in format: "%Y-%m-%d %H-%M"""
    try:
        date = date.split(' ')
        year, month, day = date[0].split('-')
        hour, minute = date[1].split('-')
        datetime(int(year), int(month), int(day), int(hour), int(minute))
        return True

    except Exception:
        return False

def valid_date_Y(date: str) -> bool:
    month = 1
    day = 1
    try:
        datetime(int(date), month, day)
        return True
    except Exception:
        return False

def valid_date_Y_m(date: str) -> bool:
    day = 1
    try:
        year, month = date.split('-')
        datetime(int(year), int(month))
        return True
    except Exception:
        return False