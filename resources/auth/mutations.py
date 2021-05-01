import graphene
from flask import render_template
from flask_graphql_auth import (
    get_jwt_identity,
    create_access_token, 
    create_refresh_token, 
    mutation_jwt_refresh_token_required
)
from flask_mail import Message
from bson import ObjectId

import datetime
import secrets

from extensions import mail, mongo
from ..user.types import UserInput, User
from ..utility_types import ResponseMessage

class Authentication(graphene.Mutation):
    class Arguments:
        email_or_username= graphene.String()
        password= graphene.String()
        with_google= UserInput()

    access_token= graphene.String()
    refresh_token= graphene.String()
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, email_or_username= '', password= '', with_google= None):
        #if email_or_username is None or password is None or email_or_username == '' or password == '':
        #    return Authentication(response= ResponseMessage(text= 'Kolom tidak boleh ada yang kosong!', status= False))

        #LOGIN WITH GOOGLE
        if with_google:
            google_auth= Authentication.login_with_google(with_google)
            
            if google_auth is False:
                return Authentication(response= ResponseMessage(text= 'Terjadi kesalahan terhadap akun Google anda, silahkan coba kembali', status= False))
            elif google_auth is True:
                email_or_username= with_google.email
                password= with_google.password

        user= mongo.db.users.find_one({
            '$or': [
                { 'email': email_or_username },
                { 'username': email_or_username }
            ],
            'password': password 
        })

        if user is None:
            return Authentication(response= ResponseMessage(text= 'Alamat surel/nama pengguna atau kata sandi anda salah!', status= False))

        return Authentication(
            access_token= create_access_token(str(user['_id'])),
            refresh_token= create_refresh_token(str(user['_id'])),
            response= ResponseMessage(text= 'Login success', status= True)
        )
    
    @staticmethod
    def login_with_google(account_info):
        exist= mongo.db.users.find_one({ 'email': account_info.email })

        if exist:
            return None
        
        result= mongo.db.users.insert_one(dict(account_info))

        if result.inserted_id is None or type(result.inserted_id) is not ObjectId:
            return False

        return True

class RefreshAuthentication(graphene.Mutation):
    class Arguments:
        refresh_token= graphene.String()
    
    new_token= graphene.String()

    @mutation_jwt_refresh_token_required
    def mutate(self):
        current_user= get_jwt_identity()

        return RefreshAuthentication(new_token= create_access_token(identity= current_user))

class RequestResetPassword(graphene.Mutation):
    class Arguments:
        email= graphene.String()

    reset_url= graphene.String()
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, email):
        user= mongo.db.users.find_one({ 'email': email })

        if user is None:
            return RequestResetPassword(response= ResponseMessage(text= 'Alamat surel anda salah atau belum terdaftar!', status= False))
        
        token= secrets.token_urlsafe()
        token_expiry= datetime.datetime.utcnow()+datetime.timedelta(minutes= 15)

        result= mongo.db.reset_passwords.insert_one({
            'email': user['email'],
            'token': token,
            'token_expiry': token_expiry
        })

        if result.inserted_id is None:
            return RequestResetPassword(response= ResponseMessage(text= 'Terjadi kesalahan pada server, permintaan ubah kata sandi gagal', status= False))

        try:
            message= Message('Permintaan ubah kata sandi', sender= 'moodscape.app@gmail.com', recipients= [user['email']])
            message.html= render_template('emails/reset-password.html', name= user['first_name'], reset_token= token)
            mail.send(message)
        except:
            return RequestResetPassword(response= ResponseMessage(text= 'Terjadi kesalahan pada server, permintaan ubah kata sandi gagal', status= False))

        return RequestResetPassword(reset_url= f"https://moodscape.netlify.app/reset-password/{token}", response= ResponseMessage(text= 'Berhasil melakukan permintaan ubah kata sandi', status= True))

class ResetPassword(graphene.Mutation):
    class Arguments:
        reset_token= graphene.String()
        new_password= graphene.String()
    
    user_with_new_password= graphene.Field(User)
    response= graphene.Field(ResponseMessage)

    def mutate(self, root, reset_token, new_password):
        requested_reset= mongo.db.reset_passwords.find_one({ 'token': reset_token })

        if requested_reset is None:
            return ResetPassword(response= ResponseMessage(text= 'Token ubah kata sandi tidak sesuai', status= False))

        if datetime.datetime.utcnow() > requested_reset['token_expiry']:
            return ResetPassword(response= ResponseMessage(text= 'Batas waktu token ubah kata sandi habis', status= False))

        result= mongo.db.users.find_one_and_update(
            { 'email': requested_reset['email'] },
            { '$set': { 'password': new_password, 'last_password_changed_at': datetime.datetime.utcnow() } }
        )
        clear_requests_reset= mongo.db.reset_passwords.delete_many({ 'email': result['email'] })

        if result is None or clear_requests_reset.deleted_count == 0:
            return ResetPassword(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal mengubah kata sandi', status= False))

        return ResetPassword(user_with_new_password= User(result), response= ResponseMessage(text= 'Berhasil melakukan pengubahan kata sandi', status= True))

class AuthMutation(graphene.AbstractType):
    login= Authentication.Field()
    refresh_auth= RefreshAuthentication.Field()
    request_reset_password= RequestResetPassword.Field()
    reset_password= ResetPassword.Field()


