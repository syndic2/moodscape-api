import graphene
from bson.objectid import ObjectId

from extensions import mongo
from .types import ArticleInput, Article, ArticlePagination

class ArticleQuery(graphene.AbstractType):
    article= graphene.Field(Article, _id= graphene.Int())
    article_by_url_name= graphene.Field(Article, url_name= graphene.String())
    all_article= graphene.Field(
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

    def resolve_all_article(self, info, **kwargs):
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