import graphene
from bson.objectid import ObjectId

from extensions import mongo
from ..utility_types import ResponseMessage
from .types import ThemeInput, Theme

class CreateTheme(graphene.Mutation):
	class Arguments:
		fields= ThemeInput()

	created_theme= graphene.Field(Theme)
	response= graphene.Field(ResponseMessage)

	def mutate(self, info, fields):
		is_theme_name_exist= mongo.db.themes.find_one({ 'name': fields.name })

		if is_theme_name_exist:
			return CreateTheme(
				created_theme= None,
				response= ResponseMessage(text= 'Nama tema sudah terpakai', status= False)
			)
		
		result= mongo.db.themes.insert_one(dict(fields))

		if result.inserted_id is None:
			return CreateTheme(
				created_theme= None,
				response= ResponseMessage(text= 'Terjadi kesalahan pada server, tema gagal terbuat', status= False)
			)

		created_theme= mongo.db.themes.find_one({ 'name': fields.name })

		return CreateTheme(
			created_theme= created_theme,
			response= ResponseMessage(text= 'Berhasil membuat tema baru', status= True)
		)

class UpdateTheme(graphene.Mutation):
	class Arguments:
		_id= graphene.String()
		fields= ThemeInput()
	
	updated_theme= graphene.Field(Theme)
	response= graphene.Field(ResponseMessage)

	def mutate(self, info, _id, fields):
		is_theme_id_exist= mongo.db.themes.find_one({ '_id': ObjectId(_id) })
		
		if is_theme_id_exist is None:
			return UpdateTheme(
				updated_theme= None,
				response= ResponseMessage(text= 'Tema tidak ditemukan, tema gagal diperbarui', status= False)
			) 
		
		is_theme_name_exist= mongo.db.themes.find_one({ 
			'$and': [ 
				{ '_id': { '$ne': ObjectId(_id) } },
				{ 'name': fields.name }
			]
		})

		if is_theme_name_exist:
			return UpdateTheme(
				updated_theme= None,
				response= ResponseMessage(text= 'Nama tema sudah terpakai', status= False)
			)

		result= mongo.db.themes.find_one_and_update(
			{ '_id': ObjectId(_id) },
			{ '$set': dict(fields) }
		)

		if result is None:
			return UpdateTheme(
				updated_theme= None,
				response= ResponseMessage(text= 'Terjadi kesalahan pada server, tema gagal diperbarui', status= False)
			) 

		updated_theme= mongo.db.themes.find_one({ '_id': ObjectId(_id) })

		return UpdateTheme(
			updated_theme= updated_theme,
			response= ResponseMessage(text= 'Berhasil membarui tema', status= True)
		)

class RemoveThemes(graphene.Mutation):
	class Arguments:
		theme_ids= graphene.List(graphene.String)
	
	removed_themes= graphene.List(graphene.String)
	response= graphene.Field(ResponseMessage)

	def mutate(self, info, theme_ids):
		themes= [str(theme['_id']) for theme in mongo.db.themes.find({})]
		is_theme_ids_exist= all(_id in themes for _id in theme_ids)
		
		if is_theme_ids_exist is False:
			return RemoveThemes(
				removed_themes= [],
				response= ResponseMessage(text= 'Tema tidak ditemukan, tema gagal terhapus', status= False)
			)

		for i in range(len(theme_ids)):
			theme_ids[i]= ObjectId(theme_ids[i])

		result= mongo.db.themes.delete_many({ '_id': { '$in': theme_ids } })

		if result.deleted_count == 0:
			return RemoveThemes(
				removed_themes= [],
				response= ResponseMessage(text= 'Terjadi kesalahan pada server, tema gagal terhapus', status= False)
			) 

		return RemoveThemes(
			removed_themes= theme_ids,
			response= ResponseMessage(text= 'Berhasil menghapus tema', status= True)
		)

class ThemeMutation(graphene.AbstractType):
	create_theme= CreateTheme.Field()
	update_theme= UpdateTheme.Field()
	remove_themes= RemoveThemes.Field()
