import graphene

from extensions import mongo
from utilities.helpers import get_sequence
from ..utility_types import ResponseMessage
from .types import PsychologyDiseaseInput, PsychologyDisease

class CreateDisease(graphene.Mutation):
    class Arguments:
        fields= PsychologyDiseaseInput()
    
    created_disease= graphene.Field(PsychologyDisease)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, fields):
        return CreateDisease(
            created_disease= None,
            response= ResponseMessage(text= 'Berhasil membuat informasi penyakit psikologi baru', status= True)
        )

class UpdateDisease(graphene.Mutation):
    class Arguments:
        _id= graphene.Int()
        fields= PsychologyDiseaseInput()
    
    updated_disease= graphene.Field(PsychologyDisease)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, _id, fields):
        result= mongo.db.psychology_diseases.find_one_and_update({ '_id': _id }, { '$set': dict(fields) })

        if result is None:
            return UpdateDisease(
                updated_disease= None,
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, informasi penyakit gagal diperbarui', status= False)
            )   

        updated_disease= mongo.db.psychology_diseases.find_one({ '_id': _id })

        return UpdateDisease(
            updated_disease= updated_disease,
            response= ResponseMessage(text= 'Berhasil membarui informasi penyakit psikologi', status= True)
        )

class RemoveDiseases(graphene.Mutation):
    class Arguments:
        disease_ids= graphene.List(graphene.Int)

    removed_diseases= graphene.List(graphene.Int)
    response= graphene.Field(ResponseMessage)

    def mutate(self, info, disease_ids):
        diseases= [disease['_id'] for disease in list(mongo.db.psychology_diseases.find({}))]
        is_disease_ids_exist= all(_id in diseases for _id in disease_ids)

        if is_disease_ids_exist is False:
            return RemoveDiseases(
                removed_diseases= [],
                response= ResponseMessage(text= 'Penyakit tidak ditemukan, informasi penyakit gagal terhapus', status= False)
            )

        results= mongo.db.psychology_diseases.delete_many({ '_id': { '$in': disease_ids } })

        if results.deleted_count == 0:
            return RemoveDiseases(
                removed_diseases= [],
                response= ResponseMessage(text= 'Terjadi kesalahan pada server, informasi penyakit gagal terhapus', status= False)
            )

        return RemoveDiseases(
            removed_diseases= disease_ids,
            response= ResponseMessage(text= 'Berhasil menghapus informasi penyakit psikologi', status= True)
        )

class PsychologyDiseaseMutation(graphene.AbstractType):
    create_disease= CreateDisease.Field()
    update_disease= UpdateDisease.Field()
    remove_diseases= RemoveDiseases.Field()
