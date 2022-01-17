from myapplication.logger import get_logger
from myapplication.config import YamlConf
from myapplication.security import CryptoKey
from myapplication.db import db_before_request, db_init_app, get_cursor, init_tables
from flask import Flask, jsonify, g, request, json
from flask_restful import Api
from werkzeug.exceptions import HTTPException
from datetime import datetime


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

    @app.errorhandler(HTTPException)
    def not_found(e):
        time = datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        dictionary = {'errors': [{'timestamp': str(time), 'status': int(e.code), 'description': str(e.description),
                                  "name": str(e.name), "method": request.method, "path": request.full_path,
                                  "args": request.args, "host": request.host_url, "url": request.url}]}
        api_body = json.dumps(dictionary)
        response = e.get_response()
        response.data = api_body
        response.content_type = "application/json"
        response.code = e.code
        response.content_language = "en"

        return response

    @app.route('/', methods=['GET'])
    def hello_world():
        init_tables()
        x = get_cursor().execute("""SELECT * FROM users""")
        print(x)
        return f'Hello World\n {x}'

    return app


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