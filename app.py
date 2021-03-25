from flask import Flask, jsonify
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_graphql_auth import GraphQLAuth

import requests
import json

from schema import schema
from extensions import mongo

app= Flask(__name__)

app.config['JWT_SECRET_KEY']= 'access-token'
app.config['REFRESH_EXP_LENGTH']= 30
#app.config['ACCESS_EXP_LENGTH']= 100
app.config['MONGO_URI']= 'mongodb://localhost:27017/moodscape'

auth = GraphQLAuth(app)
db= mongo.init_app(app)
cors= CORS(app)

@app.route('/')
def index():
    return jsonify(message='Online!')

@app.route('/scrape-books')
def scrape_books():
    response= requests.get('http://localhost:9080/crawl.json', { 'spider_name': 'books', 'start_requests': True })
    data= json.loads(response.text)

    return jsonify(books= data['items'])

app.add_url_rule('/api/graphql', view_func= GraphQLView.as_view(
    'graphql',
    schema=schema, 
    graphiql=True
))

if __name__ == '__main__':
    app.run(debug=True)