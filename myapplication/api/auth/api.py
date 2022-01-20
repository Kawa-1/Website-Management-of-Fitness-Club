from flask_restful import Resource, request, current_app
from datetime import datetime
from flask import json
from werkzeug.security import generate_password_hash, check_password_hash
from myapplication.api.auth.auth import check_email, check_postcode, check_number, sanitize
from myapplication import db
from myapplication.models import Users
from myapplication.error_handler.err_handler import error_handler


class RegisterUserApi(Resource):
    def post(self):
        err_resp = {"errors": [{"description": "Provided empty field, bad semantics, something exists so far etc.",
                                "method": "POST", "name": "Failed registration", "status": 400, "timestamp": datetime.now()}]}
        err_resp = json.dumps(err_resp, indent=4, sort_keys=True)

        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        city = request.form.get('city')
        street = request.form.get('street')
        house_number = request.form.get('house_number')
        postcode = request.form.get('postcode')
        email = request.form.get("email")
        password = request.form.get("password")
        repeat_password = request.form.get("repeat_password")



        # [(1, 'Kamil', 'Kamilowy', 'BC', 'naulicy', 9, '40', 'tarantino@o2.com', 'plain_text_pass', None, None)]
        user = Users.query.filter_by(email=email).first()
        print(user)
        cmd = 'SELECT * FROM fit.users WHERE users.email=\'%s\'' % email
        user = db.session.execute(cmd).cursor.fetchone()
        print(user)
        if check_email(email) is False or user:
            return err_resp

        if len(first_name) > 30 or len(first_name) < 2 or len(last_name) > 30 or len(last_name) < 2 or len(city) > 30 or len(city) < 2 or\
            len(street) > 30 or len(street) < 2 or len(password) > 30 or len(password) < 8:
            return err_resp

        if check_postcode(postcode) is False:
            return err_resp

        if password != repeat_password:
            return err_resp

        if check_number(house_number) is False:
            return err_resp

        first_name = sanitize(first_name)
        last_name = sanitize(last_name)
        city = sanitize(city)
        street = sanitize(street)
        house_number = sanitize(house_number)
        postcode = sanitize(postcode)
        email = sanitize(email)
        password = sanitize(password)

        password = generate_password_hash(password)
        new_user = Users(first_name=first_name, last_name=last_name, city=city, street=street, house_number=house_number,
                         postcode=postcode, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        created_resp = {"information": [{"description": "new user created", "status": 201, "name": "registration", "method": "POST",
                                "timestamp": datetime.now()}], "user": [{"first_name": first_name, "last_name": last_name}]}
        created_resp = json.dumps(created_resp, indent=4, sort_keys=True)

        return created_resp, 201


class LoginUserApi(Resource):
    pass




