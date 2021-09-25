import os, datetime, graphene
from graphene_file_upload.scalars import Upload
from flask import request
from flask_graphql_auth import get_jwt_identity, mutation_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo, bcrypt
from utilities.helpers import upload_path, formatted_file_name, datetime_format, validate_datetime
from ..utility_types import ResponseMessage
from .types import UserInput, User

class CreateUser(graphene.Mutation):
    class Arguments:
        fields= UserInput()
    
    created_user= graphene.Field(User)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields):
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
            return CreateUser(
                created_user= None,
                response= ResponseMessage(text= 'Alamat surel atau nama pengguna sudah ada yang menggunakan', status= False)
            )

        result= mongo.db.users.insert_one(dict(fields))
        #init_user_activities= mongo.db.user_activities.insert_one({
        #    '_id': auto_increment_id('user_activities'),
        #    'user_id': result.inserted_id,
        #    'activities': [(activity_id+1) for activity_id in range(12)],
        #})

        if result.inserted_id is None: #and init_user_activities.inserted_id is None:
            return CreateUser(
                created_user= None,
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, registrasi akun gagal', status= False)
            )
        
        created_user= mongo.db.users.find_one({ '_id': result.inserted_id })

        return CreateUser(
            created_user= created_user, 
            response= ResponseMessage(text= 'Registrasi akun baru berhasil!', status= True)
        )

class UpdateUser(graphene.Mutation):
    class Arguments:
        _id= graphene.String()
        fields= UserInput() 
        img_upload= Upload()
    
    updated_user= graphene.Field(User)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, _id, fields, img_upload):
        if  ObjectId.is_valid(_id) is False:
            return UpdateUser(
                updated_user= None,
                response= ResponseMessage(text= 'Format Id tidak sesuai, pengguna gagal diperbarui', status= False)
            )
        
        if validate_datetime(fields['date_of_birth'], 'date') is False:
            return UpdateUser(
                updated_user= None,
                response= ResponseMessage(text= 'Format tanggal tidak sesuai, pengguna gagal diperbarui', stauts= False)
            )

        if 'date_of_birth' in fields:
            fields['date_of_birth']= datetime.datetime.strptime(fields['date_of_birth'], datetime_format('date'))
        
        if 'password' in fields:
            fields['password']= bcrypt.generate_password_hash(fields['password'])

        if img_upload.filename != 'default':
            file_name= formatted_file_name(img_upload.filename)
            fields['img_url']= f"{request.host_url}uploads/images/{file_name}"
            img_upload.save(os.path.join(f"{upload_path}/images", file_name))

        result= mongo.db.users.find_one_and_update(
            { '_id': ObjectId(_id) },
            { '$set': dict(fields) }
        );

        if result is None:
            return UpdateUser(
                updated_user= None,
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, pengguna gagal diperbarui', status= False)
            ) 

        updated_user= mongo.db.users.find_one({ '_id': ObjectId(_id) })
        updated_user['date_of_birth']= updated_user['date_of_birth'].date()
        updated_user['joined_at']= updated_user['joined_at'].date()

        return UpdateUser(
            updated_user= updated_user,
            response= ResponseMessage(text= 'Berhasil membarui informasi pengguna', status= True)
        )

class RemoveUsers(graphene.Mutation):
    class Arguments:
        user_ids= graphene.List(graphene.String)
        is_soft_delete= graphene.Boolean()
    
    removed_users= graphene.List(graphene.String)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, user_ids, is_soft_delete):
        users= [str(user['_id']) for user in mongo.db.users.find({})]
        is_user_ids_exist= all(_id in users for _id in user_ids)

        if is_user_ids_exist is False:
            return RemoveUsers(
                removed_users= [],
                response= ResponseMessage(text= 'Pengguna tidak ditemukan, pengguna gagal terhapus', status= False)
            )
        
        for i in range(len(user_ids)): 
            user_ids[i]= ObjectId(user_ids[i])
        
        if is_soft_delete:
            result= mongo.db.users.update_many(
                { '_id': { '$in': user_ids } },
                { 
                    '$set': { 'is_active': False }
                }
            )

            if result.modified_count == 0:
                return RemoveUsers(
                    removed_users= [],
                    response= ResponseMessage(text= 'Terjadi kesalahan pada server, pengguna gagal terhapus', status= False)
                )
        else:
            result= mongo.db.users.delete_many({ '_id': { '$in': user_ids } })

            if result.deleted_count == 0:
                return RemoveUsers(
                    removed_users= [],
                    response= ResponseMessage(text= 'Terjadi kesalahan pada server, pengguna gagal terhapus', status= False)
                )

        return RemoveUsers(
            removed_users= user_ids,
            response= ResponseMessage(text= 'Berhasil menghapus pengguna', status= True)
        )

class UpdateProfile(graphene.Mutation):
    class Arguments:
        fields= UserInput()

    updated_profile= graphene.Field(User)
    response= graphene.Field(ResponseMessage)

    @mutation_header_jwt_required
    def mutate(self, info, fields):
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
            return UpdateProfile(
                updated_profile= None,
                response= ResponseMessage(text= 'Surel telah ada yang menggunakan, coba dengan surel lain', status= False)
            )

        fields['last_profile_changed_at']= datetime.datetime.utcnow()
        result= mongo.db.users.find_one_and_update( 
            { '_id': ObjectId(get_jwt_identity()) },
            { '$set': dict(fields) }
        )

        if result is None:
            return UpdateProfile(
                updated_profile= None,
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal perbarui profil', status= False)
            )

        updated_user= mongo.db.users.find_one({ '_id': ObjectId(get_jwt_identity()) });

        return UpdateProfile(
            updated_profile= updated_user, 
            response= ResponseMessage(text= 'Perubahan profil tersimpan', status= True)
        )

class ChangePassword(graphene.Mutation):
    class Arguments:
        old_password= graphene.String()
        new_password= graphene.String()

    user_with_new_password= graphene.Field(User)
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
            return ChangePassword(
                user_with_new_password= None,
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal mengubah kata sandi', status= False)
            )   

        user_with_new_password= mongo.db.users.find_one({ '_id': ObjectId(get_jwt_identity()) })

        return ChangePassword(
            user_with_new_password= user_with_new_password, 
            response= ResponseMessage(text= 'Berhasil mengubah kata sandi', status= True)
        )    

class UserMutation(graphene.AbstractType):
    #user
    create_user= CreateUser.Field()
    update_user= UpdateUser.Field()
    remove_users= RemoveUsers.Field()

    #auth
    update_profile= UpdateProfile.Field()
    change_password= ChangePassword.Field()