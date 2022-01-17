import yaml
import platform
from pathlib import Path


class YamlConf:

    @staticmethod
    def get_path_conf():
        _path = ''
        basedir = Path(__file__).parent.absolute()
        if platform.system() == 'Darwin':
            _path = '{}{}'.format(basedir, '/conf/config.yaml')
        elif platform.system() == 'Windows':
            _path = '{}{}'.format(basedir, '\\conf\\config.yaml')
        elif platform.system() == 'Linux':
            _path = '{}{}'.format(basedir, '/conf/config.yaml')

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
        file_yaml = YamlConf.get_path_conf()
        with open(file_yaml, mode='r') as f_handler:
            data = yaml.safe_load(f_handler)

        data = data['postgres']

        return data


print(YamlConf.get_yaml_postgres())



