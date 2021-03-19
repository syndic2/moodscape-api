import graphene

class UserAbstract(graphene.AbstractType):
    name= graphene.String()
    email= graphene.String()
    username= graphene.String()
    password= graphene.String()

class User(UserAbstract, graphene.ObjectType):
    pass

class UserInput(UserAbstract, graphene.InputObjectType):
    pass