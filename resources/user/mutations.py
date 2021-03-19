import graphene

from .types import User, UserInput
from extensions import mongo

class CreateUser(graphene.Mutation):
    class Arguments:
        user= UserInput()
    
    user= graphene.Field(User)
    status_code= graphene.String()

    def mutate(self, root, user):
        mongo.db.users.insert_one(vars(user))
        
        new_user= User(
            name= user.name,
            email= user.email
        )

        return CreateUser(user= new_user, status_code= '200 OK')

class UserMutation(graphene.AbstractType):
    new_user= CreateUser.Field()