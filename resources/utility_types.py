import graphene

class ResponseMessage(graphene.ObjectType):
    text= graphene.String()
    status= graphene.Boolean()