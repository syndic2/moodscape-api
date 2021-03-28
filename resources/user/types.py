import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage

class UserAbstract(graphene.AbstractType):
    first_name= graphene.String()
    last_name= graphene.String()
    gender= graphene.String()
    age= graphene.Int()
    email= graphene.String()
    username= graphene.String()
    password= graphene.String()
    img_url= graphene.String()

class UserInput(UserAbstract, graphene.InputObjectType):
    confirm_password= graphene.String()

    def __setattr__(self, name, value):
        if value is not None:
            self.__dict__[name]= value

class User(UserAbstract, graphene.ObjectType):
    _id= graphene.String()  

    def __init__(self, data):
        for key in data:
            if key == '_id':
                data[key]= str(data[key])

            setattr(self, key, data[key])

class ProtectedUser(graphene.Union):
    class Meta:
        types= (User, AuthInfoField, ResponseMessage)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

    