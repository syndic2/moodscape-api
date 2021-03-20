import graphene
from flask_graphql_auth import AuthInfoField
from bson.objectid import ObjectId

class UserAbstract(graphene.AbstractType):
    first_name= graphene.String()
    last_name= graphene.String()
    gender= graphene.String()
    age= graphene.Int()
    email= graphene.String()
    username= graphene.String()
    password= graphene.String()

class User(UserAbstract, graphene.ObjectType):
    _id= graphene.String()

    def __init__(self, data):
        for key in data:
            if key == '_id':
                data[key]= ObjectId(data[key])

            setattr(self, key, data[key])

class UserInput(UserAbstract, graphene.InputObjectType):
    pass

class ProtectedUser(graphene.Union):
    class Meta:
        types= (User, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

    