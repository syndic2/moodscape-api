import graphene

from .activity_seeder import ActivityBaseSeeder

class QuerySeederRoot(graphene.ObjectType):
    seeds= graphene.String()

class MutationSeederRoot(
        ActivityBaseSeeder,
        graphene.ObjectType
    ):
    pass

seeder_schema= graphene.Schema(query= QuerySeederRoot, mutation= MutationSeederRoot)