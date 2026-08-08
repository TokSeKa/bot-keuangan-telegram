# IMPORT PYTHON
import requests
from requests import RequestException
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import json
from time import sleep

#Own function
from utils.gemini_conn import send_chat_llm, daftar_fungsi_penutup, get_uploaded_file_api
from utils.database import (
    insert_transaksi, search_transaksi_multi, insert_riwayat_percakapan, 
    edit_transaksi_by_id, delete_transaksi_by_id
)
from utils.telegram_function import (
    jawabanTelegramInsert, getUpdatesTelegramBerkala, konteksChatUserTelegram, 
    isPinnedMessage, jawaban_telegram, isGeminiLupaPenutup, jawabanTelegramEdit, 
    jawabanTelegramDelete, isHaveImageMessage, isHaveDocumentMessage,
    getGambarTelegram, isHaveManyImageMessage
)
# Memuat seluruh variabel .env 
load_dotenv()
telegram_bot_api = os.getenv("TELEGRAM_BOT_API_KEY")
url_telegram = f"https://api.telegram.org/bot{telegram_bot_api}"

# Fungsi global
update_id = None

# Main run
while True:
    try: # Setiap beberapa waktu, update dengan timeout 5 menit. Setiap kali berhasil, tetapkan offset agar pesan sebelumnya terhapus dari antrian.
        response = getUpdatesTelegramBerkala(url_telegram=url_telegram, update_id=update_id)
    except RequestException as e:
        print(f"Request error: {str(e).replace(telegram_bot_api, '***')}")
        sleep(10)
        continue
    print(response.json()) #DEBUG
    for item in response.json().get("result"):
        update_id = item.get("update_id")
    
    # continue #untuk cek json
    
    # Variabel sementara gambar
    media_group_id = gambar_upload_terbaru = file_id_gambar_terbaru = path_gambar_terbaru = None
    list_input = []
    
    if response.status_code == 200:
        try:
            data_result = response.json().get("result")
            for index, item in enumerate(data_result): # Result json itu isinya list dictionary || pake enumerate biar bisa ngintip item berikutnya, ngakalin gambar jamak yg gak tau kapan selesainya.
                # Check apa tipe pesannya:
                if "message" in item: # Jika pesan baru
                    if isPinnedMessage(item, "message"):# Pinned message, abaikan
                        update_id = item.get("update_id") # Ambil update_id terakhir
                        continue
                    # Jika ada banyak gambar maka lanjut
                    
                    if isHaveDocumentMessage(item, "message") or isHaveImageMessage(item, "message"):
                        if isHaveDocumentMessage(item, "message"): # kalau dokumen
                            mime_type = item.get("message").get('document').get('mime_type')
                            if(not mime_type.startswith("image/")): #cek bukan gambar
                                update_id = item.get("update_id") # Ambil update_id terakhir
                                response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Dokumen yang Kamu upload bukan gambar! Tolong hanya mengirim gambar kepada AI ya!"}) 
                                continue # skip karena bukan gambar
                            else:
                                file_id_gambar_terbaru = item.get("message").get("document").get("file_id")
                        elif isHaveImageMessage(item, "message"): # kalau gambar biasa
                            file_id_gambar_terbaru = item.get("message").get('photo')[-1]["file_id"]
                        
                        # Bagian masukkan ke input
                        uploaded_file = getGambarTelegram(url_telegram= f"https://api.telegram.org/bot{telegram_bot_api}", file_id_gambar=file_id_gambar_terbaru)
                        gambar_untuk_input_gemini = {"type": "image", "uri": uploaded_file.uri, "mime_type": uploaded_file.mime_type}
                        list_input.append(gambar_untuk_input_gemini) 
                        # cek caption, jika ada di append ke input
                        caption = item.get("message").get('caption')
                        if caption:
                            teks_caption_gambar = {"type": "text", "text": "Ini caption gambar: "+caption}
                            list_input.append(teks_caption_gambar)  
                            
                        if isHaveManyImageMessage(item, "message"): # Jika uploadnya jamak
                            # Jika gak ada gambar, simpan ke jangkar, add ke dalam list, dan cek apakah item berikutnya juga ada gambar, dan jika ada apakah gambarnya sama atau tidak.
                            if media_group_id is None: 
                                media_group_id = item.get("message").get('media_group_id') # Jika gambar pertama kali upload, simpan jangkarnya.
                                
                            # cek gambar berikutnya masih ada, dan group id nya masih sama, jika sama skip dan langsung ke gambar berikutnya aja
                            if index + 1 < len(data_result): # selama data masih ada kedepan
                                item_selanjutnya = data_result[index + 1] # cek data berikutnya
                                if (isHaveImageMessage(item_selanjutnya, "message") or isHaveDocumentMessage(item_selanjutnya, "message")) and (media_group_id == item_selanjutnya.get("message").get('media_group_id')):
                                    continue # skip semua, langsung lanjut berikutnya aja karena masih di satu upload yang sama        
                            
                    tanggal_input = datetime.fromtimestamp(item.get("message").get('date'), tz=timezone.utc)
                elif "edited_message" in item: # Rencana: Jika edit maka pindahkan ke konteks edit yang pernah ada
                    tanggal_input = datetime.fromtimestamp(item.get("edited_message").get('edit_date'), tz=timezone.utc)
                else:
                    print("Ini beda? coba cek") #DEBUG
                    continue # sementara belum tahu
                
                chat_id, text_user = konteksChatUserTelegram(item)
                list_input.append({"type": "text", "text": text_user})
                # print("PESAN KE LLM:\n"+text_user+"\n================================\n") #DEBUG
                # print("PESAN KE LLM:\n"+str(list_input)+"\n================================\n") #DEBUG
                
                try:
                    interaction = send_chat_llm(input_user=list_input) # Mengirim ke Gemini
                except Exception as e:
                    print(e)
                    update_id = item.get("update_id") # Ambil update_id terakhir
                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, AI sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                    continue
                for step in interaction.steps: # DEBUG
                    # 1. Print tipe step-nya dulu biar ketahuan ini step apa
                    print(f"Tipe Step: {step.type}")
                    
                    # 2. Kalau tipe step-nya adalah pemanggilan fungsi, baru kita print namanya
                    if step.type == "function_call":
                        print(f"-> Nama Fungsi : {step.name}")
                        print(f"-> Argumen     : {step.arguments}")
                    
                    print("-" * 30) # Cuma garis pemisah biar rapi di terminal
                
                chain_thought_llm = True
                kumpulan_hasil_fungsi = []
                response_telegram = "Mohon tunggu proses sedang berjalan dilatar belakang!"
                butuh_gemini = gemini_lupa_penutup_flag = False
                
                while chain_thought_llm:
                    if butuh_gemini:
                        butuh_gemini = False
                        try:
                            if gemini_lupa_penutup_flag:
                                gemini_lupa_penutup_flag = False
                                teks_lupa_penutup = "Kamu harus memakai fungsi penutup di akhir fungsi pararel!"
                                interaction = send_chat_llm(input_user=teks_lupa_penutup,interaction_id=interaction.id)
                            else:
                                interaction = send_chat_llm(input_user=kumpulan_hasil_fungsi,interaction_id=interaction.id)
                            for step in interaction.steps: #DEBUG
                                # 1. Print tipe step-nya dulu biar ketahuan ini step apa
                                print(f"2Tipe Step: {step.type}")
                                
                                # 2. Kalau tipe step-nya adalah pemanggilan fungsi, baru kita print namanya
                                if step.type == "function_call":
                                    print(f"-> 2Nama Fungsi : {step.name}")
                                    print(f"-> 2Argumen     : {step.arguments}")
                                
                                print("-" * 30) # Cuma garis pemisah biar rapi di terminal
                        except Exception as e:
                            print(e)
                            update_id = item.get("update_id") # Ambil update_id terakhir
                            response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, AI sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                            continue
                    
                    butuh_gemini = gemini_lupa_penutup_flag = isGeminiLupaPenutup(interaction=interaction, daftar_fungsi_penutup=daftar_fungsi_penutup)
                    if gemini_lupa_penutup_flag: continue
                        
                        
                    for step in interaction.steps: # KEKNYA GAK BOLEH PANGGIL DALAM FOR LOOP, BREAK LALU PANGGIL ULANG AJA DEH GEMIINYA
                        if step.type == "function_call":
                            # Bagian penutup
                            if (step.name == "llm_mendapatkan_konteks"):
                                butuh_gemini = True
                            elif (step.name == "proses_llm_selesai"):
                                chain_thought_llm = False
                                if response_telegram == "Mohon tunggu proses sedang berjalan dilatar belakang!":
                                    response_telegram = "Permintaan selesai diproses!"
                                else: continue # Gak perlu balas ke user
                            elif (step.name == "jawaban_telegram"):
                                response_telegram = jawaban_telegram(**step.arguments)
                                chain_thought_llm = False
                            # Bagian CRUDS database
                            elif (step.name == "insert_transaksi"):
                                try:
                                    response_insert = insert_transaksi(tanggal=tanggal_input, chat_id=chat_id, **step.arguments)
                                    kumpulan_hasil_fungsi.append(
                                        {
                                            "type": "function_result",
                                            "name": step.name,
                                            "call_id": step.id,
                                            "result": [{"type": "text", "text": json.dumps(response_insert, default=str)}],
                                        }
                                    )
                                    response_telegram = jawabanTelegramInsert(response_insert)
                                except Exception as e:
                                    print(e)   
                                    update_id = item.get("update_id") # Ambil update_id terakhir
                                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Database sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                                    continue
                            elif (step.name == "edit_transaksi_by_id"):
                                try:
                                    response_edit_data_sebelum, response_edit_data_setelah = edit_transaksi_by_id(chat_id=chat_id, **step.arguments)
                                    kumpulan_hasil_fungsi.append(
                                        {
                                            "type": "function_result",
                                            "name": step.name,
                                            "call_id": step.id,
                                            "result": [{"type": "text", "text_data_sebelum": json.dumps(response_edit_data_sebelum, default=str)}, {"type": "text", "text_data_sesudah": json.dumps(response_edit_data_setelah, default=str)}],
                                        }
                                    )
                                    response_telegram = jawabanTelegramEdit(response_edit_data_sebelum, response_edit_data_setelah)
                                except Exception as e:
                                    print(e)   
                                    update_id = item.get("update_id") # Ambil update_id terakhir
                                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Database sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                                    continue
                            elif (step.name == "delete_transaksi_by_id"):
                                try:
                                    response_delete_data = delete_transaksi_by_id(chat_id=chat_id, **step.arguments)
                                    kumpulan_hasil_fungsi.append(
                                        {
                                            "type": "function_result",
                                            "name": step.name,
                                            "call_id": step.id,
                                            "result": [{"type": "text", "text_data_sesudah": json.dumps(response_delete_data, default=str)}],
                                        }
                                    )
                                    response_telegram = jawabanTelegramDelete(response_delete_data)
                                except Exception as e:
                                    print(e)   
                                    update_id = item.get("update_id") # Ambil update_id terakhir
                                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Database sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                                    continue
                            elif (step.name == "search_transaksi_multi"):
                                try:
                                    hasil_transaksi = search_transaksi_multi(chat_id=chat_id, **step.arguments)
                                    print("\n========================================\nHASIL SQL: "+json.dumps(hasil_transaksi, default=str)+"\n========================================\n")
                                    kumpulan_hasil_fungsi.append(
                                        {
                                            "type": "function_result",
                                            "name": step.name,
                                            "call_id": step.id,
                                            "result": [{"type": "text", "text": json.dumps(hasil_transaksi, default=str)}],
                                        }
                                    )
                                    continue # Gak perlu balas ke user
                                except Exception as e:
                                    print(e)   
                                    update_id = item.get("update_id") # Ambil update_id terakhir
                                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Database sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                                    continue
                            
                            response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":response_telegram}) # kirimkan pesan kepada user     
                            if response_chat.status_code == 200: # KEKNYA BAKAL TETAP KE SKIP DEH WALAU ERROR ATAU GMN2?? CASE: JIKA DATA MASUK PUN DAN TELE ERROR, DIA BAKAL TETAP MAJU ANYWAY
                                insert_riwayat_percakapan(chat_id=chat_id,identitas="Bot", tanggal=tanggal_input, pesan=response_telegram, catatan=None, conn=None)
                                update_id = item.get("update_id") # Ambil update_id terakhir
                            else: # ini harusnya kalau bisa transaksi terakhir dibatalin somehow, # TODO future.
                                sleep(10)
                                break
                        
        except Exception as e:
            print(e)
            sleep(10)
            continue
    else:
        sleep(30)

