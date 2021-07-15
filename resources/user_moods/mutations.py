from enum import auto
import graphene
from flask_graphql_auth import fields, get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import auto_increment_id
from ..utility_types import ResponseMessage
from ..mood.types import MoodInput, Mood
from .types import ProtectedUserMood

class CreateUserMood(graphene.Mutation):
    class Arguments:
        fields= MoodInput()

    created_mood= graphene.Field(Mood)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields):
        fields['_id']= auto_increment_id('moods')
        insert_mood= mongo.db.moods.insert_one(dict(fields))

        if insert_mood.inserted_id is None:
            return CreateUserMood(response= ResponseMessage(text= 'Terjadi kendala pada server, gagal menambahkan mood baru', status= False))
        
        return CreateUserMood(response= ResponseMessage(text= 'Berhasil menambahkan mood baru', status= True))

class UpdateUserMood(graphene.Mutation):
    class Arguments:
        fields= MoodInput()
    
    updated_mood= graphene.Field(Mood)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields):
        return UpdateUserMood(response= ResponseMessage(text= 'Berhasil membarui mood', status= True))

class RemoveUserMood(graphene.Mutation):
    class Arguments:
        mood_ids= graphene.List(graphene.Int)
    
    removed_moods= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, mood_ids):
        return RemoveUserMood(response= ResponseMessage(text= 'Berhasil menghapus mood', status= True))

class UserMoodMutation(graphene.AbstractType):
    create_user_mood= CreateUserMood.Field()
    update_user_mood= UpdateUserMood.Field()
    remove_user_mood= RemoveUserMood.Field()
