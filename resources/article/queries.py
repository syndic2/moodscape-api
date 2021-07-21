from flask_cors.core import get_app_kwarg_dict
import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import ArticleInput, Article, ArticlePagination, UserArticles, ProtectedUserArticles

class GetArticle(graphene.ObjectType):
    article= graphene.Field(Article, _id= graphene.Int())
    article_by_url_name= graphene.Field(Article, url_name= graphene.String())
    articles= graphene.Field(
        ArticlePagination, 
        fields= graphene.Argument(ArticleInput),
        offset= graphene.Int(default_value= 5), 
        limit= graphene.Int(default_value= 0)
    )

    def resolve_article(self, info, _id): 
        article= mongo.db.articles.find_one({ '_id': ObjectId(_id) })

        return article
    
    def resolve_article_by_url_name(self, info, url_name):
        article= mongo.db.articles.find_one({ 'url_name': url_name })

        return article

    def resolve_articles(self, info, **kwargs):
        fields= kwargs.get('fields')
        offset= kwargs.get('offset')
        limit= kwargs.get('limit')

        if fields.title:        
            title= fields.title
            fields['title']= { '$regex': title, '$options': 'i' }

        total_articles= mongo.db.articles.find({}).count()

        #PAGINATE
        if offset < len(list(mongo.db.articles.find({}))):
            last_id= dict(mongo.db.articles.find({}).sort('_id')[offset])['_id']
            fields['_id']= { '$gte': last_id }
        else:
            fields['_id']= { '$gte': total_articles-limit }
        
        articles= mongo.db.articles.find(fields).limit(limit)
        articles = sorted(articles, key= lambda i: i['_id'], reverse= True)

        return ArticlePagination(
            offset= offset,
            limit= limit,
            max_page= total_articles/limit,
            articles= articles
        )

class GetUserArticles(graphene.ObjectType):
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
        
        return UserArticles(
            _id= user_articles['_id'], 
            user_id= ObjectId(get_jwt_identity()), 
            articles= articles, 
            response= ResponseMessage(text= 'Berhasil mengembalikan artikel user', status= True)
        )

class ArticleQuery(GetArticle, GetUserArticles, graphene.AbstractType):
    pass