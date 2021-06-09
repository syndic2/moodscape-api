import graphene

from resources.utility_types import ResponseMessage
from extensions import mongo

class ActivityIconsSeeder(graphene.Mutation):
    response= graphene.Field(ResponseMessage)
    
    def mutate(self, info):
        mongo.db.activity_icons.delete_many({})
        
        seeds= mongo.db.activity_icons.insert_many([
            { '_id': 1, 'name': 'person-dancing' },
            { '_id': 2, 'name': 'eating' },
            { '_id': 3, 'name': 'good-sleep' },
            { '_id': 4, 'name': 'medium-sleep' },
            { '_id': 5, 'name': 'bad-sleep' },
            { '_id': 6, 'name': 'french-fries' },
            { '_id': 7, 'name': 'home' },
            { '_id': 8, 'name': 'fork-knife' },
            { '_id': 9, 'name': 'basket' },
            { '_id': 10, 'name': 'no-meat' },
            { '_id': 11, 'name': 'no-sweets' },
            { '_id': 12, 'name': 'no-soda' },
            { '_id': 13, 'name': 'bottle' },
            { '_id': 14, 'name': 'walk' },
            { '_id': 15, 'name': 'meditation' },
            { '_id': 16, 'name': 'hand-love' },
            { '_id': 17, 'name': 'ear' },
            { '_id': 18, 'name': 'moneys' },
            { '_id': 19, 'name': 'gift' },
            { '_id': 20, 'name': 'pan' },
            { '_id': 21, 'name': 'washing-machine' },
            { '_id': 22, 'name': 'flowers' },
            { '_id': 23, 'name': 'thumb-up' },
            { '_id': 24, 'name': 'love-handshake' },
            { '_id': 25, 'name': 'check-list' },
            { '_id': 26, 'name': 'crosshair' },
            { '_id': 27, 'name': 'coffe' },
            { '_id': 28, 'name': 'scissor' },
            { '_id': 29, 'name': 'massage' },
            { '_id': 30, 'name': 'nail' },
            { '_id': 31, 'name': 'skin-care' },
            { '_id': 32, 'name': 'hot-bathub' },
            { '_id': 33, 'name': 'home' },
            { '_id': 34, 'name': 'briefcase' },
            { '_id': 35, 'name': 'laptop' },
            { '_id': 36, 'name': 'persons-handshake' },
            { '_id': 37, 'name': 'car' },
            { '_id': 38, 'name': 'barbel' },
            { '_id': 39, 'name': 'movie-tapes' },
            { '_id': 40, 'name': 'mountain' },
            { '_id': 41, 'name': 'beach-umbrella' },
            { '_id': 42, 'name': 'sunny' },
            { '_id': 43, 'name': 'cloudy' },
            { '_id': 44, 'name': 'rainy' },
            { '_id': 45, 'name': 'snowy' },
            { '_id': 46, 'name': 'thermometer' },
            { '_id': 47, 'name': 'storm' },
            { '_id': 48, 'name': 'windy' },
            { '_id': 49, 'name': 'bicycle' },
            { '_id': 50, 'name': 'peoples' }
        ]);

        if not seeds.inserted_ids:
            return ActivityIconsSeeder(response= ResponseMessage(text= 'Seeding activity_icons collection failed...', status= False))

        return ActivityIconsSeeder(response= ResponseMessage(text= 'Seeding activity_icons collection succeed...', status= True))

class ActivitiesSeeder(graphene.Mutation):
    response= graphene.Field(ResponseMessage)

    def mutate(self, info):
        mongo.db.activities.delete_many({})

        seeds= mongo.db.activities.insert_many([
            { '_id': 1, 'name': 'pesta', 'icon': 'person-dancing' },
            { '_id': 2, 'name': 'makan', 'icon': 'eating' },
            { '_id': 3, 'name': 'tidur nyenyak', 'icon': 'good-sleep' },
            { '_id': 4, 'name': 'tidur sedang', 'icon': 'medium-sleep' },
            { '_id': 5, 'name': 'tidur buruk', 'icon': 'bad-sleep' },
            { '_id': 6, 'name': 'makanan cepat saji', 'icon': 'french-fries' },
            { '_id': 7, 'name': 'buatan sendiri', 'icon': 'home' },
            { '_id': 8, 'name': 'restoran', 'icon': 'fork-knife' },
            { '_id': 9, 'name': 'kiriman', 'icon': 'basket' },
            { '_id': 10, 'name': 'tanpa daging', 'icon': 'no-meat' },
            { '_id': 11, 'name': 'tanpa gula', 'icon': 'no-sweets' },
            { '_id': 12, 'name': 'tanpa soda', 'icon': 'no-soda' },
            { '_id': 13, 'name': 'minum air putih', 'icon': 'bottle' },
            { '_id': 14, 'name': 'berjalan', 'icon': 'walk' },
            { '_id': 15, 'name': 'meditasi', 'icon': 'meditation' },
            { '_id': 16, 'name': 'kebaikan', 'icon': 'hand-love' },
            { '_id': 17, 'name': 'mendengarkan', 'icon': 'ear' },
            { '_id': 18, 'name': 'mendonasi', 'icon': 'moneys' },
            { '_id': 19, 'name': 'memberi hadiah', 'icon': 'gift' },
            { '_id': 20, 'name': 'memasak', 'icon': 'pan' },
            { '_id': 21, 'name': 'mencuci baju', 'icon': 'washing-machine' },
            { '_id': 22, 'name': 'memberi hadiah', 'icon': 'gift' },
            { '_id': 23, 'name': 'bunga', 'icon': 'flowers' },
            { '_id': 24, 'name': 'menghargai', 'icon': 'thumb-up' },
            { '_id': 25, 'name': 'waktu bersama', 'icon': 'love-handshake' },
            { '_id': 26, 'name': 'memberi hadiah', 'icon': 'gift' },
            { '_id': 27, 'name': 'membuat daftar', 'icon': 'check-list' },
            { '_id': 28, 'name': 'fokus', 'icon': 'crosshair' },
            { '_id': 29, 'name': 'istirahat', 'icon': 'coffe' },
            { '_id': 30, 'name': 'potong rambut', 'icon': 'scissor' },
            { '_id': 31, 'name': 'pijat', 'icon': 'massage' },
            { '_id': 32, 'name': 'manikur', 'icon': 'nail' },
            { '_id': 33, 'name': 'perawatan kulit', 'icon': 'skin-care' },
            { '_id': 34, 'name': 'spa', 'icon': 'hot-bathub' },
            { '_id': 35, 'name': 'rumah', 'icon': 'home' },
            { '_id': 36, 'name': 'kantor', 'icon': 'briefcase' },
            { '_id': 37, 'name': 'sekolah', 'icon': 'laptop' },
            { '_id': 38, 'name': 'mengunjungi', 'icon': 'persons-handshake' },
            { '_id': 39, 'name': 'perjalanan', 'icon': 'car' },
            { '_id': 40, 'name': 'gym', 'icon': 'barbel' },
            { '_id': 41, 'name': 'bioskop', 'icon': 'movie-tapes' },
            { '_id': 42, 'name': 'alam', 'icon': 'mountain' },
            { '_id': 43, 'name': 'liburan', 'icon': 'beach-umbrella' },
            { '_id': 44, 'name': 'cerah', 'icon': 'sunny' },
            { '_id': 45, 'name': 'mendung', 'icon': 'cloudy' },
            { '_id': 46, 'name': 'hujan', 'icon': 'rainy' },
            { '_id': 47, 'name': 'salju', 'icon': 'snowy' },
            { '_id': 48, 'name': 'panas', 'icon': 'thermometer' },
            { '_id': 49, 'name': 'badai', 'icon': 'storm' },
            { '_id': 50, 'name': 'angin kencang', 'icon': 'windy' },
            { '_id': 51, 'name': 'bersepeda', 'icon': 'bicycle' },
            { '_id': 52, 'name': 'bertemu seseorang', 'icon': 'peoples' }
        ])
        
        if not seeds.inserted_ids:
            return ActivitiesSeeder(response= ResponseMessage(text= 'Seeding activities collection failed...', status= False))

        return ActivitiesSeeder(response= ResponseMessage(text= 'Seeding activities collection succeed...', status= True))

class ActivityCategoriesSeeder(graphene.Mutation):
    response= graphene.Field(ResponseMessage)

    def mutate(self, info):
        mongo.db.activity_categories.delete_many({})
        
        seeds= mongo.db.activity_categories.insert_many([
            {
                '_id': 1,
                'category': 'Sosial',
                'activities': [1]
            },
            {
                '_id': 2,
                'category': 'Hobi',
                'activities': [2]
            },
            {
                '_id': 3,
                'category': 'Tidur',
                'activities': [3, 4, 5]
            },
            {
                '_id': 4,
                'category': 'Makanan',
                'activities': [6, 7, 8, 9, 10, 11, 12]
            },
            {
                '_id': 5,
                'category': 'Kesehatan',
                'activities': [13, 14]
            },
            {
                '_id': 6,
                'category': 'Saya Lebih Baik',
                'activities': [15, 16, 17, 18, 19]
            },
            {
                '_id': 7,
                'category': 'Pekerjaan Rumah',
                'activities': [20, 21]
            },
            {
                '_id': 8,
                'category': 'Romansa',
                'activities': [22, 23, 24, 25]
            },
            {
                '_id': 9,
                'category': 'Produktivitas',
                'activities': [26, 27, 28, 29]
            },
            {
                '_id': 10,
                'category': 'Kecantikan',
                'activities': [30, 31, 32, 33, 34]
            },
            {
                '_id': 11,
                'category': 'Tempat',
                'activities': [35, 36, 37, 38, 39, 40, 41, 42, 43]
            },
            {
                '_id': 12,
                'category': 'Cuaca',
                'activities': [44, 45, 46, 47, 48, 49, 50]
            },
            {
                '_id': 13,
                'category': 'other',
                'activities': [51, 52]
            }
        ])
    
        if not seeds.inserted_ids:
            return ActivityCategoriesSeeder(response= ResponseMessage(text= 'Seeding activity_categories collection failed...', status= False))

        return ActivityCategoriesSeeder(response= ResponseMessage(text= 'Seeding activity_categories collection succeed...', status= True))

class ActivityBaseSeeder(ActivityCategoriesSeeder, graphene.AbstractType):
    activity_icons_seeder= ActivityIconsSeeder.Field()
    activities_seeder= ActivitiesSeeder.Field()
    activity_categories_seeder= ActivityCategoriesSeeder.Field()    