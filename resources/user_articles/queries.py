import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import UserArticles, ProtectedUserArticles

class UserArticlesQuery(graphene.AbstractType):
    archived_articles= graphene.Field(ProtectedUserArticles)
    
    @query_header_jwt_required
    def resolve_archived_articles(self, info):
        article_ids= mongo.db.user_articles.find_one({ 'user_id': ObjectId("60583c9845da16c2712b9155") })['archived_articles']
        articles= mongo.db.articles.find({
            '_id': {
                '$in': article_ids
            }
        }).sort('_id', -1)

        return UserArticles(_id= 1, user_id= '1', articles= articles, response= ResponseMessage(text= 'Berhasil mengembalikan respon', status= True))