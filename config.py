import datetime
from os import environ as ENV

from utilities.helpers import upload_path

class BaseConfig:
    MAIL_SERVER= ENV.get('MAIL_SERVER')
    MAIL_PORT= 587
    MAIL_USE_TLS= True
    MAIL_USE_SSL= False
    MAIL_USERNAME= ENV.get('MAIL_USERNAME')
    MAIL_PASSWORD= ENV.get('MAIL_PASSWORD')

    JWT_SECRET_KEY= ENV.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES= datetime.timedelta(days= 30) 
    JWT_REFRESH_TOKEN_EXPIRES= datetime.timedelta(days= 35) 

    FCM_SERVER_KEY= ENV.get('FCM_SERVER_KEY')

    UPLOAD_FOLDER= upload_path
    SCHEDULER_TIMEZONE= 'Asia/Jakarta'

class DevelopmentConfig(BaseConfig):
    MONGO_URI= 'mongodb://localhost:27017/moodscape'

class ProductionConfig(BaseConfig):
    MONGO_URI= ENV.get('MONGO_URI')

config= ProductionConfig()