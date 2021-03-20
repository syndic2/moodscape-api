import graphene
from flask_graphql_auth import get_jwt_identity, mutation_jwt_required
from bson.objectid import ObjectId

from .types import User, UserInput, ProtectedUser
from extensions import mongo

class CreateUser(graphene.Mutation):
    class Arguments:
        fields= UserInput()
    
    created_user= graphene.Field(User)
    message= graphene.String()
    status= graphene.Boolean()

    def mutate(self, root, fields):
        exist= mongo.db.users.find_one({
            '$or': [
                { 'email': fields.email },
                { 'username': fields.username }
            ]
        })

        if exist:
            return CreateUser(message= 'Email or username already taken', status= False)

        result= mongo.db.users.insert_one(vars(fields))
        
        if type(result.inserted_id) is not ObjectId:
            return CreateUser(message= 'Create user failed', status= False)

        fields['_id']= result.inserted_id
        created_user= User(fields)

        return CreateUser(  
            created_user= created_user, 
            message= 'Create user success',
            status= True
        )

class UpdateUser(graphene.Mutation):
    class Arguments:
        token= graphene.String()
        fields= UserInput()

    updated_user= graphene.Field(ProtectedUser)
    message= graphene.String()
    status= graphene.Boolean()
    
    @mutation_jwt_required
    def mutate(self, root, fields):
        user= get_jwt_identity()

        return UpdateUser(
            message= 'Update user success',
            status= True
        )

class UserMutation(graphene.AbstractType):
    create_user= CreateUser.Field()
    update_user= UpdateUser.Field()