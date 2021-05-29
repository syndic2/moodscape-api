from flask import Flask, request, jsonify
from flask_graphql import GraphQLView
from bs4 import BeautifulSoup

import requests
import urllib
import json

from config import config
from extensions import cors, mail, auth, mongo
from resources.schema import main_schema, auth_schema
from seeder.schema import seeder_schema

app= Flask(__name__)

app.config.from_object(config)

cors.init_app(app)
mail.init_app(app)
auth.init_app(app)
mongo.init_app(app)

app.add_url_rule('/api/graphql', view_func= GraphQLView.as_view(
    'graphql',
    schema= main_schema, 
    graphiql= True
))

app.add_url_rule('/api/auth', view_func= GraphQLView.as_view(
    'auth',
    schema= auth_schema, 
    graphiql= True
))

app.add_url_rule('/api/seeds', view_func= GraphQLView.as_view(
    'seeds',
    schema= seeder_schema,
    graphiql= True
))

@app.route('/')
def index():
    return jsonify(message= 'Server is online!', status= 'OK')

#@app.route('/scrape-articles')
#def scrape_articles():
#    params= { 
#        'spider_name': 'articles',
#        'start_requests': True
#    }
#
#    if request.args.get('pages'):
#        pages= int(request.args.get('pages'))
#        params['crawl_args']= urllib.parse.quote(json.dumps({ 'pages': pages }))
#
#    response= requests.get('http://localhost:9080/crawl.json', params)
#    data= json.loads(response.text)
#
#    if 'error' in data or 'errors' in data:
#        return jsonify(message= 'Connection trouble or something happend in the server. Please try again.')
#
#    return jsonify(data)

if __name__ == '__main__':
    app.run(debug= True)