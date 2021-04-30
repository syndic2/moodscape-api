from flask_cors import CORS
from flask_mail import Mail
from flask_graphql_auth import GraphQLAuth
from flask_pymongo import PyMongo

cors= CORS()
mail= Mail()
auth= GraphQLAuth()
mongo= PyMongo()
