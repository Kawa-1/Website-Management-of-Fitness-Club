from functools import wraps
from flask import request
from datetime import datetime

timestamp = str(datetime.utcnow())

#TODO: Let's think upon decorator...
def limit_offset(f):
    def decorator(*args, **kwargs):
        limit_ = request.args.get("limit")
        offset_ = request.args.get("offset")

        if limit_ is not None:
            try:
                limit = int(limit_)
            except Exception as e:
                err_resp = {"message": {
                    "description": "Argument limit must be int",
                    "status": 400, "name": "invalid format of parameter limit", "method": "GET",
                    "timestamp": timestamp}}
                return err_resp, 400

        if offset_ is not None:
            try:
                offset = int(offset_)
            except Exception as e:
                err_resp = {"message": {
                    "description": "Argument offset must be int",
                    "status": 400, "name": "invalid format of parameter offset", "method": "GET",
                    "timestamp": timestamp}}
                return err_resp, 400
