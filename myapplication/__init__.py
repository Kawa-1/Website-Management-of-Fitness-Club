from myapplication.logger import get_logger
from myapplication.config import YamlConf
from myapplication.security import CryptoKey
from myapplication.db import db_before_request, db_init_app, get_cursor, init_tables
from flask import Flask, jsonify, g, request
from flask_restful import Api


log = get_logger(__name__)

def create_app():
    #log.info("Starting server...")
    app = Flask(__name__)
    api = Api(app)
    app.config.from_mapping(SECRET_KEY='dev')

    crypt_ob = CryptoKey()
    app.config['CryptoKey'] = crypt_ob

    conf_db = YamlConf.get_yaml_postgres()
    app.config['DB_DRIVER'] = conf_db['driver']
    app.config['DB_HOST'] = conf_db['host']
    app.config['DB_NAME'] = conf_db['dbname']
    app.config['DB_USER'] = conf_db['user']
    conf_db['password'] = crypt_ob.get_decryption_string(bytes(conf_db['password'], 'utf-8'))
    app.config['DB_PASSWORD'] = conf_db['password']
    app.config['DB_PORT'] = conf_db['port']

    #db_init_app(app) Tu jest błąd musimy go rozwiązać elo

    app.before_request(db_before_request)
    init_tables()

    @app.route('/', methods=['GET'])
    def hello_world():
        init_tables()
        return 'Hello World'

    return app
