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

    from myapplication.models import Users, Facilities, Subscriptions, PriceList, Classes, Participation
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
    api.add_resource(UserActivityApi, "/api/user_activity/<int:class_id>", "/api/user_activity")

    from myapplication.api.activities.classes import ActivityApi
    api.add_resource(ActivityApi, "/api/activity_api/<string:date>", "/api/activity_api")

    from myapplication.api.instructors.api import InstructorsApi
    api.add_resource(InstructorsApi, "/api/instructors")

    from myapplication.api.auth.api import Test
    api.add_resource(Test, "/test")

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