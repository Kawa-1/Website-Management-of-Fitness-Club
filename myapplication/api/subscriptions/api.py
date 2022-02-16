from flask import request, g
from flask_restful import Resource
from myapplication import db
from myapplication.api.auth.auth import token_required
from datetime import datetime, timedelta

timestamp = str(datetime.utcnow())

class StartSubscription(Resource):
    @token_required
    def post(self):
        """This endpoints expect body with every id listed in table subscriptions as well as start_date
            date should be passed in format %Y-%m-%d
            PARAMETERS IN BODY:
                service_id: int
                facility_id: int
                price_id: int
                start_date: str
        """
        post_data = request.get_json()

        service_id = post_data.get('service_id')
        user_id = g.user.id
        facility_id = post_data.get('facility_id')
        price_id = post_data.get('price_id')
        start_date = post_data.get('start_date')

        if service_id is None or not isinstance(service_id, int) or facility_id is None or not isinstance(facility_id, int) or \
                price_id is None or not isinstance(price_id, int) or start_date is None or not isinstance(start_date, str):
            err_resp = {"message": {
                "description": "Not all parameters properly provided",
                "status": 400, "name": "lack of proper parameters", "method": "POST",
                "timestamp": timestamp}}
            return err_resp, 400

        today = datetime.utcnow().strftime('%Y-%m-%d')
        if start_date < today:
            err_resp = {"message": {
                "description": "Cannot make a subscription of pass with older date than today {}".format(today),
                "status": 400, "name": "Invalid date; subscription", "method": "POST",
                "timestamp": timestamp}}
            return err_resp, 400

        cmd = """SELECT * FROM fit.types_of_services WHERE service_id=%d and is_subscription=1""" % service_id
        type_of_pass = db.session.execute('cmd').cursor.fetchone()

        #TODO: pass 30d 1d 1yr


