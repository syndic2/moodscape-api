import graphene
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

import datetime

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import UserInput, User, ProtectedUser

class CreateUser(graphene.Mutation):
    class Arguments:
        fields= UserInput()
    
    created_user= graphene.Field(User)
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, fields):
        #if fields is None or 'first_name' not in fields or 'last_name' not in fields or 'gender' not in fields or 'age' not in fields or 'email' not in fields or 'username' not in fields or 'password' not in fields or 'confirm_password' not in fields:
        #    return CreateUser(response= ResponseMessage(text= 'Terjadi kesalahan pada server, data yang dikirimkan tidak lengkap.', status= False))
        #
        #for key, value in fields.items():
        #    if value is None or value == '' or (key == 'age' and value == 0):
        #        return CreateUser(response= ResponseMessage(text= 'Kolom registrasi tidak boleh ada yang kosong!', status= False))
        #
        #if fields.password != fields.confirm_password:
        #    return CreateUser(response= ResponseMessage(text= 'Konfirmasi kata sandi dengan kata sandi tidak cocok!', status= False))
        #
        #del fields['confirm_password']

        exist= mongo.db.users.find_one({
            '$or': [
                { 'email': fields.email },
                { 'username': fields.username }
            ]
        })

        if exist:
            return CreateUser(response= ResponseMessage(text= 'Alamat surel atau nama pengguna sudah ada yang menggunakan', status= False))

        result= mongo.db.users.insert_one(dict(fields))
        
        if result.inserted_id is None:
            return CreateUser(response= ResponseMessage(text= 'Terjadi kesalahan pada server, registrasi akun gagal', status= False))

        fields['_id']= result.inserted_id

        return CreateUser(created_user= User(fields), response= ResponseMessage(text= 'Registrasi akun baru berhasil!', status= True))

class UpdateUser(graphene.Mutation):
    class Arguments:
        fields= UserInput()

    updated_user= graphene.Field(ProtectedUser)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, root, fields):
        #for key, value in fields.items():
        #    if value is None or value == '':
        #        return UpdateUser(response= ResponseMessage(text= 'Kolom tidak boleh ada yang kosong!', status= False))

        exist= mongo.db.users.find_one({
            '$and': [
                { 
                    '_id': { 
                        '$ne': ObjectId(get_jwt_identity())
                    } 
                },
                { 'email': fields['email'] }
            ]
        })

        if exist:
            return UpdateUser(response= ResponseMessage(text= 'Surel telah ada yang menggunakan, coba dengan surel lain', status= False))

        fields['last_profile_changed_at']= datetime.datetime.utcnow()
        result= mongo.db.users.find_one_and_update( 
            { '_id': ObjectId(get_jwt_identity()) },
            { '$set': dict(fields) }
        )

        if result is None:
            return UpdateUser(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal perbarui profil', status= False))
    
        return UpdateUser(updated_user= User(result), response= ResponseMessage(text= 'Perubahan profil tersimpan', status= True))

class ChangePassword(graphene.Mutation):
    class Arguments:
        old_password= graphene.String()
        new_password= graphene.String()

    user_with_new_password= graphene.Field(ProtectedUser)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, root, old_password, new_password):
        result= mongo.db.users.find_one({
            '_id': ObjectId(get_jwt_identity()),
            'password': old_password
        })

        if result is None:
            return ChangePassword(response= ResponseMessage(text= 'Gagal mengubah kata sandi, kata sandi lama salah', status= False))   

        result= mongo.db.users.find_one_and_update(
            { '_id': ObjectId(get_jwt_identity()) },
            { '$set': { 'password': new_password } }
        )

        if result is None:
            return ChangePassword(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal mengubah kata sandi', status= False))   

        return ChangePassword(user_with_new_password= User(result), response= ResponseMessage(text= 'Berhasil mengubah kata sandi', status= True))    

class UserMutation(graphene.AbstractType):
    create_user= CreateUser.Field()
    update_user= UpdateUser.Field()
    change_password= ChangePassword.Field()