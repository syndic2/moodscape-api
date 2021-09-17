import graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import ArticleInput, Article, ArticlePagination, UserArticles, ProtectedUserArticles

class GetArticle(graphene.ObjectType):
    get_articles= graphene.List(Article, title= graphene.String())
    get_article_pagination= graphene.Field(ArticlePagination, offset= graphene.Int(default_value= 5), limit= graphene.Int(default_value= 0))
    get_article= graphene.Field(Article, _id= graphene.Int())
    get_article_by_url_name= graphene.Field(Article, url_name= graphene.String())
    get_filtered_articles= graphene.Field(graphene.List(Article), fields= graphene.Argument(ArticleInput))

    def resolve_get_articles(self, info, title):
        fields= {}

        if title != '':
            fields['title']= { '$regex': title, '$options': 'i' }
        
        articles= list(mongo.db.articles.find(fields).sort('_id', -1))

        for article in articles:
            article['posted_at']= article['posted_at'].date()

        return articles

    def resolve_get_article_pagination(self, info, **kwargs):
        fields= {}
        offset= kwargs.get('offset')
        limit= kwargs.get('limit')

        total_articles= mongo.db.articles.find({}).count()

        #PAGINATE
        if offset < len(list(mongo.db.articles.find({}))):
            last_id= dict(mongo.db.articles.find({}).sort('_id')[offset])['_id']
            fields['_id']= { '$gte': last_id }
        else:
            fields['_id']= { '$gte': total_articles-limit }
        
        articles= mongo.db.articles.find(dict(fields)).limit(limit)
        articles = sorted(articles, key= lambda i: i['_id'], reverse= True)

        for article in articles:
            article['posted_at']= article['posted_at'].date()

        return ArticlePagination(
            offset= offset,
            limit= limit,
            max_page= total_articles/limit,
            articles= articles
        )
    
    def resolve_get_article(self, info, _id): 
        article= mongo.db.articles.find_one({ '_id': ObjectId(_id) })
        article['posted_at']= article['posted_at'].date()

        return article
    
    def resolve_get_article_by_url_name(self, info, url_name):
        article= mongo.db.articles.find_one({ 'url_name': url_name })
        article['posted_at']= article['posted_at'].date()

        return article
    
    def resolve_get_filtered_articles(self, info, fields):
        if fields.title:
            fields['title']= { '$regex': fields['title'], '$options': 'i' }

        articles= mongo.db.articles.find(fields)
        
        for article in articles:
            article['posted_at']= article['posted_at'].date()

        return articles

class GetUserArticles(graphene.ObjectType):
    get_archived_articles= graphene.Field(ProtectedUserArticles)
    get_filtered_archived_articles= graphene.Field(graphene.List(Article), fields= graphene.Argument(ArticleInput))

    @query_header_jwt_required
    def resolve_get_archived_articles(self, info):
        user_articles= mongo.db.user_articles.find_one({ 'user_id': ObjectId(get_jwt_identity()) })
        
        if user_articles is None:
            return UserArticles(articles= [], response= ResponseMessage(text= 'Belum memiliki artikel yang tersimpan', status= False))

        articles= list(mongo.db.articles.find({ '_id': { '$in': user_articles['archived_articles'] } }).sort('_id', -1))

        for article in articles:
            article['posted_at']= article['posted_at'].date()

        return UserArticles(
            _id= user_articles['_id'], 
            user_id= ObjectId(get_jwt_identity()), 
            articles= articles, 
            response= ResponseMessage(text= 'Berhasil mengembalikan artikel user', status= True)
        )
    
    @query_header_jwt_required
    def resolve_get_filtered_archived_articles(self, info, fields):
        is_user_articles_exist= mongo.db.user_articles.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if is_user_articles_exist is None:
            return []
        
        fields['_id']= { '$in': is_user_articles_exist['archived_articles'] }

        if fields.title:
            fields['title']= { '$regex': fields['title'], '$options': 'i' }

        articles= mongo.db.articles.find(fields)

        for article in articles:
            article['posted_at']= article['posted_at'].date()

        return articles

class ArticleQuery(GetArticle, GetUserArticles, graphene.AbstractType):
    pass