import graphene
from bson.objectid import ObjectId

from extensions import mongo
from .types import Theme

class GetTheme(graphene.AbstractType):
    get_themes= graphene.List(Theme)
    get_active_themes= graphene.List(Theme)
    get_theme= graphene.Field(Theme, _id= graphene.String())

    def resolve_get_themes(self, info):
        themes= list(mongo.db.themes.find({}))

        return themes

    def resolve_get_active_themes(self, info):
        themes= list(mongo.db.themes.find({ 'is_active': True }))

        return themes

    def resolve_get_theme(self, info, _id):
        theme= mongo.db.themes.find_one({ '_id': ObjectId(_id) })

        return theme

class ThemeQuery(GetTheme, graphene.AbstractType):
    pass