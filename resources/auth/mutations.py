import graphene
from flask_graphql_auth import (
    get_jwt_identity,
    create_access_token, 
    create_refresh_token, 
    mutation_jwt_refresh_token_required
)

from ..utility_types import ResponseMessage
from extensions import mongo

class Authentication(graphene.Mutation):
    class Arguments:
        email_or_username= graphene.String()
        password= graphene.String()

    access_token= graphene.String()
    refresh_token= graphene.String()
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, email_or_username, password):
        user= mongo.db.users.find_one({
            '$or': [
                { 'email': email_or_username },
                { 'username': email_or_username }
            ],
            'password': password 
        })

        if user is None:
            return Authentication(response= ResponseMessage(text= 'Wrong email/username or password', status= False))

        return Authentication(
            access_token= create_access_token(str(user['_id'])),
            refresh_token= create_refresh_token(str(user['_id'])),
            response= ResponseMessage(text= 'Login success', status= True)
        )

class RefreshAuthentication(graphene.Mutation):
    class Arguments:
        RefreshToken= graphene.String()
    
    new_token= graphene.String()

    @mutation_jwt_refresh_token_required
    def mutate(self):
        current_user= get_jwt_identity()

        return RefreshToken(new_token= create_access_token(identity= current_user))

class AuthMutation(graphene.AbstractType):
    login= Authentication.Field()
    refresh_auth= RefreshAuthentication.Field()


