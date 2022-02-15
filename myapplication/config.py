from __future__ import annotations
import yaml
import platform
from pathlib import Path


class Conf:

    @staticmethod
    def load_conf_mail(app: Mail, crypt_ob: CryptoKey) -> None:
        conf_db = YamlConf.get_yaml_mail()
        app.config['MAIL_SERVER'] = conf_db['mail_server']
        app.config['MAIL_USERNAME'] = conf_db['mail_username']
        app.config['MAIL_PASSWORD'] = crypt_ob.get_decryption_string(bytes(conf_db['mail_password'], 'utf-8'))
        app.config['MAIL_PORT'] = conf_db['mail_port']
        app.config['MAIL_USE_SSL'] = conf_db['mail_use_ssl']
        app.config['MAIL_USE_TLS'] = conf_db['mail_use_tls']

    @staticmethod
    def load_conf_db(app: Flask, crypt_ob: CryptoKey) -> None:
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


class YamlConf:

    @staticmethod
    def get_path_conf(name_of_file: str):
        _path = ''
        basedir = Path(__file__).parent.absolute()
        if platform.system() == 'Darwin':
            _path = '{}{}'.format(basedir, f'/conf/{name_of_file}')
        elif platform.system() == 'Windows':
            _path = '{}{}'.format(basedir, f'\\conf\\{name_of_file}')
        elif platform.system() == 'Linux':
            _path = '{}{}'.format(basedir, f'/conf/{name_of_file}')

        print(_path)
        return _path

    @staticmethod
    def get_yaml_postgres() -> dict:
        """Getting parameters involved with Database (Postgres) connection

            PARAMETERS:
                None
            RETURN:
                dict:
                    keys:
                        - dbname: str
                        - user: str
                        - password: str
                        - host: str
                        - port: int
        """
        file_yaml = YamlConf.get_path_conf("config_pg.yaml")
        with open(file_yaml, mode='r') as f_handler:
            data = yaml.safe_load(f_handler)

        data = data['postgres']

        return data

    @staticmethod
    def get_yaml_mail() -> dict:
        """Getting parameters involved with configuration of mail server and user

        PARAMETERS:
            None
        RETURN:
            dict:
                keys:
                    - mail_server: str
                    - mail_username: str
                    - mail_password: str
                    - mail_port: int
                    - mail_use_ssl: bool
                    - mail_use_tls: bool
        """

        file_yaml = YamlConf.get_path_conf("config_mail.yaml")
        with open(file_yaml, mode='r') as f_handler:
            data = yaml.safe_load(f_handler)

        data = data['mail']

        return data

#print(YamlConf.get_yaml_postgres("config_pg.yaml"))