import datetime, graphene
from flask_graphql_auth import get_jwt_identity, query_header_jwt_required
from bson.objectid import ObjectId

from extensions import mongo
from utilities.helpers import default_img, is_uploaded_file_exist, get_month_name, calculate_age, datetime_format, validate_datetime, lesser_comparison_datetime
from resources.utility_types import ResponseMessage
from .types import User, UserResponse, UsersGroupByGender, UserAgeGroup, UsersGroupByAge, UsersGrowthByYear, ProtectedUser

class UserQuery(graphene.AbstractType):
    get_users= graphene.List(User)
    get_users_group_by_gender= graphene.Field(UsersGroupByGender)
    get_users_group_by_age= graphene.Field(UsersGroupByAge)
    get_users_growth_by_year= graphene.List(UsersGrowthByYear, start_date= graphene.String(), end_date= graphene.String())
    get_user= graphene.Field(User, _id= graphene.String())
    get_user_profile= graphene.Field(ProtectedUser) 

    def resolve_get_users(self, info):
        users= list(mongo.db.users.find({}))

        for user in users:
            user['date_of_birth']= user['date_of_birth'].date()
            user['joined_at']= user['joined_at'].date()
            
            if user['img_url'] != default_img and is_uploaded_file_exist(user['img_url'].split('/')[-1]) is False:
                result= mongo.db.users.update_one(
                    { '_id': ObjectId(user['_id']) },
                    { '$set': { 'img_url': default_img } }
                )

                if result.modified_count == 0:
                    return []
                
                user['img_url']= default_img

        return users    

    def resolve_get_users_group_by_gender(self, info):
        males= mongo.db.users.find({ 'gender': 'M' })
        females= mongo.db.users.find({ 'gender': 'F' })

        return UsersGroupByGender(
            males= males,
            females= females
        )

    def resolve_get_users_group_by_age(self, info):
        users= list(mongo.db.users.find({}))
        childrens= []
        teenagers= [] 
        adults= [] 
        elders= []
        above_elders= []   

        for user in users:
            age= calculate_age(user['date_of_birth'].date())

            if age >= 5 and age <= 11:
                childrens.append(user)
            elif age >= 12 and age <= 25:
                teenagers.append(user)
            elif age >= 26 and age <= 45:
                adults.append(user)
            elif age >= 46 and age <= 65:
                elders.append(user)
            elif age > 65:
                above_elders.append(user)

        return UsersGroupByAge(
            children= UserAgeGroup(group= 'Anak-anak', range= '5-11 tahun', users= childrens),
            teenager= UserAgeGroup(group= 'Remaja', range= '12-25 tahun', users= teenagers),
            adult= UserAgeGroup(group= 'Dewasa', range= '26-45 tahun', users= adults),
            elderly= UserAgeGroup(group= 'Lansia', range= '46-65 tahun', users= elders),
            above_elderly= UserAgeGroup(group= 'Di atas 65 tahun', range= '> 65 tahun', users= above_elders)
        )

    def resolve_get_users_growth_by_year(self, info, **kwargs):
        start_date= kwargs.get('start_date')
        end_date= kwargs.get('end_date')

        if lesser_comparison_datetime(start_date, end_date, 'date') is False:
            return []

        if validate_datetime(start_date, 'date') is False or validate_datetime(end_date, 'date') is False:
            return []
        
        start_date= datetime.datetime.strptime(start_date, datetime_format('date'))
        end_date= datetime.datetime.strptime(end_date, datetime_format('date'))

        users= list(mongo.db.users.find({ 'joined_at': { '$gte': start_date, '$lte': end_date } }))
        users_growth_by_year= []

        for number in range(12):
            users_growth_by_year.append(UsersGrowthByYear(
                month= get_month_name(number),
                users= []
            ))

        for user in users:
            month= user['joined_at'].date().month
            users_growth_by_year[month-1].users.append(user)
            
        return users_growth_by_year

    def resolve_get_user(self, info, _id):
      user= mongo.db.users.find_one({ '_id': ObjectId(_id) })

      return user

    @query_header_jwt_required
    def resolve_get_user_profile(self, info):
        result= mongo.db.users.find_one({ '_id': ObjectId(get_jwt_identity()) })

        if result is None:
            return UserResponse(
                user= None,
                response= ResponseMessage(text= 'Profil pengguna tidak ditemukan', status= False)
            )

        result['date_of_birth']= result['date_of_birth'].date()
        result['joined_at']= result['joined_at'].date()

        return UserResponse(
            user= result,
            response= ResponseMessage(text= 'Berhasil mengembalikan profil pengguna', status= True)
        )
