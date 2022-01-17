import psycopg2
import platform
from flask import current_app, g
from pathlib import Path


def init_tables():
    _path = ''
    basedir = Path(__file__).parent.absolute()
    if platform.system() == 'Darwin':
        _path = '{}{}'.format(basedir, '/models.txt')
    elif platform.system() == 'Windows':
        _path = '{}{}'.format(basedir, '\\models.txt')
    elif platform.system() == 'Linux':
        _path = '{}{}'.format(basedir, '/models.txt')

    with open(_path) as file:
        tables = file.read()

    # g.cursor == get_cursor()
    g.cursor.execute(tables)
    commit()
    db_close()


def get_db():
    if 'db' not in g:
        if current_app.config['DB_DRIVER'] == 1:
            g.db = psycopg2.connect(
                host=current_app.config['DB_HOST'],
                database=current_app.config['DB_NAME'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                port=current_app.config['DB_PORT']
            )
            g.db.autocommit = True
        else:
            g.db = psycopg2.connect(
                host=current_app.config['DB_HOST'],
                database=current_app.config['DB_NAME'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                port=current_app.config['DB_PORT'],
                autocommit=True
            )

    return g.db

def get_cursor():
    if 'cursor' not in g:
             g.cursor = get_db().cursor()

    return g.cursor

def begin_transaction():
    get_db().start_transaction

def commit():
    get_db().commit()

def rollback():
    get_db().rollback()

def db_close():
    cur = g.pop('cursor', None)

    if cur is not None:
        cur.close()

    db = g.pop('db', None)

    if db is not None:
        db.close()

def db_init_app(app):
    app.teardown_appcontext(db_close)

def db_before_request() -> None:
    get_db()
    get_cursor()
    return None
