import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig:
    SECRET_KEY =               '*'



class DevelopmentConfig(BaseConfig):
    pass

class ProductionConfig(BaseConfig):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
