import graphene
from flask_graphql_auth import (
    get_jwt_identity,
    create_access_token, 
    create_refresh_token, 
    mutation_jwt_refresh_token_required
)
from bson import ObjectId

from ..user.types import UserInput
from ..utility_types import ResponseMessage
from extensions import mongo

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
                return Authentication(response= ResponseMessage(text= 'Terjadi kesalahan terhadap akun Google anda, silahkan coba kembali.', status= False))
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

class AuthMutation(graphene.AbstractType):
    login= Authentication.Field()
    refresh_auth= RefreshAuthentication.Field()


