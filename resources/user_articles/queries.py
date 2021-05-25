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
        user_articles= mongo.db.user_articles.find_one({ 'user_id': ObjectId(get_jwt_identity()) })
        
        if user_articles is None:
            return UserArticles(articles= [], response= ResponseMessage(text= 'Belum memiliki artikel yang tersimpan', status= False))

        articles= mongo.db.articles.find({
            '_id': {
                '$in': user_articles['archived_articles']
            }
        }).sort('_id', -1)
        
        return UserArticles(_id= user_articles['_id'], user_id= ObjectId(get_jwt_identity()), articles= articles, response= ResponseMessage(text= 'Berhasil mengembalikan respon', status= True))