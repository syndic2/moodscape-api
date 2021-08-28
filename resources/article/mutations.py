import graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import get_sequence
from ..utility_types import ResponseMessage
from .types import ArticleInput, Article

class UpdateArticle(graphene.Mutation):
    class Arguments:
        _id= graphene.String()
        fields= ArticleInput()
    
    updated= graphene.Boolean()
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, _id, fields):
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

    def mutate(self, info, _id):
        result= mongo.db.articles.delete_one({ '_id': ObjectId(_id) })

        if result.deleted_count == 0:
            return RemoveArticle(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal menghapus artikel.', status= False)) 

        return RemoveArticle(response= ResponseMessage(text= 'Hapus artikel berhasil.', status= True))

class ArchiveArticle(graphene.Mutation):
    class Arguments:
        article_ids= graphene.List(graphene.Int)
    
    archived_articles= graphene.List(Article)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, article_ids):
        is_article_ids_exist= mongo.db.articles.find({ '_id': { '$all': article_ids } })

        if is_article_ids_exist is None:
            return ArchiveArticle(
                archived_articles= [],
                response= ResponseMessage(text= 'Artikel tidak ditemukan, artikel gagal tersimpan', status= False)
            ) 
        
        articles= list(mongo.db.articles.find({ '_id': { '$in': article_ids } }))
        
        is_user_articles_exist= mongo.db.user_articles.find_one({ 'user_id': ObjectId(get_jwt_identity()) })

        if is_user_articles_exist is None:
            create_user_articles= mongo.db.user_articles.insert_one({
                '_id': get_sequence('user_articles'),
                'user_id': ObjectId(get_jwt_identity()),
                'archived_articles': []
            })

            if create_user_articles.inserted_id is None:
                return ArchiveArticle(
                    archived_articles= [],
                    response= ResponseMessage(text= 'Tidak dapat membuat user_articles baru, artikel gagal tersimpan', status= False)
                )

        is_already_archived= mongo.db.user_articles.find_one({ 
            'user_id': ObjectId(get_jwt_identity()),
            'archived_articles': {
                '$in': article_ids
            }
        })

        if is_already_archived:
            return ArchiveArticle(
                archived_articles= [],
                response= ResponseMessage(text= 'Artikel ini sudah tersimpan', status= False)
            )

        result= mongo.db.user_articles.update_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            {
                '$push': {
                    'archived_articles': { '$each': article_ids }
                }
            }
        )

        if result.modified_count == 0:
            return ArchiveArticle(
                archived_articles= [],
                response= ResponseMessage(text= 'Terjadi kendala pada server, artikel gagal tersimpan', status= False)
            )

        return ArchiveArticle(
            archived_articles= articles,
            response= ResponseMessage(text= 'Artikel tersimpan', status= True)
        )

class RemoveArchivedArticles(graphene.Mutation):
    class Arguments:
        article_ids= graphene.List(graphene.Int)
    
    removed_articles= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, article_ids):
        is_article_ids_exist= mongo.db.user_articles.find_one({
            'user_id': ObjectId(get_jwt_identity()),
            'archived_articles': { '$all': article_ids }
        })

        if is_article_ids_exist is None:
            return RemoveArchivedArticles(
                removed_articles= [],
                response= ResponseMessage(text= 'Artikel tidak ditemukan, artikel gagal terhapus', status= False)
            )

        result= mongo.db.user_articles.update_one(
            { 'user_id': ObjectId(get_jwt_identity()) },
            { 
                '$pull': {
                    'archived_articles': { '$in': article_ids }
                }
            }
        )

        if result.modified_count == 0:
            return RemoveArchivedArticles(
                removed_articles= [],
                response= ResponseMessage(text= 'Terjadi kendala pada server, artikel gagal terhapus', status= False)
            )
        
        return RemoveArchivedArticles(
            removed_articles= article_ids, 
            response= ResponseMessage(text= 'Berhasil menghapus artikel', status= True)
        )

class ArticleMutation(graphene.AbstractType):
    update_article= UpdateArticle.Field()
    remove_article= RemoveArticle.Field()
    archive_articles= ArchiveArticle.Field()
    remove_archived_articles= RemoveArchivedArticles.Field()