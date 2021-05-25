from typing import Text
import graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import ArchivedArticleIds, ProtectedArchivedArticleIds

class ArchiveArticle(graphene.Mutation):
    class Arguments:
        article_ids= graphene.List(graphene.Int)
    
    archived_articles= graphene.Field(ProtectedArchivedArticleIds)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, root, article_ids):
        archived= mongo.db.user_articles.find_one({ 
            'user_id': ObjectId(get_jwt_identity()),
            'archived_articles': {
                '$in': article_ids
            }
        })

        if archived:
            return ArchiveArticle(response= ResponseMessage(text= 'Artikel ini sudah tersimpan', status= False))

        already_had= mongo.db.user_articles.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if already_had:
            result= mongo.db.user_articles.update_one( 
                { 'user_id': ObjectId(get_jwt_identity()) },
                { 
                    '$push': { 
                        'archived_articles': { '$each': article_ids }
                    }
                }
            )

            return ArchiveArticle(archived_articles= ArchivedArticleIds(article_ids= article_ids), response= ResponseMessage(text= 'Berhasil menyimpan artikel', status= True))

        archives= mongo.db.user_articles.find({}).sort('_id', -1)

        if (archives.count() > 0):
            _id= archives[0]['_id']+1
        else:
            _id= 1

        result= mongo.db.user_articles.insert_one({
            '_id': _id,
            'user_id': ObjectId(get_jwt_identity()),
            'archived_articles': article_ids
        })

        if result.inserted_id is None:
            return ArchiveArticle(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal menyimpan artikel', status= False))

        return ArchiveArticle(archived_articles= ArchivedArticleIds(article_ids= article_ids), response= ResponseMessage(text= 'Berhasil menyimpan artikel dalam arsip', status= True))

class RemoveArchivedArticles(graphene.Mutation):
    class Arguments:
        article_ids= graphene.List(graphene.Int)
    
    removed_articles= graphene.Field(ProtectedArchivedArticleIds)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, root, article_ids):
        result= mongo.db.user_articles.find_one_and_update(
            { 
                'user_id': ObjectId(get_jwt_identity()),
                'archived_articles': {
                    '$in': article_ids
                }
            },
            { 
                '$pull': {
                    'archived_articles': {
                        '$in': article_ids
                    }
                }
            }
        )

        if result is None:
            return RemoveArchivedArticles(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal menghapus artikel dari arsip', status= False))
        
        return RemoveArchivedArticles(removed_articles= ArchivedArticleIds(article_ids= article_ids), response= ResponseMessage(text= 'Berhasil menghapus artikel dari arsip', status= True))

class UserArticlesMutation(graphene.AbstractType):
    archive_articles= ArchiveArticle.Field()
    remove_archived_articles= RemoveArchivedArticles.Field()