import graphene

from .activity_seeder import ActivitySeeder
from .mood_seeder import MoodSeeder
from .habit_seeder import HabitSeeder

class QuerySeederRoot(graphene.ObjectType):
    seeds= graphene.String()

    def resolve_seeds(self, info):
        return 'GraphQL Seeder Query'

class MutationSeederRoot(
        ActivitySeeder,
        MoodSeeder,
        HabitSeeder,
        graphene.ObjectType
    ):
    pass

seeder_schema= graphene.Schema(query= QuerySeederRoot, mutation= MutationSeederRoot)