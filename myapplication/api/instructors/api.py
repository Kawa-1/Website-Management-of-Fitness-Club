from flask_restful import Resource
from flask import json, request
from datetime import datetime, timedelta
from myapplication.models import Users

timestamp = str(datetime.utcnow())

class InstructorsApi:
    def get(self):
        pass