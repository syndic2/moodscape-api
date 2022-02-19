import os, datetime, graphene
from graphene_file_upload.scalars import Upload
from flask import request
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import default_img, is_uploaded_file_exist, upload_path, formatted_file_name, datetime_format, validate_datetime, get_sequence
from ..utility_types import ResponseMessage
from .types import ArticleInput, Article

class CreateArticle(graphene.Mutation):
    class Arguments:
        fields= ArticleInput()
        header_img_upload= Upload()

    created_article= graphene.Field(Article)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields, header_img_upload):
        if validate_datetime(fields.posted_at, 'date') is False:
            return CreateArticle(
                updated_article= None, 
                response= ResponseMessage(text= 'Format tanggal tidak valid, artikel gagal terbuat', status= False)
            )

        is_article_title_exist= mongo.db.articles.find_one({ 'title': fields.title })

        if is_article_title_exist:
            return CreateArticle(
                updated_article= None, 
                response= ResponseMessage(text= 'Judul sudah terpakai, artikel gagal terbuat', status= False)
            )

        fields= {
            '_id': get_sequence('articles'),
            'title': fields['title'],
            'short_summary': fields['short_summary'],
            'author': fields['author'],
            'posted_at': datetime.datetime.strptime(fields.posted_at, datetime_format('date')),
            'reviewed_by': fields['reviewed_by'],
            'header_img': default_img,
            'content': fields['content'],
            'url_name': fields['title'].lower().replace(', ', ' ').replace(' ', '-'),
            'url': ''
        }

        if header_img_upload.filename != 'default':
            file_name= formatted_file_name(header_img_upload.filename)
            fields['header_img']= f"{request.host_url}uploads/images/{file_name}"
            header_img_upload.save(os.path.join(f"{upload_path}/images", file_name))

        result= mongo.db.articles.insert_one(dict(fields))

        if result.inserted_id is None:
            return CreateArticle(
                updated_article= None, 
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, artikel gagal terbuat', status= False)
            )

        created_article= list(mongo.db.articles.find({}).sort('_id', -1).limit(1))[0]
        created_article['posted_at']= created_article['posted_at'].date()

        return CreateArticle(
            created_article= created_article,
            response= ResponseMessage(text= 'Berhasil menambahkan artikel baru', status= True)
        )

class UpdateArticle(graphene.Mutation):
    class Arguments:
        _id= graphene.Int()
        fields= ArticleInput()
        header_img_upload= Upload()
    
    updated_article= graphene.Field(Article)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, _id, fields, header_img_upload):
        if validate_datetime(fields.posted_at, 'date') is False:
            return UpdateArticle(
                updated_article= None, 
                response= ResponseMessage(text= 'Format tanggal tidak valid, artikel gagal diperbarui', status= False)
            ) 

        is_article_title_exist= mongo.db.articles.find_one({ '_id': { '$ne': _id }, 'title': fields.title })

        if is_article_title_exist:
            return UpdateArticle(
                updated_article= None, 
                response= ResponseMessage(text= 'Judul sudah terpakai, artikel gagal diperbarui', status= False)
            )

        fields['posted_at']= datetime.datetime.strptime(fields.posted_at, datetime_format('date'))
        
        if header_img_upload.filename != 'default':
            file_name= formatted_file_name(header_img_upload.filename)
            fields['header_img']= f"{request.host_url}uploads/images/{file_name}"
            header_img_upload.save(os.path.join(f"{upload_path}/images", file_name))

        result= mongo.db.articles.find_one_and_update(
            { '_id': _id },
            { '$set': dict(fields) }
        )

        if result is None:
            return UpdateArticle(
                updated_article= None, 
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, artikel gagal diperbarui', status= False)
            )

        updated_article= mongo.db.articles.find_one({ '_id': _id })
        updated_article['posted_at']= updated_article['posted_at'].date()

        if updated_article['header_img'] != default_img and is_uploaded_file_exist(updated_article['header_img'].split('/')[-1]) is False:
            result= mongo.db.articles.update_one(
                { '_id': _id },
                { '$set': { 'header_img': default_img } }
            )

            if result.modified_count == 0:
                return UpdateArticle(
                    updated_article= None, 
                    response= ResponseMessage(text= 'Terjadi kesalahan pada gambar artikel, artikel gagal diperbarui', status= False)
                )

            updated_article['header_img']= default_img

        return UpdateArticle(
            updated_article= updated_article, 
            response= ResponseMessage(text= 'Berhasil membarui artikel', status= True)
        )

class RemoveArticles(graphene.Mutation):
    class Arguments:
        article_ids= graphene.List(graphene.Int)

    removed_articles= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, article_ids):
        articles= [article['_id'] for article in list(mongo.db.articles.find({}))]
        is_article_ids_exist= all(_id in articles for _id in article_ids)

        if is_article_ids_exist is False:
            return RemoveArticles(
                removed_articles= [],
                response= ResponseMessage(text= 'Artikel tidak ditemukan, artikel gagal terhapus', status= False)
            ) 
        
        result= mongo.db.articles.delete_many({ '_id': { '$in': article_ids } })

        if result.deleted_count == 0:
            return RemoveArticles(
                removed_articles= [],
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, artikel gagal terhapus', status= False)
            ) 
    
        return RemoveArticles(
            removed_articles= article_ids,
            response= ResponseMessage(text= 'Berhasil menghapus artikel', status= True)
        )

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
    create_article= CreateArticle.Field()
    update_article= UpdateArticle.Field()
    remove_articles= RemoveArticles.Field()
    archive_articles= ArchiveArticle.Field()
    remove_archived_articles= RemoveArchivedArticles.Field()