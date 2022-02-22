import datetime, graphene
from flask import render_template
from flask_graphql_auth import get_jwt_identity, create_access_token, create_refresh_token, mutation_jwt_refresh_token_required
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_mail import Message
from bson import ObjectId

from os import environ as ENV
import datetime
import secrets

from extensions import mail, mongo
from ..user.types import UserInput, User
from ..utility_types import ResponseMessage

class AdminAuthentication(graphene.Mutation):
    class Arguments:
        email_or_username= graphene.String()
        password= graphene.String()

    authenticated_user= graphene.Field(User)

    access_token= graphene.String()
    refresh_token= graphene.String()
    response= graphene.Field(ResponseMessage)
    
    def mutate(self, info, email_or_username, password):
        result= mongo.db.users.find_one({
            '$or': [
                { 'email': email_or_username },
                { 'username': email_or_username }
            ],
            'is_admin': True 
        })

        if result is None or check_password_hash(result['password'], password) is False:
            return AdminAuthentication(response= ResponseMessage(text= 'Alamat surel/nama pengguna atau kata sandi anda salah!', status= False))

        return AdminAuthentication(
            access_token= create_access_token(str(result['_id'])),
            refresh_token= create_refresh_token(str(result['_id'])),
            response= ResponseMessage(text= 'Berhasil masuk', status= True)
        )

class Authentication(graphene.Mutation):
    class Arguments:
        email_or_username= graphene.String()
        password= graphene.String()
        with_google= UserInput()

    authenticated_user= graphene.Field(User)
    access_token= graphene.String()
    refresh_token= graphene.String()
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, email_or_username, password, with_google):
        #if email_or_username is None or password is None or email_or_username == '' or password == '':
        #    return Authentication(response= ResponseMessage(text= 'Kolom tidak boleh ada yang kosong!', status= False))

        #LOGIN WITH GOOGLE
        if with_google:
            google_auth= Authentication.login_with_google(with_google)
            
            if google_auth is False:
                return Authentication(response= ResponseMessage(text= 'Terjadi kesalahan terhadap akun Google anda, silahkan coba kembali', status= False))
            else:
                email_or_username= with_google.email
                password= with_google.password

        authenticated_user= mongo.db.users.find_one({
            '$or': [
                { 'email': email_or_username },
                { 'username': email_or_username }
            ],
            'is_admin': False 
        })

        if authenticated_user is None:
            return Authentication(response= ResponseMessage(text= 'Alamat surel/nama pengguna atau kata sandi anda salah!', status= False))
        else:
            try:
                if not with_google and check_password_hash(authenticated_user['password'], password) is False:
                    return Authentication(response= ResponseMessage(text= 'Alamat surel/nama pengguna atau kata sandi anda salah!', status= False))
            except:
                return Authentication(response= ResponseMessage(text= 'Alamat surel/nama pengguna atau kata sandi anda salah!', status= False))
        
        if 'img_url' not in authenticated_user:
            authenticated_user['img_url']= 'https://via.placeholder.com/100'

        if 'date_of_birth' in authenticated_user:
            authenticated_user['date_of_birth']= authenticated_user['date_of_birth'].date()

        return Authentication(
            authenticated_user= authenticated_user,
            access_token= create_access_token(str(authenticated_user['_id'])),
            refresh_token= create_refresh_token(str(authenticated_user['_id'])),
            response= ResponseMessage(text= 'Berhasil masuk', status= True)
        )
    
    @staticmethod
    def login_with_google(account_info):
        exist= mongo.db.users.find_one({ 'email': account_info.email })

        if exist:
            return None
        
        account_info['joined_at']= datetime.datetime.now()
        account_info['is_admin']= False
        account_info['is_active']= True
        
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

    def mutate(self, info, email):
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
            return RequestResetPassword(response= ResponseMessage(text= 'Terjadi kesalahan pada server, permintaan ubah kata sandi gagal', status= False));
        
        try:
            message= Message('Permintaan ubah kata sandi', sender= ENV.get('MAIL_USERNAME'), recipients= [user['email']])
            message.html= render_template('emails/reset-password.html', name= user['first_name'], reset_token= token)
            mail.send(message)
        except Exception as ex:
            return RequestResetPassword(response= ResponseMessage(text= str(ex), status= False))

        return RequestResetPassword(reset_url= f"https://moodscape-app.web.app/reset-password/{token}", response= ResponseMessage(text= 'Berhasil melakukan permintaan ubah kata sandi', status= True))

class ResetPassword(graphene.Mutation):
    class Arguments:
        reset_token= graphene.String()
        new_password= graphene.String()
    
    user_with_new_password= graphene.Field(User)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, reset_token, new_password):
        requested_reset= mongo.db.reset_passwords.find_one({ 'token': reset_token })

        if requested_reset is None:
            return ResetPassword(response= ResponseMessage(text= 'Token ubah kata sandi tidak sesuai', status= False))

        if datetime.datetime.utcnow() > requested_reset['token_expiry']:
            return ResetPassword(response= ResponseMessage(text= 'Batas waktu token ubah kata sandi habis', status= False))

        result= mongo.db.users.find_one_and_update(
            { 'email': requested_reset['email'] },
            { '$set': { 'password': generate_password_hash(new_password), 'last_password_changed_at': datetime.datetime.utcnow() } }
        )
        clear_requests_reset= mongo.db.reset_passwords.delete_many({ 'email': result['email'] })

        if result is None or clear_requests_reset.deleted_count == 0:
            return ResetPassword(response= ResponseMessage(text= 'Terjadi kesalahan pada server, gagal mengubah kata sandi', status= False))

        return ResetPassword(user_with_new_password= User(result), response= ResponseMessage(text= 'Berhasil melakukan pengubahan kata sandi', status= True))

class AuthMutation(graphene.AbstractType):
    admin_login= AdminAuthentication.Field()
    login= Authentication.Field()
    refresh_auth= RefreshAuthentication.Field()
    request_reset_password= RequestResetPassword.Field()
    reset_password= ResetPassword.Field()


