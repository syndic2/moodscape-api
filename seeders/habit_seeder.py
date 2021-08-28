import enum, datetime, graphene
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import datetime_format
from resources.utility_types import ResponseMessage

class HABIT_LABEL_COLORS(enum.Enum):
    RED= '#FF0000'
    PINK= '#FFC0CB'
    ORANGE= '#FF8C00'
    BLUE= '#0000FF'
    GREEN= '#358873'

habits= [
    {
        '_id': 1,
        'name': 'dummy name1',
        'description': 'dummy description1',
        'created_at': datetime.datetime.strptime('2021-08-21 2:13', datetime_format('datetime')),
        'type': 'to do',
        'day': 'all day',
        'goal': 30,
        'goal_dates': {
            'start': datetime.datetime.strptime('2021-08-21', datetime_format('date')),
            'end': datetime.datetime.strptime('2021-09-21', datetime_format('date'))
        },
        'reminder_time': datetime.datetime.strptime('8:00', datetime_format('time')),
        'label_color': str(HABIT_LABEL_COLORS.ORANGE.value)
    },
    {
        '_id': 2,
        'name': 'dummy name2',
        'description': 'dummy description2',
        'created_at': datetime.datetime.strptime('2021-08-20 2:13', datetime_format('datetime')),
        'type': 'to do',
        'day': 'friday',
        'goal': 20,
        'goal_dates': {
            'start': datetime.datetime.strptime('2021-08-20', datetime_format('date')),
            'end': datetime.datetime.strptime('2021-09-10', datetime_format('date'))
        },
        'reminder_time': datetime.datetime.strptime('9:00', datetime_format('time')),
        'label_color': str(HABIT_LABEL_COLORS.BLUE.value)
    },
        {
        '_id': 3,
        'name': 'dummy name3',
        'description': 'dummy description3',
        'created_at': datetime.datetime.strptime('2021-08-19 2:13', datetime_format('datetime')),
        'type': 'not to do',
        'day': 'thursday',
        'goal': 10,
        'goal_dates': {
            'start': datetime.datetime.strptime('2021-08-19', datetime_format('date')),
            'end': datetime.datetime.strptime('2021-08-29', datetime_format('date'))
        },
        'reminder_time': datetime.datetime.strptime('10:00', datetime_format('time')),
        'label_color': str(HABIT_LABEL_COLORS.RED.value)
    }
]

class UserHabitSeeds(graphene.Mutation):
    response= graphene.Field(ResponseMessage)

    def mutate(self, info):
        mongo.db.sequences.delete_one({ '_id': 'habits' })
        mongo.db.sequences.delete_one({ '_id': 'user_habits' })
        mongo.db.habits.delete_many({})
        mongo.db.user_habits.delete_many({})

        seeds= mongo.db.habits.insert_many(habits)

        if not seeds.inserted_ids:
            return UserHabitSeeds(response= ResponseMessage(text= 'Seeding habits collection failed...', status= False))
        
        mongo.db.sequences.insert_many([
            { '_id': 'habits', 'value': len(habits) },
            { '_id': 'user_habits', 'value': 1 }
        ])

        mongo.db.user_habits.insert_many([
            {
                '_id': 1,
                'user_id': ObjectId('60acfde1ea67a0786c51fc0c'),
                'habits': [1, 2, 3]
            }
        ])

        return UserHabitSeeds(response= ResponseMessage(text= 'Seeding habits collection succeed...', status= True))

class HabitSeeder(graphene.AbstractType):
    user_habits_seeder= UserHabitSeeds.Field()