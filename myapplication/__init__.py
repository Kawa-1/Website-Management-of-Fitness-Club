from myapplication.logger import get_logger
from myapplication.config import YamlConf
from myapplication.security import CryptoKey
# from myapplication.db import db_before_request, db_init_app, get_cursor, init_tables
from flask import Flask, jsonify, g, request, json, current_app
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from datetime import datetime
from myapplication.error_handler.err_handler import error_handler


log = get_logger(__name__)
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    printer("\tWELCOME SERVER FLASK!!!")
    #log.info("Starting server...")
    app = Flask(__name__)
    api = Api(app)

    app.config.from_mapping(SECRET_KEY='dev')

    crypt_ob = CryptoKey()
    app.config['CRYPTO_KEY'] = crypt_ob

    conf_db = YamlConf.get_yaml_postgres()
    app.config['DB_DRIVER'] = conf_db['driver']
    app.config['DB_HOST'] = conf_db['host']
    app.config['DB_NAME'] = conf_db['dbname']
    app.config['DB_USER'] = conf_db['user']
    conf_db['password'] = crypt_ob.get_decryption_string(bytes(conf_db['password'], 'utf-8'))
    app.config['DB_PASSWORD'] = conf_db['password']
    app.config['DB_PORT'] = conf_db['port']

    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{app.config['DB_PASSWORD']}@localhost:5432/fitness"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    from myapplication.models import Users, Facilities, Subscriptions, PriceList, Classes, Participation
    db.init_app(app)
    migrate.init_app(app, db)
    db.create_all(app=app)

    app.register_error_handler(HTTPException, error_handler)

    from myapplication.api.auth.api import RegisterUserApi
    api.add_resource(RegisterUserApi, '/api/register')

    from myapplication.api.activities.classes import ActivityApi
    api.add_resource(ActivityApi, "/api/activity/<string:date>")

    @app.route('/', methods=['GET'])
    def hello():
        r = db.engine.execute('SELECT * FROM users;')
        return "<h1>HELLOOOOOO!!!</h1>"

    @app.route('/hello', methods=['GET'])
    def hello_world():
        x = 1
        #init_tables()
        #x = get_cursor().execute("""SELECT * FROM users""")
        #print(x)
        return f'Hello World\n {x}'

    return app

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