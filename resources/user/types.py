import graphene
from flask_graphql_auth import AuthInfoField

from ..utility_types import ResponseMessage

class UserAbstract(graphene.AbstractType):
    first_name= graphene.String()
    last_name= graphene.String()
    gender= graphene.String()
    date_of_birth= graphene.String()
    email= graphene.String()
    username= graphene.String()
    password= graphene.String()
    img_url= graphene.String()
    joined_at= graphene.String()
    is_active= graphene.Boolean()

class UserInput(UserAbstract, graphene.InputObjectType):
    confirm_password= graphene.String()

class User(UserAbstract, graphene.ObjectType):
    _id= graphene.String()  

class UsersGroupByGender(graphene.ObjectType):
    males= graphene.List(User)
    females= graphene.List(User)

class UserAgeGroup(graphene.ObjectType):
    group= graphene.String()
    range= graphene.String()
    users= graphene.List(User)

class UsersGroupByAge(graphene.ObjectType):
    children= graphene.Field(UserAgeGroup)
    teenager= graphene.Field(UserAgeGroup)
    adult= graphene.Field(UserAgeGroup)
    elderly= graphene.Field(UserAgeGroup)
    above_elderly= graphene.Field(UserAgeGroup)

class UsersGrowthByYear(graphene.ObjectType):
    month_name= graphene.String()
    month_number= graphene.Int()
    year= graphene.Int()
    users= graphene.List(User)

class UserResponse(graphene.ObjectType):
    user= graphene.Field(User)
    response= graphene.Field(ResponseMessage)

class ProtectedUser(graphene.Union):
    class Meta:
        types= (UserResponse, AuthInfoField)
    
    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)

    