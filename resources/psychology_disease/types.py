import graphene

class PsychologyDiseaseAbstract(graphene.AbstractType):
    name= graphene.String()
    short_description= graphene.String()
    img_url= graphene.String()
    url= graphene.String()

class PsychologyDiseaseInput(PsychologyDiseaseAbstract, graphene.InputObjectType):
    pass

class PsychologyDisease(PsychologyDiseaseAbstract, graphene.ObjectType):
    _id= graphene.Int()

