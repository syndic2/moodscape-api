import graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import auto_increment_id
from ..utility_types import ResponseMessage
from .types import ArticleInput, Article,  ArchivedArticleIds, ProtectedArchivedArticleIds

class UpdateArticle(graphene.Mutation):
    class Arguments:
        _id= graphene.String()
        fields= ArticleInput()
    
    updated= graphene.Boolean()
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, _id, fields):
        if ObjectId.is_valid(_id):
            _id= ObjectId(_id)
        else:
            _id= ObjectId()
        
        result= mongo.db.articles.update_one( 
            { '_id': _id },
            { '$set': dict(fields) },
            upsert= True
        )

        if result.upserted_id:
            return UpdateArticle(updated= False, response= ResponseMessage(text= 'Berhasil membuat artikel baru.', status= False))

        if result.matched_count == 0:
            return UpdateArticle(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal perbarui artikel.', status= False))

        return UpdateArticle(updated= True, response= ResponseMessage(text= 'Perubahan artikel tersimpan.', status= True))

class RemoveArticle(graphene.Mutation):
    class Arguments:
        _id= graphene.String()

    response= graphene.Field(ResponseMessage)

    def mutate(self, root, _id):
        result= mongo.db.articles.delete_one({ '_id': ObjectId(_id) })

        if result.deleted_count == 0:
            return RemoveArticle(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal menghapus artikel.', status= False)) 

        return RemoveArticle(response= ResponseMessage(text= 'Hapus artikel berhasil.', status= True))

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
        
        result= mongo.db.user_articles.insert_one({
            '_id': auto_increment_id('user_articles'),
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

class ArticleMutation(graphene.AbstractType):
    update_article= UpdateArticle.Field()
    remove_article= RemoveArticle.Field()
    archive_articles= ArchiveArticle.Field()
    remove_archived_articles= RemoveArchivedArticles.Field()