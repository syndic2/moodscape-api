import graphene

from .activity_seeder import ActivitySeeder

class QuerySeederRoot(graphene.ObjectType):
    seeds= graphene.String()

    def resolve_seeds(self, info):
        return 'GraphQL Seeder Query'

class MutationSeederRoot(
        ActivitySeeder,
        graphene.ObjectType
    ):
    pass

seeder_schema= graphene.Schema(query= QuerySeederRoot, mutation= MutationSeederRoot)