import graphene

from .types import User, UserInput
from extensions import mongo

class UserQuery(graphene.AbstractType):
    user= graphene.Field(User, name= graphene.String())

    def resolve_user(self, info, name):
        user= mongo.db.users.find_one({ 'name': name })

        return user
    