import os, asyncio
from flask import Blueprint, request, jsonify
from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError, PhoneCodeExpiredError, PhoneCodeInvalidError, FloodWaitError
from bson.objectid import ObjectId
from googletrans import Translator
import text2emotion as te

from utilities.helpers import telegram_sessions_path
from extensions import mongo

telegram_service_api= Blueprint('telegram_api', __name__)

@telegram_service_api.route('/auth', methods= ['POST'])
async def auth_phone():
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    phone= request.json['phone']

    #telegram auth
    try:
        client= TelegramClient(f'{telegram_sessions_path}/phone_{phone}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)
        
        if client.is_connected() is False: 
            await client.connect()

        if not await client.is_user_authorized():
            code= await client.send_code_request(phone, force_sms= True)
            await client.disconnect()

            return jsonify(
                status= True,
                phone_code_hash= code.phone_code_hash, 
                message= f'Berhasil mengirimkan kode OTP verifikasi ke nomor {phone}'
            )
        else:
            user= await client.get_me() 
            await client.disconnect()

            return jsonify(
                status= True,
                user= {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'access_hash': user.access_hash
                }, 
                message= 'Berhasil mendapatkan data user Telegram'
            )
    except (PhoneNumberInvalidError, FloodWaitError) as ex:
        await client.disconnect()
        
        if isinstance(ex, PhoneNumberInvalidError):
            return jsonify(status= False, message= f'Format nomor HP tidak valid'), 500
        elif isinstance(ex, FloodWaitError):
            return jsonify(status= False, message= f'Kode verifikasi OTP menunggu {ex.seconds} detik untuk pengiriman selanjutnya'), 500
        else:
            return jsonify(status= False, message= str(ex)), 500

@telegram_service_api.route('/otp-verification', methods= ['POST'])
async def auth_code():
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if 'user_id' not in request.json or ObjectId.is_valid(request.json['user_id']) is False:
        return jsonify(message= 'Object Id tidak valid'), 500

    user_id= request.json['user_id']
    phone= request.json['phone']
    phone_code_has= request.json['phone_code_hash']
    otp_code= request.json['otp_code']
    is_chat_emotions_exist= mongo.db.telegram_chat_emotions.find_one({ 'user_id': ObjectId(user_id), 'phone': phone })

    try:
        client= TelegramClient(f'{telegram_sessions_path}/phone_{phone}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)
        
        if client.is_connected() is False: 
            await client.connect()

        if not await client.is_user_authorized():
            await client.sign_in(phone, otp_code, phone_code_hash= phone_code_has)
            await client.disconnect()

            #mongo check phone exist
            if is_chat_emotions_exist is None:
                result= mongo.db.telegram_chat_emotions.insert_one({
                    'user_id': ObjectId(user_id),
                    'phone': phone,
                    'emotions': None
                })

                if result.inserted_id is None:
                    return jsonify(status= False, message= f'Terjadi kesalahan pada server, gagal login menggunakan Telegram dengan nomor {phone}'), 500

            return jsonify(status= True, verify_success= True, message= f'Berhasil melakukan login ke dalam Telegram dengan nomor {phone}')
        else:
            await client.disconnect()

            return jsonify(status= False, verify_success= False, message= f'Nomor {phone} sudah terverifikasi')
    except (PhoneCodeExpiredError, PhoneCodeInvalidError) as ex:
        await client.disconnect()

        if isinstance(ex, PhoneCodeExpiredError):
            return jsonify(status= False, message= 'Kode verifikasi OTP sudah tidak berlaku'), 500
        elif isinstance(ex, PhoneCodeInvalidError):
            return jsonify(status= False, message= 'Kode verifikasi OTP tidak valid'), 500
        else:
            return jsonify(status= False, message= str(ex)), 500

@telegram_service_api.route('/auth/logout', methods= ['POST'])
async def logout():
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if 'user_id' not in request.json or  ObjectId.is_valid(request.json['user_id']) is False:
        return jsonify(status= False, message= 'Object Id tidak valid'), 500

    user_id= request.json['user_id']

    is_chat_emotions_exist= mongo.db.telegram_chat_emotions.find_one({ 'user_id': ObjectId(user_id) })

    if is_chat_emotions_exist is None:
        return jsonify(status= False, is_authorized= False, message= 'Belum melakukan login ke dalam Telegram'), 401

    try:
        client= TelegramClient(f'{telegram_sessions_path}/phone_{is_chat_emotions_exist["phone"]}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)

        if client.is_connected() is False: 
            await client.connect()

        if await client.is_user_authorized() is True:
            await client.log_out()
            await client.disconnect()

            return jsonify(status= True, message= 'Berhasil melakukan logout dari Telegram')
        
        return jsonify(status= True, message= 'Pengguna belum melakukan login ke dalam Telegram')
    except Exception as ex:
        return jsonify(status= False, message= str(ex)), 500

@telegram_service_api.route('/chat-emotions/<user_id>')
async def get_chat_emotions(user_id):
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if ObjectId.is_valid(user_id) is False:
        return jsonify(message= 'Object Id tidak valid'), 500

    chat_emotions= mongo.db.telegram_chat_emotions.find_one({ 'user_id': ObjectId(user_id) })
    
    if chat_emotions is None:
        return jsonify(status= False, is_authorized= False, message= 'Belum melakukan login ke dalam Telegram')

    try:
        client= TelegramClient(f'{telegram_sessions_path}/phone_{chat_emotions["phone"]}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)

        if client.is_connected() is False: 
            await client.connect()

        if not await client.is_user_authorized():
            return jsonify(status= False, is_authorized= False, message= 'Belum melakukan login ke dalam Telegram')
        else:
            entities= await client.get_dialogs()
            messages= []

            for entity in entities:
                message_container= client.iter_messages(entity)

                async for message_object in message_container:
                    if message_object.out is True and message_object.message is not None and message_object.message != '':
                        chat_with= await client.get_entity(message_object.peer_id)
                        messages.append({
                            'chat_with': {
                                'user_id': chat_with.id,
                                'first_name': chat_with.first_name,
                                'phone': '+'+str(chat_with.phone)
                            },
                            'data': {
                                'message_id': message_object.id,
                                'text': message_object.message,
                                'timestamps': message_object.date, 
                                'is_out_message': message_object.out
                            },
                            'emotions': {}
                        })

            await client.disconnect()

            translator= Translator()
            for message in messages:
                translated= translator.translate(message['data']['text'], src= 'id')
                emotions= te.get_emotion(translated.text)
                message['emotions']= {
                    'angry': emotions['Angry'],
                    'fear': emotions['Fear'],
                    'happy': emotions['Happy'],
                    'sad': emotions['Sad'],
                    'surprise': emotions['Surprise'],
                }

            emotions_total= {
                'angry': 0,
                'fear': 0,
                'happy': 0,
                'sad': 0,
                'surprise': 0
            }
            for message in messages:
                for key in message['emotions']:
                    if message['emotions'][key] > 0: 
                        emotions_total[key]+= 1

            if chat_emotions['emotions'] != emotions_total:
                result= mongo.db.telegram_chat_emotions.find_one_and_update(
                    { 'user_id': ObjectId(user_id) },
                    { '$set': { 'emotions': dict(emotions_total) } }
                )
                
                if result is None:
                    return jsonify(status= False, message= 'Terjadi kesalahan pada server, gagal menyimpan data emosi teks pengguna'), 500
            
            return jsonify(
                status= True,
                chat_emotions= { 'emotions_total': emotions_total, 'messages': messages },
                message= 'Berhasil mendapatkan riwayat pesan telegram'
            )
    except (FloodWaitError, Exception) as ex:
        await client.disconnect()

        if isinstance(ex, FloodWaitError):
            return jsonify(status= False, message= f'Kode verifikasi OTP menunggu {ex.seconds} detik untuk pengiriman selanjutnya'), 500
        else:
            return jsonify(status= False, message= str(ex)), 500

#@telegram_api.route('/send-messages', methods= ['POST'])
#async def test_messages():
#    loop= asyncio.new_event_loop()
#    asyncio.set_event_loop(loop)
#    
#    sender_phone= request.form['sender_phone']
#    receiver_phone= request.form['receiver_phone']
#
#    try:
#        client= TelegramClient(f'{telegram_sessions_path}/phone_{sender_phone}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)
#
#        if client.is_connected() is False: 
#            await client.connect()
#        
#        entity= await client.get_entity(receiver_phone)
#
#        await client.send_message(entity, 'test pesan')
#        await client.disconnect()
#
#        return jsonify(message= 'Berhasil mengirimkan pesan ke nomor')
#    except Exception as ex: 
#        await client.disconnect()
#
#        return jsonify(message= ex)