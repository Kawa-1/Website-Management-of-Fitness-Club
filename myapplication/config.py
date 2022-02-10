import yaml
import platform
from pathlib import Path


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



