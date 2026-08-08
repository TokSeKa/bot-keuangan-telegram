# IMPORT PYTHON
import requests
from requests import RequestException
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import json
from time import sleep

#Own function
from utils.database import insert_transaksi, search_transaksi_multi, insert_riwayat_percakapan, edit_transaksi_by_id, delete_transaksi_by_id
from utils.gemini_conn import send_chat_llm, daftar_fungsi_penutup
from utils.telegram_function import jawabanTelegramInsert, getUpdatesTelegramBerkala, konteksChatUserTelegram, isPinnedMessage, jawaban_telegram, isGeminiLupaPenutup, jawabanTelegramEdit, jawabanTelegramDelete

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
    # Jika telegram response 200/sucess
    if response.status_code == 200:
        try:
            for item in response.json().get("result"): # Result json itu isinya list dictionary
                # type_chat = tanggal_input = tanggal_edit = None
                # Check apa tipe pesannya:
                if "message" in item: # Jika pesan baru
                    if isPinnedMessage(item, "message"):# Pinned message, abaikan
                        update_id = item.get("update_id") # Ambil update_id terakhir
                        continue
                    tanggal_input = datetime.fromtimestamp(item.get("message").get('date'), tz=timezone.utc)
                elif "edited_message" in item: # Rencana: Jika edit maka pindahkan ke konteks edit yang pernah ada
                    tanggal_input = datetime.fromtimestamp(item.get("edited_message").get('edit_date'), tz=timezone.utc)
                else:
                    print("Ini beda? coba cek") #DEBUG
                    continue # sementara belum tahu
                
                chat_id, text_user = konteksChatUserTelegram(item)
                print("PESAN KE LLM:\n"+text_user+"\n================================\n") #DEBUG
                
                try:
                    interaction = send_chat_llm(input_user=text_user) # Mengirim ke Gemini
                except Exception as e:
                    print(e)
                    update_id = item.get("update_id") # Ambil update_id terakhir
                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, AI sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                    continue
                for step in interaction.steps:
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

