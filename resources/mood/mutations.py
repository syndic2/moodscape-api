import datetime, graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import validate_datetime, get_sequence
from ..utility_types import ResponseMessage
from .types import MoodInput, Mood

def get_activities_from_user(activity_ids, user_id):
    activities= mongo.db.user_activities.aggregate([
        {
            '$match': {
                'user_id': user_id,
                'activity_categories.activities._id': {
                    '$all': activity_ids
                }
            }
        },
        {
            '$project': {
                'activity_categories': {
                    '$filter': {
                        'input': {
                            '$map': {
                                'input': '$activity_categories',
                                'as': 'item1',
                                'in': {
                                    'activities': {
                                        '$filter': {
                                            'input': '$$item1.activities',
                                            'as': 'item2',
                                            'cond': {
                                                '$in': ['$$item2._id', activity_ids]
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        'as': 'item1',
                        'cond': {
                            '$ne': ['$$item1.activities', []]
                        }
                    }
                }
            }
        },
        {
            '$addFields': {
                'activities': {
                    '$reduce': {
                        'input': '$activity_categories.activities',
                        'initialValue': [],
                        'in': {
                            '$setUnion': ['$$value', '$$this']
                        }
                    }
                }
            }
        },
        {
            '$project': {
                'activities': 1
            }
        }
    ])
    activities= list(activities)[0]['activities']

    return activities

class CreateMood(graphene.Mutation):
    class Arguments:
        fields= MoodInput()

    created_mood= graphene.Field(Mood)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, fields):
        if validate_datetime(f"{fields.created_at.date} {fields.created_at.time}") is False:
            return CreateMood(
                created_mood= None,
                response= ResponseMessage(text= 'Format tanggal dan waktu tidak sesuai, mood gagal ditambahkan', status= False)
            )

        activities= []

        if len(fields.activities) > 0:
            is_activity_ids_exist= mongo.db.user_activities.find_one({ 
                'user_id': ObjectId(get_jwt_identity()),
                'activity_categories.activities._id': {
                    '$all': fields.activities
                } 
            })

            if is_activity_ids_exist is None:
                return CreateMood(
                    created_mood= None,
                    response= ResponseMessage(text= 'Aktivitas tidak ditemukan, mood gagal ditambahkan', status= False)
                )
            
            activities= get_activities_from_user(fields.activities, ObjectId(get_jwt_identity()))

        fields= {
            '_id': get_sequence('moods'),
            'emoticon': fields['emoticon'],
            'created_at': datetime.datetime.strptime(f"{fields.created_at.date} {fields.created_at.time}", '%Y-%m-%d %H:%M'),
            'parameters': fields['parameters'],
            'activities': activities,
            'note': fields['note']
        }

        result= mongo.db.moods.insert_one(dict(fields))

        if result.inserted_id is None:
            return CreateMood(
                created_mood= None,
                response= ResponseMessage(text= 'Tidak dapat menyimpan pada moods collection, mood gagal ditambahkan', status= False)
            )

        is_user_moods_exist= mongo.db.user_moods.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if is_user_moods_exist is None:
            create_user_moods= mongo.db.user_moods.insert_one({
                '_id': get_sequence('user_moods'),
                'user_id': ObjectId(get_jwt_identity()),
                'moods': [result.inserted_id]
            })

            if create_user_moods.inserted_id is None:
                return CreateMood(
                    created_mood= None,
                    response= ResponseMessage(text= 'Tidak dapat membuat user_moods baru, mood gagal ditambahkan', status= False)
                ) 
        else:
            insert_on_user_moods= mongo.db.user_moods.update_one(
                { 'user_id': ObjectId(get_jwt_identity()) },
                {
                    '$push': {
                        'moods': result.inserted_id
                    }
                }
            )

            if insert_on_user_moods.modified_count == 0:
                return CreateMood(
                    created_mood= None,
                    response= ResponseMessage(text= 'Tidak dapat menyimpan pada user_moods collection, mood gagal ditambahkan', status= False)
                ) 
        
        created_mood= mongo.db.moods.find_one({ '_id': result.inserted_id })
        created_mood['created_at']= {
            'date': created_mood['created_at'].date(),
            'time': str(created_mood['created_at'].time())[:-3]
        }

        return CreateMood(  
            created_mood= created_mood,
            response= ResponseMessage(text= 'Berhasil menambahkan mood baru', status= True)
        )

class UpdateMood(graphene.Mutation):
    class Arguments:
        _id= graphene.Int()
        fields= MoodInput()
    
    updated_mood= graphene.Field(Mood)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, _id, fields):
        if validate_datetime(f"{fields.created_at.date} {fields.created_at.time}") is False:
            return UpdateMood(
                updated_mood= None,
                response= ResponseMessage(text= 'Format tanggal dan waktu tidak sesuai, mood gagal diperbarui', status= False)
            ) 

        is_mood_id_exist_in_user_moods= mongo.db.user_moods.find_one({
            'user_id': ObjectId(get_jwt_identity()),
            'moods': _id
        })

        if is_mood_id_exist_in_user_moods is None:
            return UpdateMood(
                updated_mood= None,
                response= ResponseMessage(text= 'Mood tidak ditemukan pada user_moods collection, mood gagal diperbarui', status= False)
            )

        is_mood_id_exist_in_moods= mongo.db.moods.find_one({ '_id': _id })

        if is_mood_id_exist_in_moods is None:
            return UpdateMood(
                updated_mood= None,
                response= ResponseMessage(text= 'Mood tidak ditemukan pada moods collection, mood gagal diperbarui', status= False)
            )

        activities= []

        if len(fields.activities) > 0:
            is_activity_ids_exist= mongo.db.user_activities.find_one({ 
                'user_id': ObjectId(get_jwt_identity()),
                'activity_categories.activities._id': {
                    '$all': fields.activities
                } 
            })

            if is_activity_ids_exist is None:
                return UpdateMood(
                    updated_mood= None,
                    response= ResponseMessage(text= 'Aktivitas tidak ditemukan, mood gagal diperbarui', status= False)
                )

            activities= get_activities_from_user(fields.activities, ObjectId(get_jwt_identity()))

        fields= {
            'emoticon': fields['emoticon'],
            'created_at': datetime.datetime.strptime(f"{fields.created_at.date} {fields.created_at.time}", '%Y-%m-%d %H:%M'),
            'parameters': fields['parameters'],
            'activities': activities,
            'note': fields['note']
        }

        result= mongo.db.moods.find_one_and_update(
            { '_id': _id },
            { '$set': dict(fields) }
        )

        if result is None:
            return UpdateMood(
                updated_mood= None,
                response= ResponseMessage(text= 'Terjadi kendala pada server, mood gagal diperbarui', status= False)
            )

        updated_mood= mongo.db.moods.find_one({ '_id': _id })
        updated_mood['created_at']= {
            'date': result['created_at'].date(),
            'time': str(result['created_at'].time())[:-3]
        }

        return UpdateMood(
            updated_mood= updated_mood,
            response= ResponseMessage(text= 'Berhasil membarui mood', status= True)
        )

class RemoveMoods(graphene.Mutation):
    class Arguments:
        mood_ids= graphene.List(graphene.Int)
    
    removed_moods= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, mood_ids):
        is_mood_ids_exist= mongo.db.user_moods.find_one({
            'user_id': ObjectId(get_jwt_identity()),
            'moods': {
                '$all': mood_ids
            }
        })

        if is_mood_ids_exist is None:
            return RemoveMoods(
                removed_moods= [],
                response= ResponseMessage(text= 'Mood tidak ditemukan, mood gagal terhapus', status= False)
            )

        remove_from_moods= mongo.db.moods.delete_many({ '_id': { '$in': mood_ids } })

        if remove_from_moods.deleted_count == 0:
            return RemoveMoods(
                removed_moods= [],
                response= ResponseMessage(text= 'Gagal menghapus mood dari moods collection, mood gagal terhapus', status= False)
            )

        remove_from_user_moods= mongo.db.user_moods.update_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                '$pull': {
                    'moods': { '$in': mood_ids }
                }
            }
        )

        if remove_from_user_moods.modified_count == 0:
            return RemoveMoods(
                removed_moods= [],
                response= ResponseMessage(text= 'Gagal menghapus mood dari user_moods collection, mood gagal terhapus', status= False)
            )

        return RemoveMoods(
            removed_moods= mood_ids,
            response= ResponseMessage(text= 'Berhasil menghapus mood', status= True)
        )

class MoodMutation(graphene.AbstractType):
    create_mood= CreateMood.Field()
    update_mood= UpdateMood.Field()
    remove_moods= RemoveMoods.Field()