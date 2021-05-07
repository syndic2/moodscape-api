import graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

import datetime

from extensions import mongo
from .types import AppFeedbackInput, AppFeedback, ProtectedAppFeedback
from ..utility_types import ResponseMessage

class CreateAppFeedback(graphene.Mutation):
    class Arguments:
        fields= AppFeedbackInput()
    
    created_feedback= graphene.Field(ProtectedAppFeedback)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, root, fields):
        if fields['rating'] > 5:
            return CreateAppFeedback(response= ResponseMessage(text= 'Nilai rating tidak sesuai, gagal mengirimkan umpan balik', status= False))

        fields['_id']= mongo.db.app_feedbacks.find({}).count()+1
        fields['user_id']= ObjectId(get_jwt_identity())
        fields['created_at']= datetime.datetime.utcnow().replace(microsecond= 0)
        result= mongo.db.app_feedbacks.insert_one(dict(fields))

        if result.inserted_id is None:
            return CreateAppFeedback(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal mengirimkan umpan balik', status= False)) 

        return CreateAppFeedback(created_feedback= AppFeedback(fields), response= ResponseMessage(text= 'Umpan balik berhasil terkirim', status= True)) 

class FeedbackMutation(graphene.AbstractType):
    create_app_feedback= CreateAppFeedback.Field()