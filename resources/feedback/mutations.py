import datetime, graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from .types import AppFeedbackInput, AppFeedback, ChatbotFeedbackInput, ChatbotFeedback
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

class HandleAppFeedback(graphene.Mutation):
    class Arguments:
        feedback_id= graphene.String()
        handle_status= graphene.String()
        handle_note= graphene.String()

    updated_feedback= graphene.Field(ChatbotFeedback)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, feedback_id, handle_status, handle_note):
        if ObjectId.is_valid(feedback_id) is False:
            return HandleAppFeedback(
                response= ResponseMessage(text= 'Data umpan balik tidak ditemukan', status= False)
            )

        feedback= mongo.db.app_feedbacks.find_one({ '_id': ObjectId(feedback_id) })

        if feedback is None:
            return HandleAppFeedback(
                response= ResponseMessage(text= 'Data umpan balik tidak ditemukan', status= False)
            )

        if handle_status != 'NO_ACTION' and handle_status != 'ON_CHECK' and handle_status != 'COMPLETE':
            return HandleAppFeedback(
                response= ResponseMessage(text= 'Properti "HANDLE_STATUS" tidak valid', status= False)
            ) 

        result= mongo.db.app_feedbacks.find_one_and_update(
            { '_id': ObjectId(feedback_id) },
            { '$set': { 'handle_status': 'COMPLETE', 'handle_status': handle_status, 'handle_note': handle_note } }
        )

        if result is None:
            return HandleAppFeedback(
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal memperbarui data umpan balik', status= False)
            )

        updated_feedback= mongo.db.app_feedbacks.find_one({ '_id': ObjectId(feedback_id) })

        return HandleAppFeedback(
            updated_feedback= updated_feedback,
            response= ResponseMessage(text= 'Berhasil memperbarui data umpan balik', status= True)
        )

class RemoveAppFeedbacks(graphene.Mutation):
    class Arguments:
        feedback_ids= graphene.List(graphene.String)
    
    removed_feedbacks= graphene.List(graphene.String)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, feedback_ids):
        feedbacks= [str(feedback['_id']) for feedback in mongo.db.app_feedbacks.find({})]

        if len(feedback_ids) == 0:
            return RemoveAppFeedbacks(
                removed_feedbacks= [],
                response= ResponseMessage(text= 'Umpan balik tidak ditemukan, umpan balik gagal terhapus', status= False)
            ) 

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
            response= ResponseMessage(text= 'Berhasil menghapus data umpan balik aplikasi', status= True)
        )

class CreateChatbotFeedback(graphene.Mutation):
    class Arguments:
        fields= ChatbotFeedbackInput()

    created_feedback= graphene.Field(ChatbotFeedback)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, root, fields):
        if ObjectId.is_valid(fields['bot_message']['recipient_id']) is True:
            fields['bot_message']['recipient_id']= ObjectId(fields['bot_message']['recipient_id'])

        if ObjectId.is_valid(fields['bot_message']['sender']) is True:
            fields['bot_message']['sender']= ObjectId(fields['bot_message']['recipient_id'])

        for message in fields['messages']:
            if ObjectId.is_valid(message['recipient_id']) is True:
                message['recipient_id']= ObjectId(message['recipient_id'])

            if ObjectId.is_valid(message['sender']) is True:
                message['recipient_id']= ObjectId(message['sender'])

        fields['user_id']= ObjectId(get_jwt_identity())
        fields['created_at']= datetime.datetime.now()

        result= mongo.db.chatbot_feedbacks.insert_one(dict(fields))
        if result.inserted_id is None:
            return CreateChatbotFeedback(
                created_feedback= None,
                response= ResponseMessage(text= 'Umpan balik pesan chatbot berhasil dikirim', status= True)
            ) 

        created_feedback= mongo.db.chatbot_feedbacks.find_one({ '_id': result.inserted_id, 'user_id': ObjectId(get_jwt_identity()) })
        created_feedback['user']= mongo.db.users.find_one({ '_id': ObjectId(get_jwt_identity()) })
        created_feedback['created_at']= {
            'date': created_feedback['created_at'].date(),
            'time': created_feedback['created_at'].time()
        }

        return CreateChatbotFeedback(
            created_feedback= created_feedback,
            response= ResponseMessage(text= 'Umpan balik pesan chatbot berhasil dikirim', status= True)
        )

class HandleChatbotFeedback(graphene.Mutation):
    class Arguments:
        feedback_id= graphene.String()
        handle_status= graphene.String()
        handle_note= graphene.String()

    updated_feedback= graphene.Field(ChatbotFeedback)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, feedback_id, handle_status, handle_note):
        if ObjectId.is_valid(feedback_id) is False:
            return HandleChatbotFeedback(
                response= ResponseMessage(text= 'Data umpan balik tidak ditemukan', status= False)
            )

        feedback= mongo.db.chatbot_feedbacks.find_one({ '_id': ObjectId(feedback_id) })

        if feedback is None:
            return HandleChatbotFeedback(
                response= ResponseMessage(text= 'Data umpan balik tidak ditemukan', status= False)
            )

        if handle_status != 'NO_ACTION' and handle_status != 'ON_CHECK' and handle_status != 'COMPLETE':
            return HandleChatbotFeedback(
                response= ResponseMessage(text= 'Properti "HANDLE_STATUS" tidak valid', status= False)
            ) 

        result= mongo.db.chatbot_feedbacks.find_one_and_update(
            { '_id': ObjectId(feedback_id) },
            { '$set': { 'handle_status': 'COMPLETE', 'handle_status': handle_status, 'handle_note': handle_note } }
        )

        if result is None:
            return HandleChatbotFeedback(
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal memperbarui data umpan balik', status= False)
            )

        updated_feedback= mongo.db.chatbot_feedbacks.find_one({ '_id': ObjectId(feedback_id) })

        return HandleChatbotFeedback(
            updated_feedback= updated_feedback,
            response= ResponseMessage(text= 'Berhasil memperbarui data umpan balik', status= True)
        )

class RemoveChatbotFeedbacks(graphene.Mutation):
    class Arguments:
        feedback_ids= graphene.List(graphene.String)

    removed_feedbacks= graphene.List(graphene.String)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, feedback_ids):
        feedbacks= [str(feedback['_id']) for feedback in mongo.db.chatbot_feedbacks.find({})]

        if len(feedback_ids) == 0:
            return RemoveChatbotFeedbacks(
                removed_feedbacks= [],
                response= ResponseMessage(text= 'Umpan balik tidak ditemukan, umpan balik gagal terhapus', status= False)
            ) 

        is_feedback_ids_exist= all(_id in feedbacks for _id in feedback_ids)
        
        if is_feedback_ids_exist is False:
            return RemoveChatbotFeedbacks(
                removed_feedbacks= [],
                response= ResponseMessage(text= 'Umpan balik tidak ditemukan, umpan balik gagal terhapus', status= False)
            )

        for i in range(len(feedback_ids)):
            feedback_ids[i]= ObjectId(feedback_ids[i])

        result= mongo.db.chatbot_feedbacks.delete_many({ '_id': { '$in': feedback_ids } })

        if result.deleted_count == 0:
            return RemoveChatbotFeedbacks(
                removed_feedbacks= [],
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, umpan balik gagal terhapus', status= False)
            )

        return RemoveChatbotFeedbacks(
            removed_feedbacks= feedback_ids,
            response= ResponseMessage(text= 'Berhasil menghapus data umpan balik pesan chatbot', status= True)
        )

class FeedbackMutation(graphene.AbstractType):
    create_app_feedback= CreateAppFeedback.Field()
    handle_app_feedback= HandleAppFeedback.Field()    
    remove_app_feedbacks= RemoveAppFeedbacks.Field()
    create_chatbot_feedback= CreateChatbotFeedback.Field()
    handle_chatbot_feedback= HandleChatbotFeedback.Field()
    remove_chatbot_feedbacks= RemoveChatbotFeedbacks.Field()