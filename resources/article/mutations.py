import graphene
from bson.objectid import ObjectId

from extensions import mongo
from .types import ArticleInput, Article
from ..utility_types import ResponseMessage

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

class DeleteArticle(graphene.Mutation):
    class Arguments:
        _id= graphene.String()

    response= graphene.Field(ResponseMessage)

    def mutate(self, root, _id):
        result= mongo.db.articles.delete_one({ '_id': ObjectId(_id) })

        if result.deleted_count == 0:
            return DeleteArticle(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal menghapus artikel.', status= False)) 

        return DeleteArticle(response= ResponseMessage(text= 'Hapus artikel berhasil.', status= True))

class ArticleMutation(graphene.AbstractType):
    update_article= UpdateArticle.Field()
    delete_article= DeleteArticle.Field()