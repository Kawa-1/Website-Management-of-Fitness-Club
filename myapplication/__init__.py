import re
from myapplication.logger import get_logger
from myapplication.config import YamlConf, Conf
from myapplication.security import CryptoKey
# from myapplication.db import db_before_request, db_init_app, get_cursor, init_tables
from flask import Flask, jsonify, g, request, json, current_app
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash
from datetime import datetime
from myapplication.error_handler.err_handler import error_handler


log = get_logger(__name__)
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app():
    printer("\tWELCOME SERVER FLASK!!!")
    #log.info("Starting server...")
    app = Flask(__name__)
    api = Api(app)

    app.config.from_mapping(SECRET_KEY='dev')

    crypt_ob = CryptoKey()
    app.config['CRYPTO_KEY'] = crypt_ob

    mail.init_app(app)
    app.config['SAFE_EMAIL'] = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    app.config['MAIL_APP'] = mail
    print(app.config['SAFE_EMAIL'])

    Conf.load_conf_db(app, crypt_ob)
    Conf.load_conf_mail(app, crypt_ob)

    from myapplication.models import Users, Facilities, Subscriptions, PriceList, Activities, Participation, TypesOfActivities, ServiceNames
    db.init_app(app)
    migrate.init_app(app, db)
    db.create_all(app=app)

    app.register_error_handler(HTTPException, error_handler)

    from myapplication.api.auth.api import RegisterUserApi
    api.add_resource(RegisterUserApi, '/api/register')

    from myapplication.api.auth.api import ConfirmEmail
    api.add_resource(ConfirmEmail, "/api/confirm_email/<string:token>")

    from myapplication.api.auth.api import SendEmailConfirmationApi
    api.add_resource(SendEmailConfirmationApi, "/api/send_confirmation_email")

    from myapplication.api.auth.api import LoginUserApi
    api.add_resource(LoginUserApi, "/api/login")

    from myapplication.api.auth.api import LogoutUserApi
    api.add_resource(LogoutUserApi, "/api/logout")

    from myapplication.api.auth.api import PasswordUserApi
    api.add_resource(PasswordUserApi, "/api/change_password")

    from myapplication.api.auth.api import UserApi
    api.add_resource(UserApi, "/api/status")

    from myapplication.api.activities.classes import UserActivityApi
    api.add_resource(UserActivityApi, "/api/user_activity/<int:activity_id>", "/api/user_activity")

    from myapplication.api.activities.classes import ActivityApi
    api.add_resource(ActivityApi, "/api/activity_api/<string:date>", "/api/activity_api")

    from myapplication.api.instructors.api import InstructorsApi
    api.add_resource(InstructorsApi, "/api/instructors")

    from myapplication.api.facilities.api import FacilitiesApi
    api.add_resource(FacilitiesApi, "/api/facilities")

    from myapplication.api.auth.api import Test
    api.add_resource(Test, "/test")

    #TODO: after_requst function which is not in this function, namespace...

    @app.after_request
    def header_after_request(response):
        response.headers["yo"] = "XDDD"
        http_origin = request.environ.get('HTTP_ORIGIN', None)
        http_access_control_request_headers = request.environ.get(
            'HTTP_ACCESS_CONTROL_REQUEST_HEADERS',
            None
        )
        if http_origin and re.search(r'^[a-zA-Z0-9\-\_\/\:\.]+$', http_origin, re.DOTALL):
            response.headers['Content-Type'] = "application/json"
            response.headers['Access-Control-Allow-Origin'] = http_origin
            response.headers['Access-Control-Allow-Credentials'] = "true"
            response.headers['Access-Control-Allow-Methods'] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers[
                'Access-Control-Expose-Headers'] = "*, Content-Disposition, Content-Length, X-Uncompressed-Content-Length"
            if http_access_control_request_headers:
                response.headers['Access-Control-Allow-Headers'] = http_access_control_request_headers
        return response

    # @app.before_first_request
    # def service_names_activities_names(TypesOfActivities=TypesOfActivities, ServiceNames=ServiceNames):
    #     yoga = TypesOfActivities(name_of_activity='yoga')
    #     crossfit = TypesOfActivities(name_of_activity='crossfit')
    #     abs = TypesOfActivities(name_of_activity='abs')
    #     pilates = TypesOfActivities(name_of_activity='pilates')
    #     aerobic = TypesOfActivities(name_of_activity='aerobic')
    #     ems = TypesOfActivities(name_of_activity='ems')
    #     stretching = TypesOfActivities(name_of_activity='stretching')
    #     box = TypesOfActivities(name_of_activity='box')
    #     db.session.add(yoga)
    #     db.session.add(crossfit)
    #     db.session.add(abs)
    #     db.session.add(pilates)
    #     db.session.add(aerobic)
    #     db.session.add(ems)
    #     db.session.add(stretching)
    #     db.session.add(box)

    #     pass_ = ServiceNames(service='pass')
    #     activities = ServiceNames(service='activity')
    #     db.session.add(pass_)
    #     db.session.add(activities)

    #     db.session.commit()
    #     print('done')

    # @app.before_first_request
    # def instructors(Users=Users):
    #     password = generate_password_hash('123456789')
    #     instructor_1 = Users(first_name="Jacek", last_name="Soplica", city="Cracow", street="Reymont", house_number=10,
    #                          postcode="31-100", email='jacek@onet.com', password=password, is_instructor=1, confirmed=1)
    #     instructor_2 = Users(first_name="Ksiądz", last_name="Robak", city="Warsaw", street="Gdanska", house_number=53,
    #                          postcode="00-120", email='robak@onet.com', password=password, is_instructor=1, confirmed=1)
    #     instructor_3 = Users(first_name="Grzegorz", last_name="Brzęczyszczykiewicz", city="Trzebrzeszyn",
    #                          street="Szczedrzykowska",
    #                          house_number=99, postcode="10-333", email='szcz@onet.com', password=password,
    #                          is_instructor=1, confirmed=1)
    #     instructor_4 = Users(first_name="Franek", last_name="Dolas", city="Wroclove", street="fabryczna",
    #                          house_number=38,
    #                          postcode="21-921", email='dolas@onet.com', password=password, is_instructor=1, confirmed=1)
    #     db.session.add(instructor_1)
    #     db.session.add(instructor_2)
    #     db.session.add(instructor_3)
    #     db.session.add(instructor_4)

    #     db.session.commit()
    #     print('done')



    @app.route('/', methods=['GET'])
    def hello():
        arguments = request.args.get("username")
        print(type(arguments))
        #r = db.engine.execute('SELECT * FROM users;')
        data = request.get_json(silent=True)
        print(data)
        g.user = arguments
        print(g)
        print(g.user)
        js = {"message": {"hej": "hej"}}
        js = jsonify(js)
        js.status_code = 200
        #print(data.get('id'))
        return js

    @app.route('/hello', methods=['GET'])
    def hello_world():
        x = 1
        #init_tables()
        #x = get_cursor().execute("""SELECT * FROM users""")
        #print(x)
        return f'Hello World\n {x}'

    return app


class AfterRequest:

    @staticmethod
    def header_after_request(response):
        print("hej")
        http_origin = request.environ.get('HTTP_ORIGIN', None)
        http_access_control_request_headers = request.environ.get(
            'HTTP_ACCESS_CONTROL_REQUEST_HEADERS',
            None
        )
        if http_origin and re.search(r'^[a-zA-Z0-9\-\_\/\:\.]+$', http_origin, re.DOTALL):
            response.headers['Access-Control-Allow-Origin'] = http_origin
            response.headers['Access-Control-Allow-Credentials'] = "true"
            response.headers['Access-Control-Allow-Methods'] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers[
                'Access-Control-Expose-Headers'] = "*, Content-Disposition, Content-Length, X-Uncompressed-Content-Length"
            if http_access_control_request_headers:
                response.headers['Access-Control-Allow-Headers'] = http_access_control_request_headers
        return response


class ValuesInitTable:

    @staticmethod
    def service_names_activities_names(TypesOfActivities, ServiceNames):
        yoga = TypesOfActivities('yoga')
        crossfit = TypesOfActivities('crossfit')
        abs = TypesOfActivities('abs')
        pilates = TypesOfActivities('pilates')
        aerobic = TypesOfActivities('aerobic')
        ems = TypesOfActivities('ems')
        stretching = TypesOfActivities('stretching')
        box = TypesOfActivities('box')
        db.session.add(yoga)
        db.session.add(crossfit)
        db.session.add(abs)
        db.session.add(pilates)
        db.session.add(aerobic)
        db.session.add(ems)
        db.session.add(stretching)
        db.session.add(box)

        pass_ = ServiceNames('pass')
        activities = ServiceNames('activity')
        db.session.add(pass_)
        db.session.add(activities)

        db.session.commit()

    @staticmethod
    def instructors(Users):
        password = generate_password_hash('123456789')
        instructor_1 = Users(first_name="Jacek", last_name="Soplica", city="Cracow", street="Reymont", house_number=10,
                             postcode="31-100", email='jacek@onet.com', password=password, is_instructor=1, confirmed=1)
        instructor_2 = Users(first_name="Ksiądz", last_name="Robak", city="Warsaw", street="Gdanska", house_number=53,
                             postcode="00-120", email='robak@onet.com', password=password, is_instructor=1, confirmed=1)
        instructor_3 = Users(first_name="Grzegorz", last_name="Brzęczyszczykiewicz", city="Trzebrzeszyn", street="Szczedrzykowska",
                             house_number=99, postcode="10-333", email='szcz@onet.com', password=password, is_instructor=1, confirmed=1)
        instructor_4 = Users(first_name="Franek", last_name="Dolas", city="Wroclove", street="fabryczna", house_number=38,
                             postcode="21-921", email='dolas@onet.com', password=password, is_instructor=1, confirmed=1)
        db.session.add(instructor_1)
        db.session.add(instructor_2)
        db.session.add(instructor_3)
        db.session.add(instructor_4)

        db.session.commit()

    @staticmethod
    def facilities(Facilities):
        facility_1 = Facilities(city="Cracow", street="Obi-Wan-Kenobi", house_number=72, postcode="30-110", contact_number=999999999,
                                email="fitness-cracow@fitness.com")
        facility_2 = Facilities(city="Warsaw", street="Aragorn", house_number=12, postcode="00-921", contact_number=911131111,
                                email="fitness-warsaw@fitness.com")
        facility_3 = Facilities(city="Gdansk", street="Geralt", house_number=10, postcode="10-531", contact_number=310131770,
                                email="fitness-gdansk@fitness.com")
        db.session.add(facility_1)
        db.session.add(facility_2)
        db.session.add(facility_3)

        db.session.commit()


def star(func):
    def inner(*args, **kwargs):
        print('*' * 60)
        func(*args, **kwargs)
        print('*' * 60)
    return inner

def percent(func):
    def inner(*args, **kwargs):
        print('%' * 60)
        func(*args, **kwargs)
        print('%' * 60)
    return inner

@star
@percent
def printer(msg):
    print(msg)

# request.method:              GET
# request.url:                 http://127.0.0.1:5000/alert/dingding/test?x=y
# request.base_url:            http://127.0.0.1:5000/alert/dingding/test
# request.url_charset:         utf-8
# request.url_root:            http://127.0.0.1:5000/
# str(request.url_rule):       /alert/dingding/test
# request.host_url:            http://127.0.0.1:5000/
# request.host:                127.0.0.1:5000
# request.script_root:
# request.path:                /alert/dingding/test
# request.full_path:           /alert/dingding/test?x=y
#
# request.args:                ImmutableMultiDict([('x', 'y')])
# request.args.get('x'):       y