import datetime, graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from utilities.helpers import get_sequence
from extensions import mongo
from .types import AppFeedbackInput, AppFeedback
from ..utility_types import ResponseMessage

class CreateAppFeedback(graphene.Mutation):
    class Arguments:
        fields= AppFeedbackInput()
    
    created_feedback= graphene.Field(AppFeedback)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, root, fields):
        if fields['rating'] > 5:
            return CreateAppFeedback(
                created_feedback= None,
                response= ResponseMessage(text= 'Nilai rating tidak sesuai, gagal mengirimkan umpan balik', status= False)
            )
        
        fields['user_id']= ObjectId(get_jwt_identity())
        fields['created_at']= datetime.datetime.now()
        result= mongo.db.app_feedbacks.insert_one(dict(fields))

        if result.inserted_id is None:
            return CreateAppFeedback(
                created_feedback= None,
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal mengirimkan umpan balik', status= False)
            ) 

        created_feedback= mongo.db.app_feedbacks.find_one({ '_id': result.inserted_id, 'user_id': ObjectId(get_jwt_identity()) })
        created_feedback['user']= mongo.db.users.find_one({ '_id': ObjectId(get_jwt_identity()) })
        created_feedback['created_at']= {
            'date': created_feedback['created_at'].date(),
            'time': created_feedback['created_at'].time()
        }

        return CreateAppFeedback(
            created_feedback= created_feedback, 
            response= ResponseMessage(text= 'Umpan balik berhasil terkirim', status= True)
        ) 

class RemoveAppFeedbacks(graphene.Mutation):
    class Arguments:
        feedback_ids= graphene.List(graphene.String)
    
    removed_feedbacks= graphene.List(graphene.String)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, feedback_ids):
        feedbacks= [str(feedback['_id']) for feedback in mongo.db.app_feedbacks.find({})]
        is_feedback_ids_exist= all(_id in feedbacks for _id in feedback_ids)
    
        if is_feedback_ids_exist is False:
            return RemoveAppFeedbacks(
                removed_feedbacks= [],
                response= ResponseMessage(text= 'Umpan balik tidak ditemukan, umpan balik gagal terhapus', status= False)
            )

        for i in range(len(feedback_ids)):
            feedback_ids[i]= ObjectId(feedback_ids[i])

        result= mongo.db.app_feedbacks.delete_many({ '_id': { '$in': feedback_ids } })

        if result.deleted_count == 0:
            return RemoveAppFeedbacks(
                removed_feedbacks= [],
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, umpan balik gagal terhapus', status= False)
            )

        return RemoveAppFeedbacks(
            removed_feedbacks= feedback_ids,
            response= ResponseMessage(text= 'Berhasil menghapus umpan balik aplikasi', status= True)
        )

class FeedbackMutation(graphene.AbstractType):
    create_app_feedback= CreateAppFeedback.Field()
    remove_app_feedbacks= RemoveAppFeedbacks.Field()