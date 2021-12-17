from flask import Flask, jsonify, render_template, send_file
from flask_graphql import GraphQLView
from graphene_file_upload.flask import FileUploadGraphQLView

from config import config
from seeds import seed_cli
from extensions import cors, auth, bcrypt, mail, mongo
from resources.schema import main_schema, auth_schema
from services.mental_disorders import mental_disorder_api
from services.telegram import telegram_api

app= Flask(__name__)

app.config.from_object(config)
app.cli.add_command(seed_cli)

cors.init_app(app)
auth.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)
mongo.init_app(app)

app.add_url_rule('/api/graphql', view_func= FileUploadGraphQLView.as_view(
    'graphql',
    schema= main_schema, 
    graphiql= True
))

app.add_url_rule('/api/auth', view_func= GraphQLView.as_view(
    'auth',
    schema= auth_schema, 
    graphiql= True
))

app.register_blueprint(mental_disorder_api, url_prefix= '/api/mental-disorders')
app.register_blueprint(telegram_api, url_prefix= '/telegram')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_handlers/page-not-found.html'), 404

@app.route('/')
def index():
    return jsonify(message= 'Server is online!', status= 'OK')

@app.route('/uploads/images/<file_name>')
def display_uploaded_image(file_name):
    return send_file(f"{app.config['UPLOAD_FOLDER']}/images/{file_name}", mimetype= 'image/gif')

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