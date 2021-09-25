from flask_cors import CORS
from flask_graphql_auth import GraphQLAuth
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_pymongo import PyMongo

cors= CORS()
auth= GraphQLAuth()
bcrypt= Bcrypt()
mail= Mail()
mongo= PyMongo()