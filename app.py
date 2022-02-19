from flask import Flask, jsonify, render_template, send_file
from flask_graphql import GraphQLView
from graphene_file_upload.flask import FileUploadGraphQLView

import datetime

from config import config
from seeds import seed_cli
from extensions import cors, auth, bcrypt, mail, mongo, scheduler
from resources.schema import main_schema, auth_schema
from services.brief_cope_evaluation import brief_cope_evaluation_api
from services.mental_disorders import mental_disorder_api
from services.telegram import telegram_service_api
from services.firebase_cloud_messaging import fcm_service_api, send_notification

app= Flask(__name__)

app.config.from_object(config)
app.cli.add_command(seed_cli)

cors.init_app(app)
auth.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)
mongo.init_app(app)
scheduler.init_app(app)
scheduler.start()

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

app.register_blueprint(brief_cope_evaluation_api, url_prefix= '/api/brief-cope-evaluation')
app.register_blueprint(mental_disorder_api, url_prefix= '/api/mental-disorders')
app.register_blueprint(telegram_service_api, url_prefix= '/services/telegram')
app.register_blueprint(fcm_service_api, url_prefix= '/services/fcm')

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

#this must be refactor with proper filter query in the future
@scheduler.task(trigger= 'interval', id= 'habits_reminder', seconds= 1)
def habits_reminder():
    current_datetime= datetime.datetime.now()
    current_date= current_datetime.date()
    current_time= str(current_datetime.time())[:5]

    habits= list(mongo.db.habits.find())
    habits_tracks_to_remind= []

    #filter habit for reminder
    for habit in habits:
        if ((current_date >= habit['goal_dates']['start'].date() and current_date <= habit['goal_dates']['end'].date()) and 
            (habit['reminder_time'] != '' and 'is_reminder' in habit and habit['is_reminder'] == True)):
            reminder_time= str(habit['reminder_time'].time())[:5]

            if reminder_time == current_time:
                habits_tracks_to_remind.append(habit['_id'])
            else:
                mongo.db.habits.find_one_and_update({ '_id': habit['_id'] }, { '$set': { 'is_notified': False } })
        else:
            mongo.db.habits.find_one_and_update({ '_id': habit['_id'] }, { '$set': { 'is_notified': False } })
    
    #print('habit tracks to remind', habits_tracks_to_remind)

    habits_tracks= list(mongo.db.habit_tracks.find({ 'habit_id': { '$in': habits_tracks_to_remind } }))
    habit_ids_to_remind= []
    habits_to_remind= []

    #filter habit tracks for reminder    
    for habit_track in habits_tracks:
        for streak_log in habit_track['streak_logs']:
            if (current_date >= streak_log['start_date'].date() and current_date <= streak_log['end_date'].date()) and streak_log['is_complete'] == False:
                habit_ids_to_remind.append(habit_track['habit_id'])

    #print('habits to remind', habit_ids_to_remind)

    #get reminder habit
    for habit in habits:
        for habit_id in habit_ids_to_remind:
            if habit['_id'] == habit_id:
                habits_to_remind.append(habit)

    user_habits= list(mongo.db.user_habits.find({ 'habits': { '$in': [habit['_id'] for habit in habits_to_remind] } }))
    users_to_remind= []

    #map user id from user habits
    for user_habit in user_habits:
        users_to_remind.append(user_habit['user_id'])

    fcm_tokens= list(mongo.db.fcm_tokens.find({ 'user_id': { '$in': users_to_remind } }))
    tokens_to_remind= []

    #filter fcm token (device)
    for fcm_token in fcm_tokens:
        tokens_to_remind.append({
            'token': fcm_token['token'],
            'user_id': fcm_token['user_id'],
            'habits': []
        })
    
    #get reminder habit
    for user_habit in user_habits:
        for habit_id in user_habit['habits']:
            for habit in habits_to_remind:
                if habit_id == habit['_id']:
                    for i in range(len(tokens_to_remind)):
                        if user_habit['user_id'] == tokens_to_remind[i]['user_id']:
                            tokens_to_remind[i]['habits'].append(habit)

    #print('current time and second', current_time, current_second)

    #send notifications
    for token_to_remind in tokens_to_remind:
        for habit in token_to_remind['habits']:
            if 'is_notified' in habit and habit['is_notified'] == False:
                print('token', token_to_remind['token'])
                reminder_time= str(habit['reminder_time'].time())[:5]
                send_notification(
                    token_to_remind['token'], 
                    { 
                        'title': habit['name'], 
                        'body': f'{reminder_time} - Jangan lupa untuk tracking',
                    }
                )
                mongo.db.habits.find_one_and_update({ '_id': habit['_id'] }, { '$set': { 'is_notified': True } })

if __name__ == '__main__':
    app.run(debug= True)