# IMPORT PYTHON
import requests
from requests import RequestException
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import zoneinfo
from time import sleep

#Own function
from utils.database import insert_transaksi, search_transaksi_multi
from utils.gemini_conn import send_chat_llm
from utils.telegram_function import jawabanTelegramInsert, getUpdatesTelegramBerkala, konteksChatUserTelegram, isPinnedMessage, jawaban_telegram_penolakan

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
                type_chat = tanggal_input = tanggal_edit = None
                # Check apa tipe pesannya:
                if "message" in item: # Jika pesan baru
                    type_chat = "message"
                    # Kasus : Pinned message
                    if isPinnedMessage(item, type_chat):
                        # Pinned message, abaikan
                        update_id = item.get("update_id") # Ambil update_id terakhir
                        continue
                    tanggal_input = datetime.fromtimestamp(item.get(type_chat).get('date'), tz=timezone.utc)
                elif "edited_message" in item: # Rencana: Jika edit maka pindahkan ke konteks edit yang pernah ada
                    type_chat = "edited_message"
                    tanggal_input = datetime.fromtimestamp(item.get(type_chat).get('date'), tz=timezone.utc)
                    tanggal_edit = datetime.fromtimestamp(item.get(type_chat).get('edit_date'), tz=timezone.utc)
                else:
                    print("Ini beda? coba cek") #DEBUG
                    continue # sementara belum tahu
                
                # Pengecekan 
                # Bagian mengambil informasi siapa user
                chat_id = item.get(type_chat).get('chat').get("id") # Ambil id chat user
                chat_text = item.get(type_chat).get('text', "User tidak mengirimkan text")
                
                text_user = konteksChatUserTelegram(type_chat=type_chat, tanggal_input=tanggal_input, tanggal_edit=tanggal_edit, chat_id=chat_id, text_user=chat_text)
                print("PESAN KE USER\n"+text_user+"\nDone\n") #DEBUG
                
                
                # Mengirim promt user ke LLM : gemini
                try:
                    response_gemini = send_chat_llm(input_user=text_user) # Mengirim ke Gemini
                except Exception as e:
                    print(e)
                    update_id = item.get("update_id") # Ambil update_id terakhir
                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, AI sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                    continue
                
                for step in response_gemini:
                    if step.type == "function_call":
                        # Insert transaksi
                        if (step.name == "insert_transaksi"):
                            try:
                                response_insert = insert_transaksi(tanggal=tanggal_input, chat_id=chat_id, **step.arguments)
                                response_insert_telegram = jawabanTelegramInsert(response_insert)
                            except Exception as e:
                                print(e)   
                                update_id = item.get("update_id") # Ambil update_id terakhir
                                response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Database sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                                continue
                            print(f"Function to call: {step.name}")
                            print(f"Arguments: {step.arguments}")
                        if (step.name == "search_transaksi_multi"):
                            try:
                                hasil_transaksi = search_transaksi_multi(chat_id=chat_id, **step.arguments)
                                response_insert_telegram = "\n".join([str(row) for row in hasil_transaksi]) # Tes keluarin dulu, nanti rencananya bisa pakai untuk search.
                            except Exception as e:
                                print(e)   
                                update_id = item.get("update_id") # Ambil update_id terakhir
                                response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Database sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                                continue
                            print(f"Function to call: {step.name}")
                            print(f"Arguments: {step.arguments}")
                        elif (step.name == "jawaban_telegram_penolakan"):
                            response_insert_telegram = jawaban_telegram_penolakan(**step.arguments)
                        
                        response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":response_insert_telegram}) # kirimkan pesan kepada user     
                        if response_chat.status_code == 200: # KEKNYA BAKAL TETAP KE SKIP DEH WALAU ERROR ATAU GMN2?? CASE: JIKA DATA MASUK PUN DAN TELE ERROR, DIA BAKAL TETAP MAJU ANYWAY
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

