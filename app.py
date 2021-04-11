from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_graphql_auth import GraphQLAuth

import requests
import urllib
import json

from schemas import main_schema, auth_schema
from extensions import mongo

app= Flask(__name__)

app.config['JWT_SECRET_KEY']= 'access-token'
app.config['JWT_ACCESS_TOKEN_EXPIRES']= 1
app.config['JWT_REFRESH_TOKEN_EXPIRES']= 30
app.config['MONGO_URI']= 'mongodb://localhost:27017/moodscape'

auth = GraphQLAuth(app)
db= mongo.init_app(app)
cors= CORS(app)

@app.route('/')
def index():
    return jsonify(message= 'Online!')

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

if __name__ == '__main__':
    app.run(debug= True)