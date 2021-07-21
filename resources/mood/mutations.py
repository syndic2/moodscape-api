import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import auto_increment_id
from ..utility_types import ResponseMessage
from .types import MoodInput, Mood, ProtectedMood

class CreateMood(graphene.Mutation):
    class Arguments:
        fields= MoodInput()

    created_mood= graphene.Field(Mood)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields):
        #fields['_id']= auto_increment_id('moods')
        #insert_mood= mongo.db.moods.insert_one(dict(fields))
#
        #if insert_mood.inserted_id is None:
        #    return CreateMood(response= ResponseMessage(text= 'Terjadi kendala pada server, gagal menambahkan mood baru', status= False))
        
        return CreateMood(response= ResponseMessage(text= 'Berhasil menambahkan mood baru', status= True))

class UpdateMood(graphene.Mutation):
    class Arguments:
        fields= MoodInput()
    
    updated_mood= graphene.Field(Mood)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields):
        return UpdateMood(response= ResponseMessage(text= 'Berhasil membarui mood', status= True))

class RemoveMood(graphene.Mutation):
    class Arguments:
        mood_ids= graphene.List(graphene.Int)
    
    removed_moods= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, mood_ids):
        return RemoveMood(response= ResponseMessage(text= 'Berhasil menghapus mood', status= True))

class MoodMutation(graphene.AbstractType):
    create_mood= CreateMood.Field()
    update_mood= UpdateMood.Field()
    remove_mood= RemoveMood.Field()