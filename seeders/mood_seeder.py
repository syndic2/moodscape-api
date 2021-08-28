import enum, datetime, graphene
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import datetime_format
from resources.utility_types import ResponseMessage

class MOOD_EMOTICON_COLORS(enum.Enum):
    GEMBIRA= '#3CB403'
    SENANG= '#B4CC4E'
    NETRAL= '#FFD300'
    SEDIH= '#FFC30B'
    BURUK= '#D0312D'

moods= [
    {
        '_id': 1,
        'emoticon': {
            'name': 'gembira',
            'value': 5,
            'iconPath': 'icons/svg/emoticons/happy.svg',
            'color':  str(MOOD_EMOTICON_COLORS.GEMBIRA.value)
        },
        'created_at': datetime.datetime.strptime('2021-08-16 1:37', datetime_format('datetime')),
        'parameters': {
            'internal': 'dummy internal parameter text1',
            'external': 'dummy external parameter text1'
        },
        'activities': [
            { '_id': 1, 'name': 'pesta', 'icon': 'person-dancing' },
            { '_id': 2, 'name': 'makan', 'icon': 'eating' }
        ],
        'note': 'dummy note text1'
    },
    {
        '_id': 2,
        'emoticon': {
            'name': 'senang',
            'value': 4,
            'iconPath': 'icons/svg/emoticons/smile.svg',
            'color':  str(MOOD_EMOTICON_COLORS.SENANG.value)
        },
        'created_at': datetime.datetime.strptime('2021-08-16 1:37', datetime_format('datetime')),
        'parameters': {
            'internal': 'dummy internal parameter text2',
            'external': 'dummy external parameter text2'
        },
        'activities': [
            { '_id': 1, 'name': 'pesta', 'icon': 'person-dancing' },
            { '_id': 2, 'name': 'makan', 'icon': 'eating' }
        ],
        'note': 'dummy note text2'
    },
    {
        '_id': 3,
        'emoticon': {
            'name': 'netral',
            'value': 3,
            'iconPath': 'icons/svg/emoticons/neutral.svg',
            'color':  str(MOOD_EMOTICON_COLORS.NETRAL.value)
        },
        'created_at': datetime.datetime.strptime('2021-08-15 1:37', datetime_format('datetime')),
        'parameters': {
            'internal': 'dummy internal parameter text3',
            'external': 'dummy external parameter text3'
        },
        'activities': [
            { '_id': 3, 'name': 'tidur nyenyak', 'icon': 'good-sleep' },
            { '_id': 4, 'name': 'tidur sedang', 'icon': 'medium-sleep' },
        ],
        'note': 'dummy note text3'
    },
];

class UserMoodsSeeds(graphene.Mutation):
    response= graphene.Field(ResponseMessage)

    def mutate(self, info):
        mongo.db.sequences.delete_one({ '_id': 'moods' })
        mongo.db.sequences.delete_one({ '_id': 'user_moods' })
        mongo.db.moods.delete_many({})
        mongo.db.user_moods.delete_many({})

        seeds= mongo.db.moods.insert_many(moods)

        if not seeds.inserted_ids:
            return UserMoodsSeeds(response= ResponseMessage(text= 'Seeding moods collection failed...', status= False))            

        mongo.db.sequences.insert_many([
            { '_id': 'moods', 'value': len(moods) },
            { '_id': 'user_moods', 'value': 1 }
        ])

        mongo.db.user_moods.insert_many([
            {
                '_id': 1,
                'user_id': ObjectId('60acfde1ea67a0786c51fc0c'),
                'moods': [1, 2, 3]
            }
        ])

        return UserMoodsSeeds(response= ResponseMessage(text= 'Seeding moods collection succeed...', status= True))

class MoodSeeder(graphene.AbstractType):
    user_moods_seeds= UserMoodsSeeds.Field()