# IMPORT PYTHON
import requests
from requests import RequestException
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import zoneinfo
from time import sleep

#Own function
from utils.database import insert_transaksi, select_transaksi
from utils.gemini_conn import send_chat_llm

# Memuat seluruh variabel .env 
load_dotenv()
telegram_bot_api = os.getenv("TELEGRAM_BOT_API_KEY")
url_telegram = f"https://api.telegram.org/bot{telegram_bot_api}"

# Fungsi global
update_id = None

def isPinnedMessage(item, type_chat): # Mengembalikan True jika ada kunci 'pinned_message', False jika tidak ada
    return bool(item.get(type_chat, {}).get('pinned_message'))

def getUpdatesTelegramBerkala (update_id=None):
    if update_id:
        return requests.get(url = url_telegram+"/getUpdates", params={"timeout":300, "offset":update_id+1})
    else:
        return requests.get(url = url_telegram+"/getUpdates", params={"timeout":300})

def konteksChatUserTelegram(tanggal_input, text_user, chat_id=None, tanggal_edit=None):
    if tanggal_input and tanggal_edit:
        konteks_transaksi_edit = ""
        transaksi_lama = select_transaksi(tanggal_input, chat_id)
        for tl in transaksi_lama:
            konteks_transaksi_edit = konteks_transaksi_edit + f"""Nama: {tl['nama']}
Nominal: Rp.{tl['nominal']}
Kategori: {tl['kategori']}
Waktu: {tl['tanggal']} 
Tipe: {tl['tipe']}
next transaction\n"""
        
        print("\nINI ADALAH HASIL SELECT:")
        print(transaksi_lama) #DEBUG
        tipe_konteks_chat = "User melakukan edit pesan dan Ini adalah transaksi lama user berdasarkan timestamp user:\n" + konteks_transaksi_edit + f"\nIni adalah Pesan lama yang di edit User dengan tanggal input {tanggal_input}, dan tanggal edit {tanggal_edit}."
    elif tanggal_input:
        tipe_konteks_chat = f"Ini adalah Pesan baru dari User dengan tanggal input {tanggal_input}."
    return tipe_konteks_chat+"\nBerikut pesan user: "+ text_user # Ambil teks user / user tidak mengirimkan text
        
def jawabanTelegramInsert(response_insert):
    response_waktu_balasan = response_insert['tanggal'].astimezone(zoneinfo.ZoneInfo("Asia/Jakarta")).strftime("%d %B %Y, %H:%M WIB")
    return f"""Telah tercatat!
Nama: {response_insert['nama']}
Nominal: Rp.{response_insert['nominal']}
Kategori: {response_insert['kategori']}
Waktu: {response_waktu_balasan} 
Tipe: {response_insert['tipe']}"""
        
# Main run
while True:
    try: # Setiap beberapa waktu, update dengan timeout 5 menit. Setiap kali berhasil, tetapkan offset agar pesan sebelumnya terhapus dari antrian.
        response = getUpdatesTelegramBerkala(update_id)
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
                text_user = konteksChatUserTelegram(tanggal_input=tanggal_input, tanggal_edit=tanggal_edit, chat_id=chat_id, text_user=item.get(type_chat).get('text', "User tidak mengirimkan text"))
                print("PESAN KE USER\n"+text_user+"\nDone\n") #DEBUG
                # Mengirim promt user ke LLM : gemini
                try:
                    response_gemini = send_chat_llm(input_user=text_user) # Mengirim ke Gemini
                except Exception as e:
                    print(e)
                    update_id = item.get("update_id") # Ambil update_id terakhir
                    response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, AI sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                    continue
                print("Respon gemini: " + response_gemini.fungsi ) #DEBUG
                # Insert transaksi
                if (response_gemini.fungsi == "Pencatatan"):
                    try:
                        response_insert = insert_transaksi(nama=response_gemini.nama, nominal=response_gemini.nominal, catatan=response_gemini.catatan, kategori=response_gemini.kategori, tanggal=tanggal_input, tipe=response_gemini.tipe, chat_id=chat_id)
                        # Khusus tanggal di ubah ke WIB
                        print(response_insert) #DEBUG
                        response_insert_telegram = jawabanTelegramInsert(response_insert)
                    except Exception as e:
                        print(e)   
                        update_id = item.get("update_id") # Ambil update_id terakhir
                        response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":"Maaf, Database sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                        continue
                    
                # TODO : BIKIN EDITED MESSAGE DENGAN SISTEM : KALAU DETEKSI EDIT, MAKA CARI DULU DATANYA TRANSAKSI SEBAGAI KONTEKS TAMBAHAN KE GEMINI; JIKA ADA MAKA KIRIMKAN; JIKA GAK ADA MAKA BILANG AJA GAKA ADA; JIKA ADA MAKA KIRIMKAN APA ISINYA;
                elif response_gemini.fungsi == "Perubahan":
                    response_insert_telegram = response_gemini.response
                elif response_gemini.fungsi == "Penolakan":
                    response_insert_telegram = response_gemini.response
                else:
                    response_insert_telegram = "Maaf Permintaan Anda belum dapat dilakukan!"
                
                # Memberikan respon akhir ke user dari telegram
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

