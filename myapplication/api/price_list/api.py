from flask import g
from flask_restful import Resource
from datetime import datetime

timestamp = str(datetime.utcnow())


class PriceOnService(Resource):
    def get(self, service_id=None):
        if service_id is None:
            cmd = """SELECT """
            pass
