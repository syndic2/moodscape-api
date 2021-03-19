from flask import Flask, jsonify
from flask_cors import CORS
from flask_graphql import GraphQLView

from schema import schema
from extensions import mongo

app= Flask(__name__)

app.config['MONGO_URI']= 'mongodb://localhost:27017/moodscape'
mongo.init_app(app)

CORS(app)

@app.route('/')
def index():
    return jsonify(message='Online!')

app.add_url_rule('/api/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema, 
    graphiql=True
))

if __name__ == '__main__':
    app.run(debug=True)