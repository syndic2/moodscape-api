import graphene
from flask_graphql_auth import get_jwt_identity, mutation_jwt_required
from bson.objectid import ObjectId

from .types import UserInput, User, ProtectedUser
from ..utility_types import ResponseMessage
from extensions import mongo

class CreateUser(graphene.Mutation):
    class Arguments:
        fields= UserInput()
    
    created_user= graphene.Field(User)
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, fields):
        exist= mongo.db.users.find_one({
            '$or': [
                { 'email': fields.email },
                { 'username': fields.username }
            ]
        })

        if exist:
            return CreateUser(response= ResponseMessage(text= 'Email or username already taken', status= False))

        result= mongo.db.users.insert_one(vars(fields))
        
        if type(result.inserted_id) is not ObjectId:
            return CreateUser(response= ResponseMessage(text= 'Create user failed', status= False))

        fields['_id']= result.inserted_id

        return CreateUser(  
            created_user= User(fields), 
            response= ResponseMessage(text= 'Create user success', status= True)
        )

class UpdateUser(graphene.Mutation):
    class Arguments:
        token= graphene.String()
        fields= UserInput()

    updated_user= graphene.Field(ProtectedUser)
    response= graphene.Field(ResponseMessage)

    @mutation_jwt_required
    def mutate(self, root, fields):
        result= mongo.db.users.find_one_and_update( 
            { '_id': ObjectId(get_jwt_identity()) },
            { '$set': vars(fields) }
        )

        if result is None:
            return UpdateUser(response= ResponseMessage(text= 'Update user success', status= False))

        return UpdateUser(
            updated_user= User(result),
            response= ResponseMessage(text= 'Update user success', status= True)
        )

class UserMutation(graphene.AbstractType):
    create_user= CreateUser.Field()
    update_user= UpdateUser.Field()