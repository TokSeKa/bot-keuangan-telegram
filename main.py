# IMPORT PYTHON
import requests
from requests import RequestException
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import zoneinfo
from time import sleep

#Own function
from database import insert_transaksi
from gemini_conn import send_chat_llm

# Memuat seluruh variabel .env 
load_dotenv()
telegram_bot_api = os.getenv("TELEGRAM_BOT_API_KEY")
gemini_api = os.getenv("GEMINI_API_KEY")
url_telegram = f"https://api.telegram.org/bot{telegram_bot_api}"

# Fungsi global
update_id = None

# Main run
while True:
    try:
        if update_id:
            response = requests.get(url = url_telegram+"/getUpdates", params={"timeout":300, "offset":update_id+1})
        else:
            response = requests.get(url = url_telegram+"/getUpdates", params={"timeout":300})
    except RequestException as e:
        print(f"Request error: {e}")
        sleep(10)
        continue
    
    match response.status_code:
        case 200:
            try:
                for item in response.json().get("result"): # Untuk setiap pesan
                    tipe_konteks_chat = "Ini adalah " 
                    tanggal_edit = None
                    # Check apa tipe pesannya:
                    if "message" in item:
                        type_chat = "message"
                        tanggal_input = datetime.fromtimestamp(item.get(type_chat).get('date'), tz=timezone.utc)
                        tipe_konteks_chat = tipe_konteks_chat + f"Pesan baru dari User dengan tanggal input {tanggal_input}"
                    elif "edited_message" in item: # Rencana: Jika edit maka pindahkan ke konteks edit yang pernah ada
                        type_chat = "edited_message"
                        tanggal_input = datetime.fromtimestamp(item.get(type_chat).get('date'), tz=timezone.utc)
                        tanggal_edit = datetime.fromtimestamp(item.get(type_chat).get('edit_date'), tz=timezone.utc)
                        tipe_konteks_chat = tipe_konteks_chat + f"Pesan lama yang di edit User dengan tanggal input {tanggal_input}, dan tanggal edit {tanggal_edit} "
                    else:
                        continue # sementara belum tahu
                    
                    chat_id = item.get(type_chat).get('chat').get("id") # Ambil id chat user
                    text_user = tipe_konteks_chat+"\nBerikut pesan user: "+ item.get(type_chat).get('text', "User tidak mengirimkan text") #Bisa aja kirim gambar doang
                    
                    try:
                        response_gemini = send_chat_llm(input_user=text_user) # Mengirim ke Gemini
                    except Exception as e:
                        print(type(e).__mro__)
                        update_id = item.get("update_id") # Ambil update_id terakhir
                        response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, AI sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                        continue
                    
                    # Insert transaksi
                    if (response_gemini.fungsi == "Pencatatan"):
                        try:
                            response_insert = insert_transaksi(nama=response_gemini.nama, 
                                                                    nominal=response_gemini.nominal, 
                                                                    catatan=response_gemini.catatan, 
                                                                    kategori=response_gemini.kategori,
                                                                    tanggal=tanggal_input, 
                                                                    tipe=response_gemini.tipe, 
                                                                    chat_id=chat_id)
                            # Khusus tanggal di ubah ke WIB
                            response_waktu_balasan = response_insert['tanggal'].astimezone(zoneinfo.ZoneInfo("Asia/Jakarta")).strftime("%d %B %Y, %H:%M WIB")
                            response_insert_telegram = f"{response_insert['nama']} dengan nominal Rp.{response_insert['nominal']} telah tercatat!\nKategori: {response_insert['kategori']}\nWaktu: {response_waktu_balasan} \nTipe: {response_insert['tipe']}"
                        except Exception as e:
                            print(type(e).__mro__)   
                            update_id = item.get("update_id") # Ambil update_id terakhir
                            response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Database sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                            continue
                    else:
                        response_insert_telegram = "Maaf, tampaknya pesan Anda tidak dapat diproses, silakan mencoba pesan lain!"
                    
                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":response_insert_telegram}) # kirimkan pesan kepada user     
                    if response_chat.status_code == 200:
                        update_id = item.get("update_id") # Ambil update_id terakhir
                    else: 
                        sleep(10)
                        break
            except Exception as e:
                print(type(e).__mro__)
                sleep(10)
                continue
        case _:
            sleep(30)
