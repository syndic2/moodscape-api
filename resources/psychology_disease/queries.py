import graphene

from extensions import mongo
from .types import PsychologyDisease

class GetDisease(graphene.ObjectType):
    get_diseases= graphene.List(PsychologyDisease, name= graphene.String())
    get_disease= graphene.Field(PsychologyDisease, _id= graphene.Int())

    def resolve_get_diseases(self, info, name):
        diseases= mongo.db.psychology_diseases.find({})

        return diseases

    def resolve_get_disease(self, info, _id):
        disease= mongo.db.psychology_diseases.find_one({ '_id': _id })
        
        return disease

class PsychologyDiseaseQuery(GetDisease, graphene.AbstractType):
    pass