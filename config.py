import datetime
from os import environ as ENV

from utilities.helpers import upload_path

class BaseConfig:
    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_PORT= 465
    MAIL_USE_TLS= False
    MAIL_USE_SSL= True
    MAIL_USERNAME= ENV.get('MAIL_USERNAME')
    MAIL_PASSWORD= ENV.get('MAIL_PASSWORD')

    JWT_SECRET_KEY= ENV.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES= datetime.timedelta(days= 30) 
    JWT_REFRESH_TOKEN_EXPIRES= datetime.timedelta(days= 35) 

    UPLOAD_FOLDER= upload_path
    
class DevelopmentConfig(BaseConfig):
    MONGO_URI= 'mongodb://localhost:27017/moodscape'

class ProductionConfig(BaseConfig):
    MONGO_URI= ENV.get('MONGO_URI')

config= ProductionConfig()