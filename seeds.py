from flask.cli import AppGroup
from flask_bcrypt import generate_password_hash
from faker import Faker

from datetime import datetime
from itertools import count
import random, json

from extensions import bcrypt, mongo
from utilities.helpers import default_img, datetime_format

seed_cli= AppGroup('seed_run')
fake= Faker()
seed_length= 15 #default seed data

# ** old seeder code (probably not gonna use it anymore) **

#seeder
def user_seeder():
    mongo.db.sequences.delete_one({ '_id': 'users' })
    mongo.db.sequences.delete_one({ '_id': 'user_articles' })
    mongo.db.users.delete_many({})        

    seeds= []

    try:
        for number in range(seed_length):
            if number == 0:
                seeds.append({
                    'first_name': 'Jonathan',
                    'last_name': 'Sugianto',
                    'gender': 'M',
                    'date_of_birth': datetime(1999, 11, 1),
                    'email': 'jonathangani279@gmail.com',
                    'username': 'syndic',
                    'password': bcrypt.generate_password_hash('kusogaki'),
                    'img_url': default_img,
                    'joined_at': datetime.now(),
                    'is_admin': False,
                    'is_active': True
                })
            else:
                seeds.append({
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'gender': random.choice(['M', 'F']),
                    'date_of_birth': fake.date_time_between_dates(datetime(1980, 1, 1, 0, 0, 0, 0), datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)),
                    'email': fake.email(),
                    'username': fake.profile()['username'],
                    'password': bcrypt.generate_password_hash('seeding-password'),
                    'img_url': default_img,
                    'joined_at': fake.date_time_between_dates(datetime(2017, 1, 1), datetime.now()),
                    'is_admin': False,
                    'is_active': fake.boolean() 
                })
        
        result= mongo.db.users.insert_many(seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding users collection failed...')
            return 
        
        sequence_seed= mongo.db.sequences.insert_one({ '_id': 'users', 'value': seed_length })
        if sequence_seed.inserted_id is None:
            print('Seeding users sequences collection failed...')
            return

        print('Seeding users collection succeed...')
    except Exception as ex:
        print('Seeding users collection failed...')
        print('error: ', ex)

def mood_seeder():
    mongo.db.sequences.delete_one({ '_id': 'moods' })
    mongo.db.sequences.delete_one({ '_id': 'user_moods' })
    mongo.db.moods.delete_many({})
    mongo.db.user_moods.delete_many({})

    emoticons= [
        {
            'name': 'gembira',
            'value': 5,
            'iconPath': 'icons/svg/emoticons/happy.svg',
            'color': '#3CB403'
        },
        {
            'name': 'senang',
            'value': 4,
            'iconPath': 'icons/svg/emoticons/smile.svg',
            'color':  '#B4CC4E'
        },
        {
            'name': 'netral',
            'value': 3,
            'iconPath': 'icons/svg/emoticons/neutral.svg',
            'color': '#FFC30B'
        },
        {
            'name': 'netral',
            'value': 3,
            'iconPath': 'icons/svg/emoticons/neutral.svg',
            'color': '#FFD300'
        },
        {
            'name': 'sedih',
            'value': 2,
            'iconPath': 'icons/svg/emoticons/sad.svg',
            'color': '#FFC30B'
        },
        {
            'name': 'buruk',
            'value': 1,
            'iconPath': 'icons/svg/emoticons/awful.svg',
            'color': '#D0312D'
        },
    ]
    mood_seeds= []
    user_mood_seeds= []

    try:
        for number in range(seed_length*seed_length):
            mood_seeds.append({ 
                '_id': number+1,
                'emoticon': random.choice(emoticons),
                'created_at': fake.date_time_between_dates(datetime(2017, 1, 1), datetime.now()),
                'parameters': {
                    'internal': fake.sentence(),
                    'external': fake.sentence()
                },
                'activities': [
                    { '_id': 1, 'name': 'pesta', 'icon': 'person-dancing' },
                    { '_id': 2, 'name': 'makan', 'icon': 'eating' }
                ],
                'note': fake.sentence()
            })
        
        result= mongo.db.moods.insert_many(mood_seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding moods collection failed...')
            return
        
        sequence_seed= mongo.db.sequences.insert_one({ '_id': 'moods', 'value': seed_length*seed_length })
        if sequence_seed.inserted_id is None:
            print('Seeding moods sequences collection failed...')
            return

        mood_id_gap= 1
        user_ids= [user['_id'] for user in mongo.db.users.find({})]

        for number in range(seed_length):
            user_mood_seeds.append({
                '_id': number+1,
                'user_id': random.choice(user_ids),
                'moods': list(range(mood_id_gap, mood_id_gap+seed_length))
            })
            mood_id_gap+= 15
        
        result= mongo.db.user_moods.insert_many(user_mood_seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding user_moods collection failed...')
            return

        sequence_seed= mongo.db.sequences.insert_one({ '_id': 'user_moods', 'value': seed_length })
        if sequence_seed.inserted_id is None:
            print('Seeding user_moods sequences collection failed...')
            return
        
        print('Seeding moods collection succeed...')
        print('Seeding user_moods collection succeed...')
    except Exception as ex:
        print('Seeding moods collection failed...')
        print('Seeding user_moods collection failed...')
        print('error: ', ex)

def habit_seeder():
    mongo.db.sequences.delete_one({ '_id': 'habits' })
    mongo.db.sequences.delete_one({ '_id': 'habit_tracks' })
    mongo.db.sequences.delete_one({ '_id': 'user_habits' })
    mongo.db.habits.delete_many({})
    mongo.db.habit_tracks.delete_many({})
    mongo.db.user_habits.delete_many({})

    habit_seeds= []
    user_habit_seeds= []

    try:
        for number in range(seed_length*seed_length):
           habit_seeds.append({
                '_id': number+1,
                'name': fake.text(),
                'description': fake.sentence(),
                'created_at': fake.date_time(),
                'type': random.choice(['to do', 'not to do']),
                'day': random.choice(['all day', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']),
                'goal': random.randrange(1, 30),
                'goal_dates': {
                    'start': fake.date_time_between_dates(datetime(2017, 1, 1), datetime.now()),
                    'end': fake.date_time_between_dates(datetime(2017, 1, 1), datetime.now())
                },
                'reminder_time': random.choice(['', fake.time('%H:%M')]),
                'label_color': random.choice(['#FF0000', '#FFC0CB', '#FF8C00', '#0000FF', '#358873'])
            })

        result= mongo.db.habits.insert_many(habit_seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding habits collection failed...')
            return

        sequence_seed= mongo.db.sequences.insert_one({ '_id': 'habits', 'value': seed_length*seed_length })
        if sequence_seed.inserted_id is None:
            print('Seeding habits sequences collection failed...')
            return

        habit_id_gap= 1
        user_ids= [user['_id'] for user in mongo.db.users.find({})]

        for number in range(seed_length):
            user_habit_seeds.append({
                '_id': number+1,
                'user_id': random.choice(user_ids),
                'habits': list(range(habit_id_gap, habit_id_gap+seed_length))
            })
            habit_id_gap+= 15

        result= mongo.db.user_habits.insert_many(user_habit_seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding user_habits collection failed...')
            return

        sequence_seed= mongo.db.sequences.insert_one({ '_id': 'user_habits', 'value': seed_length })
        if sequence_seed.inserted_id is None:
            print('Seeding user_habits sequences collection failed...')
            return

        print('Seeding habits collection succeed...')
        print('Seeding user_habits collection succeed...')
    except Exception as ex:
        print('Seeding habits collection failed...')
        print('Seeding user_habits collection failed...')
        print('error: ', ex)

def activity_seeder():
    mongo.db.sequences.delete_one({ '_id': 'activity_icons' })
    mongo.db.sequences.delete_one({ '_id': 'user_activities' })
    mongo.db.sequences.delete_one({ '_id': 'array_sequences' })
    mongo.db.array_sequences.delete_many({ 'collection': 'user_activities', 'array_documents': 'activity_categories' })
    mongo.db.array_sequences.delete_many({ 'collection': 'user_activities', 'array_documents': 'activities' })
    mongo.db.activity_icons.delete_many({})
    mongo.db.user_activities.delete_many({})
    
    activity_icon_seeds= []
    user_activity_seeds= []

    try:
        for number in range(seed_length):
            activity_icon_seeds.append({
                '_id': number+1,
                'name': fake.word()
            })

        result= mongo.db.activity_icons.insert_many(activity_icon_seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding activity_icons collection failed...')
            return
    	
        user_ids= [user['_id'] for user in mongo.db.users.find({})]
        icon_names= [icon['name'] for icon in mongo.db.activity_icons.find({})]

        for user_activity_id in range(seed_length):
            activity_id_gap_counter= count()
            user_activity_seeds.append({
                '_id': user_activity_id+1,
                'user_id': random.choice(user_ids),
                'activity_categories': [
                    {
                        '_id': activity_category_id+1,
                        'category': fake.word(),
                        'activities': [
                            { 
                                '_id':  next(activity_id_gap_counter)+1, 
                                'name': fake.word(), 
                                'icon': random.choice(icon_names)
                            }
                            
                            for _ in range(seed_length)
                        ]
                    }
                    
                    for activity_category_id in range(seed_length)
                ]
            })

        result= mongo.db.user_activities.insert_many(user_activity_seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding user_activities collection failed...')
            return

        activity_categories_array_sequence_seeds= []
        activity_array_sequence_seeds= []

        for number in range(seed_length):
            activity_categories_array_sequence_seeds.append({
                '_id': number+1,
                'collection': 'user_activities',
                'document_id': random.choice(user_ids),
                'array_documents': 'activity_categories',
                'value': seed_length
            })
    
        array_sequence_seed= mongo.db.array_sequences.insert_many(activity_categories_array_sequence_seeds)
        if len(array_sequence_seed.inserted_ids) == 0:
            print('Seeding activity_categories array_sequences collection failed...')
            return

        activity_categories_document_ids= [field['document_id'] for field in mongo.db.array_sequences.find({ 'collection': 'user_activities', 'array_documents': 'activity_categories' })]

        for number in range(seed_length+1, seed_length+seed_length):
            activity_array_sequence_seeds.append({
                '_id': number+1,
                'collection': 'user_activities',
                'document_id': activity_categories_document_ids[number-seed_length],
                'array_documents': 'activities',
                'value': seed_length
            })
        
        array_sequence_seed= mongo.db.array_sequences.insert_many(activity_array_sequence_seeds)
        if len(array_sequence_seed.inserted_ids) == 0:
            print('Seeding activities array_sequences collection failed...')
            return
        
        print('Seeding activity_icons collection succeed...')
        print('Seeding user_activities collection succeed...')
    except Exception as ex:
        print('Seeding activity_icons collection failed...')
        print('Seeding user_activities collection failed...')
        print('error: ', ex)

def activity_icons_seeder():
    mongo.db.sequences.delete_one({ '_id': 'activity_icons' })

    try:
        activity_icon_seeds= []
        
        for number in range(seed_length):
            activity_icon_seeds.append({
                '_id': number+1,
                'name': fake.word()
            })

        result= mongo.db.activity_icons.insert_many(activity_icon_seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding activity_icons collection failed...')
            return
        
        print('Seeding activity_icons collection succeed...')
    except Exception as ex:
        print('Seeding activity_icons collection failed...')

def app_feedback_seeder():
    mongo.db.app_feedbacks.delete_many({})

    try:
        app_feedback_seeds= []
        user_ids= [user['_id'] for user in mongo.db.users.find({})]

        for _ in range(seed_length):
            app_feedback_seeds.append({
                'user_id': random.choice(user_ids),
                'rating': random.randrange(1, 5),
                'review': fake.paragraph(),
                'feature_category': random.choice(['Mood Tracker', 'Habit Tracker', 'Statistics', 'Chatbot', 'Article']),
                'created_at': fake.date_time_between_dates(datetime(2017, 1, 1), datetime.now())
            })

        result= mongo.db.app_feedbacks.insert_many(app_feedback_seeds)
        if len(result.inserted_ids) == 0:
            print('Seeding app_feedbacks collection failed...')
            return
        
        print('Seeding app_feedbacks collection succced...')
    except Exception as ex:
        print('Seeding app_feedbacks sequences collection failed...')
        print('error: ', ex)

#commands
@seed_cli.command('user_seeder')
def run_user_seeder():
    user_seeder()

@seed_cli.command('mood_seeder')
def run_mood_seeder():
    mood_seeder()

@seed_cli.command('habit_seeder')
def run_habit_seeder():
    habit_seeder()

@seed_cli.command('activity_seeder')
def run_activity_seeder():
    activity_seeder()

@seed_cli.command('activity_icons_seeder')
def run_activity_icons_seeder():
    activity_icons_seeder()

@seed_cli.command('app_feedback_seeder')
def run_app_feedback_seeder():
    app_feedback_seeder()

#run all commands
@seed_cli.command('all_seeder')
def run_all_seeder():
    user_seeder()
    mood_seeder()
    habit_seeder()
    activity_seeder()
    app_feedback_seeder()

# **new seeder code below here**

#seeds admin user
@seed_cli.command('admin_user_seeder')
def run_admin_user_seeder():
    mongo.db.users.delete_many({ 'is_admin': True })
    
    try:
        users= [
            {
                'first_name': 'Jonathan',
                'last_name': 'Admin',
                'email': 'jonathanadmin@gmail.com',
                'username': 'admin2',
                'password': generate_password_hash('kusogaki'), 
                'joined_at': datetime.now(),
                'is_admin': False,
                'is_active': True
            }
        ]

        result= mongo.db.users.insert_many(users)

        if len(result.inserted_ids) == 0:
            print('Seeding users(admin) collection failed...')
            return  

        print('Seeding users(admin) collection succced...')
    except Exception as ex:
        print('Seeding users(admin) collection failed...')
        print('error', ex)

#seeds brief_cope_results
@seed_cli.command('brief_cope_result_seeder')
def run_brief_cope_result_seeder():
    mongo.db.brief_cope_results.delete_many({})

    brief_cope_results= [
        {
            'user_id': '1',
            'coping_strategy': 'Problem-focused',
            'problem_focused': {
                'average': 2.75,
                'categories': {
                    'active_coping': 3,
                    'use_of_informational_support': 2,
                    'positive_reframing': 3,
                    'planning': 3
                }
            },
            'emotion_focused': {
                'average': 2.58,
                'coping_strategy': 'Problem-focused',
                'categories': {
                    'emotional_support': 3,
                    'venting': 2,
                    'humour': 1.5,
                    'acceptance': 3,
                    'self_blame': 3,
                    'religion': 3
                }
            },
            'avoidant': {
                'average': 2.5,
                'coping_strategy': 'Problem-focused',
                'categories': {
                    'self_distraction': 3,
                    'substance_use': 1.5, 
                    'denial': 2,
                    'behavioural_disengagement': 3.5
                }
            },
            'created_at': datetime.strptime('2021-12-1', datetime_format('date'))
        },
        {
            'user_id': '1',
            'coping_strategy': 'Problem-focused',
            'problem_focused': {
                'average': 2.75,
                'categories': {
                    'active_coping': 3,
                    'use_of_informational_support': 2,
                    'positive_reframing': 3,
                    'planning': 3
                }
            },
            'emotion_focused': {
                'average': 2.58,
                'categories': {
                    'emotional_support': 3,
                    'venting': 2,
                    'humour': 1.5,
                    'acceptance': 3,
                    'self_blame': 3,
                    'religion': 3
                }
            },
            'avoidant': {
                'average': 2.5,
                'categories': {
                    'self_distraction': 3,
                    'substance_use': 1.5, 
                    'denial': 2,
                    'behavioural_disengagement': 3.5
                }
            },
            'created_at': datetime.strptime('2021-12-10', datetime_format('date'))
        },
        {
            'user_id': '1',
            'coping_strategy': 'Problem-focused',
            'problem_focused': {
                'average': 2.75,
                'categories': {
                    'active_coping': 3,
                    'use_of_informational_support': 2,
                    'positive_reframing': 3,
                    'planning': 3
                }
            },
            'emotion_focused': {
                'average': 2.58,
                'categories': {
                    'emotional_support': 3,
                    'venting': 2,
                    'humour': 1.5,
                    'acceptance': 3,
                    'self_blame': 3,
                    'religion': 3
                }
            },
            'avoidant': {
                'average': 2.5,
                'categories': {
                    'self_distraction': 3,
                    'substance_use': 1.5, 
                    'denial': 2,
                    'behavioural_disengagement': 3.5
                }
            },
            'created_at': datetime.strptime('2022-1-1', datetime_format('date'))
        },
        {
            'user_id': '1',
            'coping_strategy': 'Problem-focused',
            'problem_focused': {
                'average': 2.75,
                'categories': {
                    'active_coping': 3,
                    'use_of_informational_support': 2,
                    'positive_reframing': 3,
                    'planning': 3
                }
            },
            'emotion_focused': {
                'average': 2.58,
                'categories': {
                    'emotional_support': 3,
                    'venting': 2,
                    'humour': 1.5,
                    'acceptance': 3,
                    'self_blame': 3,
                    'religion': 3
                }
            },
            'avoidant': {
                'average': 2.5,
                'categories': {
                    'self_distraction': 3,
                    'substance_use': 1.5, 
                    'denial': 2,
                    'behavioural_disengagement': 3.5
                }
            },
            'created_at': datetime.strptime('2022-2-17', datetime_format('date'))
        }
    ]

    try:
        result= mongo.db.brief_cope_results.insert_many(brief_cope_results)

        if len(result.inserted_ids) == 0:
            print('Seeding brief_cope_results collection failed...')
            return
        
        print('Seeding brief_cope_results collection succeed...')
    except Exception as ex:
        print('Seeding brief_cope_results collection failed...')
        print('error', ex)

#seeds mental_disorder
@seed_cli.command('mental_disorder_seeder')
def run_mental_disorder_seeder():
    mongo.db.mental_disorders.delete_many({})

    try:
        f= open('./seed_data/mental_disorders.json')
        mental_disorders= json.load(f)
        result= mongo.db.mental_disorders.insert_many(mental_disorders)

        if len(result.inserted_ids) == 0:
            print('Seeding mental_disorders collection failed...')
            return
        
        print('Seeding mental_disorders collection succeed...')
    except Exception as ex:
        print('Seeding mental_disorders collection failed...')
        print('error', ex)

#seeds theme
@seed_cli.command('theme_seeder')
def run_theme_seeder():
    mongo.db.themes.delete_many({})

    themes= [
        {
            'name': 'Comfort Light Green',
            'colors': {
                'primary': '#aed9b2',
                'primary_rgb': '174, 217, 178',
                'primary_contrast': '#ffffff',
                'primary_contrast_rgb': '255, 255, 255',
                'primary_shade': '#99bf9d',
                'primary_tint': '#b6ddba'
            },
            'is_active': True
        },
        {
            'name': 'Pink Dogwood',
            'colors': {
                'primary': '#f7d1d1',
                'primary_rgb': '247, 209, 209',
                'primary_contrast': '#ffffff',
                'primary_contrast_rgb': '255, 255, 255',
                'primary_shade': '#d9b8b8',
                'primary_tint': '#f8d6d6'
            },
            'is_active': True
        },
        {
            'name': 'Bright Pastel Orange',
            'colors': {
                'primary': '#ffb650',
                'primary_rgb': '255, 182, 80',
                'primary_contrast': '#ffffff',
                'primary_contrast_rgb': '2555, 255, 255',
                'primary_shade': '#e0a046',
                'primary_tint': '#ffbd62'
            },
            'is_active': True
        },
        {
            'name': 'Red Shimmer',
            'colors': {
                'primary': '#f5595c',
                'primary_rgb': '245, 89, 92',
                'primary_contrast': '#ffffff',
                'primary_contrast_rgb': '255, 255, 255',
                'primary_shade': '#d84e51',
                'primary_tint': '#f66a6c'
            },
            'is_active': True
        },
        {
            'name': 'Purple Rose',
            'colors': {
                'primary': '#b09fca',
                'primary_rgb': '176, 159, 202',
                'primary_contrast': '#ffffff',
                'primary_contrast_rgb': '255, 255, 2555',
                'primary_shade': '#9b8cb2',
                'primary_tint': '#b8a9cf'
            },
            'is_active': True
        },
    ]

    try:

        result= mongo.db.themes.insert_many(themes)

        if len(result.inserted_ids) == 0:
            print('Seeding themes collection failed...')
            return

        print('Seeding themes collection succeed...')
    except Exception as ex:
        print('Seeding themes collection failed...')
        print('error', ex)

#clear seeds
@seed_cli.command('clear_seeds')
def run_clear_seeds():
    collections= [
        'users', 'user_moods', 'user_activities', 'user_habits', 'user_articles',
        'moods', 'activity_icons', 'habits', 'habit_tracks', 'themes', 'app_feedbacks', 'reset_passwords', 'array_sequences'
    ]
    sequences= ['users', 'user_moods', 'user_habits', 'moods', 'habits']

    try:
        for collection in collections:
            if collection in mongo.db.list_collection_names():
                mongo.db[collection].drop()

        if len(list(mongo.db.sequences.find({ '_id': { '$in': sequences } }))) > 0:
            result= mongo.db.sequences.delete_many({ '_id': { '$in': sequences } })

            if result.deleted_count == 0:
                print(f'Clear sequence collections: {sequences} failed')
                return
        
        print(f'Clear collections: {collections} succeed...')
        print(f'Clear sequence collections: {sequences} succeed...')
    except Exception as ex:
        print(f'Clear collections: {collections} failed...')
        print(f'Clear sequence collections: {sequences} failed...')
        print('error', ex)


