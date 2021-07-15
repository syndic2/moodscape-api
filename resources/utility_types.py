import graphene

class TimestampsAbstract(graphene.AbstractType):
    date= graphene.String()
    time= graphene.String()

class TimestampsInput(TimestampsAbstract, graphene.InputObjectType):
    pass

class Timestamps(TimestampsAbstract, graphene.ObjectType):
    pass

class ResponseMessage(graphene.ObjectType):
    text= graphene.String()
    status= graphene.Boolean()