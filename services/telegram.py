import os, asyncio
from flask import Blueprint, request, jsonify
from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError, PhoneCodeExpiredError, PhoneCodeInvalidError, FloodWaitError
from bson.objectid import ObjectId

from utilities.helpers import telegram_sessions_path
from extensions import mongo

telegram_api= Blueprint('telegram_api', __name__)

@telegram_api.route('/auth', methods= ['POST'])
async def auth_phone():
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    #mongo check phone exist
    if 'user_id' not in request.json or ObjectId.is_valid(request.json['user_id']) is False:
        return jsonify(message= 'Object Id tidak valid'), 500
    
    user_id= request.json['user_id']
    phone= request.json['phone']
    is_phone_exist= mongo.db.telegram_chat_emotions.find_one({ 'user_id': ObjectId(user_id), 'phone': phone })        

    if is_phone_exist is None:
        result= mongo.db.telegram_chat_emotions.insert_one({
            'user_id': ObjectId(user_id),
            'phone': phone,
            'emotions': {
                'happy': [],
                'sad': [],
                'angry': [],
                'fear': []
            }
        })

        if result.inserted_id is None:
            return jsonify(message= f'Terjadi kesalahan pada server, gagak login menggunakan Telegram dengan nomor {phone}'), 500

    #telegram auth
    try:
        client= TelegramClient(f'{telegram_sessions_path}/phone_{phone}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)
        
        if client.is_connected() is False: 
            await client.connect()

        if not await client.is_user_authorized():
            code= await client.send_code_request(phone, force_sms= True)
            await client.disconnect()

            return jsonify(phone_code_hash= code.phone_code_hash, message= f'Berhasil mengirimkan kode OTP verifikasi ke nomor {phone}')
        else:
            user= await client.get_me() 
            await client.disconnect()

            return jsonify(
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
            return jsonify(message= f'Format nomor HP tidak valid'), 500
        elif isinstance(ex, FloodWaitError):
            return jsonify(message= f'Kode verifikasi OTP menunggu {ex.seconds} detik untuk pengiriman selanjutnya'), 500

@telegram_api.route('/otp-verification', methods= ['POST'])
async def auth_code():
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if 'user_id' not in request.json or ObjectId.is_valid(request.json['user_id']) is False:
        return jsonify(message= 'Object Id tidak valid'), 500

    user_id= request.json['user_id']
    otp_code= request.json['otp_code']
    phone_code_has= request.json['phone_code_hash']
    is_chat_emotions_exist= mongo.db.telegram_chat_emotions.find_one({ 'user_id': ObjectId(user_id) })

    if is_chat_emotions_exist is None:
        return jsonify(is_authorized= False, message= 'Belum melakukan login ke dalam Telegram'), 401

    try:
        client= TelegramClient(f'{telegram_sessions_path}/phone_{is_chat_emotions_exist["phone"]}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)
        
        if client.is_connected() is False: 
            await client.connect()

        if not await client.is_user_authorized():
            await client.sign_in(is_chat_emotions_exist['phone'], otp_code, phone_code_hash= phone_code_has)
            await client.disconnect()

            return jsonify(verify_success= True, message= f'Berhasil melakukan login ke dalam Telegram dengan nomor {is_chat_emotions_exist["phone"]}')
        else:
            await client.disconnect()

            return jsonify(verify_success= False, message= f'Nomor {is_chat_emotions_exist["phone"]} sudah terverifikasi')
    except (PhoneCodeExpiredError, PhoneCodeInvalidError) as ex:
        await client.disconnect()

        if isinstance(ex, PhoneCodeExpiredError):
            return jsonify(message= 'Kode verifikasi OTP sudah tidak berlaku'), 500
        elif isinstance(ex, PhoneCodeInvalidError):
            return jsonify(message= 'Kode verifikasi OTP tidak valid'), 500

@telegram_api.route('/auth/logout', methods= ['POST'])
async def logout():
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if 'user_id' not in request.json or  ObjectId.is_valid(request.json['user_id']) is False:
        return jsonify(message= 'Object Id tidak valid'), 500

    user_id= request.json['user_id']

    is_chat_emotions_exist= mongo.db.telegram_chat_emotions.find_one({ 'user_id': ObjectId(user_id) })

    if is_chat_emotions_exist is None:
        return jsonify(is_authorized= False, message= 'Belum melakukan login ke dalam Telegram'), 401

    try:
        client= TelegramClient(f'{telegram_sessions_path}/phone_{is_chat_emotions_exist["phone"]}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)

        if client.is_connected() is False: 
            await client.connect()

        if await client.is_user_authorized() is True:
            await client.log_out()
            await client.disconnect()

            return jsonify(message= 'Berhasil melakukan logout dari Telegram')
        
        return jsonify(message= 'Pengguna belum melakukan login ke dalam Telegram')
    except Exception as ex:
        return jsonify(message= ex)

@telegram_api.route('/chat-emotions/<user_id>')
async def get_messages(user_id):
    loop= asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    if ObjectId.is_valid(user_id) is False:
        return jsonify(message= 'Object Id tidak valid'), 500

    is_chat_emotions_exist= mongo.db.telegram_chat_emotions.find_one({ 'user_id': ObjectId(user_id) })
    
    if is_chat_emotions_exist is None:
        return jsonify(is_authorized= False, message= 'Belum melakukan login ke dalam Telegram')

    try:
        client= TelegramClient(f'{telegram_sessions_path}/phone_{is_chat_emotions_exist["phone"]}.session', os.environ.get('TELEGRAM_API_ID'), os.environ.get('TELEGRAM_API_HASH'), loop= loop)

        if client.is_connected() is False: 
            await client.connect()

        if not await client.is_user_authorized():
            return jsonify(is_authorized= False, message= 'Belum melakukan login ke dalam Telegram')
        else:
            entities= await client.get_dialogs(limit= 100)
            messages= []

            for entity in entities:
                message_objects= await client.get_messages(entity, limit= 100)

                for message in message_objects:
                    messages.append(message.message)

            await client.disconnect()
            
            return jsonify(
                chat_emotions= is_chat_emotions_exist['emotions'], 
                message= 'Berhasil mendapatkan riwayat pesan telegram'
            )
    except (FloodWaitError, Exception) as ex:
        await client.disconnect()

        if isinstance(ex, FloodWaitError):
            return jsonify(message= f'Kode verifikasi OTP menunggu {ex.seconds} detik untuk pengiriman selanjutnya')
        else:
            return jsonify(message= ex)

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