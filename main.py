# IMPORT PYTHON
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
import json, os, random
from time import sleep

#Own function
from utils.gemini_conn import send_chat_llm, daftar_fungsi_penutup
from utils.database import (
    insert_transaksi, search_transaksi_multi, insert_riwayat_percakapan, 
    edit_transaksi_by_id, delete_transaksi_by_id
)
from utils.telegram_function import (
    jawabanTelegramInsert, getUpdatesTelegramBerkala, konteksChatUserTelegram, 
    isPinnedMessage, jawaban_telegram, isGeminiLupaPenutup, jawabanTelegramEdit, 
    jawabanTelegramDelete, isAnyFile,
    getMediaTelegram, isHaveManyFileMessage
)
# Memuat seluruh variabel .env 
load_dotenv()
telegram_bot_api = os.getenv("TELEGRAM_BOT_API_KEY")
url_telegram = f"https://api.telegram.org/bot{telegram_bot_api}"

# Fungsi global
update_id = None

# Text loading
loading_text = [
  "Tunggu sebentar ya...", "Beri aku waktu sejenak...", "Sedang membuka catatanmu...", "Mencari jawaban yang pas...", "Sebentar, lagi disiapkan...", "Sabar ya, hampir selesai...", "Sedang memastikan semuanya beres...",
  "Tunggu ya, lagi aku urus...", "Sebentar ya! lagi ku proses!", "bentar yah :3", "okeh! sebentar boss!", "sabar~ lagi diproses!", "santai, aku kerjain!", "jangan buru-buru, aku kerjain kok!",
  "sabar bos! on the way!", "huft huft huft!", "eh, kerja?, oke bentar!", "5 men-, eh~ canda~, bentar ya!", "hmmm, bentar... ini menarik...", "kalau kamu gak buru buru bisa tinggalin aku kok, aku lagi proses~", "aku lagi proses~ nanti ku chat ya~",
  "yeay~ kerja! OTW!", "kamu nyuruh aku kerja? baiklah...", "kerja! kerja! kerja!", "hosh..hosh..hosh.. bentar ya!", "sat sit sut, aku siap bantu! mohon ditunggu!", "haittt! shap! otw kerjain requestmu!", "dua tiga, aku kerja~",
  "OTW (gak 5 menit kok!)", "trust me, its working behind~", "eh eh? bentar ya~ aku kerjain~", "Hoammmm... iyaaaa bentar yaaaa", "Okeh, sebentar bos..."
]

# Main run
while True:
    try: # Setiap beberapa waktu, update dengan timeout 5 menit. Setiap kali berhasil, tetapkan offset agar pesan sebelumnya terhapus dari antrian.
        response = getUpdatesTelegramBerkala(url_telegram=url_telegram, update_id=update_id)
    except requests.RequestException as e:
        print(f"Request error: {str(e).replace(telegram_bot_api, '***')}")
        sleep(10)
        continue
    print(response.json()) #DEBUG
    # for item in response.json().get("result"):
    #     update_id = item.get("update_id")
    
    # continue #untuk cek json DEBUG
    
    # Variabel sementara gambar
    media_group_id = file_id_media_terbaru = text_user = caption = None
    list_input = []
    
    if response.status_code == 200:
        try:
            data_result = response.json().get("result")
            for index, item in enumerate(data_result): # Result json itu isinya list dictionary || pake enumerate biar bisa ngintip item berikutnya, ngakalin gambar jamak yg gak tau kapan selesainya.
                # Check apa tipe pesannya:
                if "message" in item: # Jika pesan baru
                    type_chat = "message"
                    if isPinnedMessage(item, "message"):# Pinned message, abaikan
                        update_id = item.get("update_id") # Ambil update_id terakhir
                        continue
                    tanggal_input = datetime.fromtimestamp(item.get("message").get('date'), tz=timezone.utc)
                elif "edited_message" in item: # Rencana: Jika edit maka pindahkan ke konteks edit yang pernah ada
                    tanggal_input = datetime.fromtimestamp(item.get("edited_message").get('edit_date'), tz=timezone.utc)
                else:
                    print("Ini beda? coba cek") #DEBUG
                    continue # sementara belum tahu
                
                # Bagian masukkan media ke input
                if(isAnyFile(item=item, type_chat=type_chat)):
                    uploaded_file = getMediaTelegram(item=item, type_chat=type_chat, url_telegram= f"https://api.telegram.org/bot{telegram_bot_api}")
                    if uploaded_file is not None: 
                        if isinstance(uploaded_file, str):
                            requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":uploaded_file}) 
                        else:
                            gambar_untuk_input_gemini = uploaded_file
                            list_input.append(gambar_untuk_input_gemini)
                            
                        # cek caption. kalau ada, masuk var, nanti passing ke konteks Chat, sebagai pengganti text;
                        caption = item.get(type_chat).get('caption') or caption
                        
                        if isHaveManyFileMessage(item=item, type_chat=type_chat): # Jika uploadnya jamak
                            # Jika gak ada gambar, simpan ke jangkar, add ke dalam list, dan cek apakah item berikutnya juga ada gambar, dan jika ada apakah gambarnya sama atau tidak.
                            if media_group_id is None: 
                                media_group_id = item.get(type_chat).get('media_group_id') # Jika gambar pertama kali upload, simpan jangkarnya.
                                
                            # cek gambar berikutnya masih ada, dan group id nya masih sama, jika sama skip dan langsung ke gambar berikutnya aja
                            if index + 1 < len(data_result): # selama data masih ada kedepan
                                item_selanjutnya = data_result[index + 1] # cek data berikutnya
                                if (isAnyFile(item_selanjutnya, type_chat)):
                                    continue # skip semua, langsung lanjut berikutnya aja karena masih di satu upload yang sama     
                
                chat_id, text_user = konteksChatUserTelegram(item=item, caption=caption)
                list_input.append({"type": "text", "text": text_user})
                print("PESAN KE LLM:\n"+text_user+"\n================================\n") #DEBUG
                # print("PESAN KE LLM:\n"+str(list_input)+"\n================================\n") #DEBUG
                
                text_user = caption = None # asumsikan dalam satu loop udah beda user, mending reset setelah pakai;
                try:
                    interaction = send_chat_llm(input_user=list_input) # Mengirim ke Gemini
                    # Mengakses data penggunaan token dari response DEBUG
                    print("\n=====================================================")
                    print("Token Input:", interaction.usage.total_input_tokens)
                    print("Token Output:", interaction.usage.total_output_tokens)
                    print("Total keseluruhan token:", interaction.usage.total_tokens)
                    print("\n=====================================================")
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
                response_telegram = random.choice(loading_text)
                butuh_gemini = gemini_lupa_penutup_flag = False
                
                while chain_thought_llm:
                    if butuh_gemini:
                        butuh_gemini = False
                        try:
                            if gemini_lupa_penutup_flag:
                                gemini_lupa_penutup_flag = False
                                teks_lupa_penutup = "Kamu harus memakai fungsi penutup di akhir fungsi pararel! JIKA KAMU DIBERIKAN PESAAN INI, BERARTI FUNGSI SEBELUMNYA BELUM DI PROSES, ULANGI KEMBALI!"
                                interaction = send_chat_llm(input_user=teks_lupa_penutup,interaction_id=interaction.id)
                                # Mengakses data penggunaan token dari response DEBUG
                                print("\n=====================================================")
                                print("Token Input:", interaction.usage.total_input_tokens)
                                print("Token Output:", interaction.usage.total_output_tokens)
                                print("Total keseluruhan token:", interaction.usage.total_tokens)
                                print("\n=====================================================")
                            else:
                                interaction = send_chat_llm(input_user=kumpulan_hasil_fungsi,interaction_id=interaction.id)
                                # Mengakses data penggunaan token dari response DEBUG
                                print("\n=====================================================")
                                print("Token Input:", interaction.usage.total_input_tokens)
                                print("Token Output:", interaction.usage.total_output_tokens)
                                print("Total keseluruhan token:", interaction.usage.total_tokens)
                                print("\n=====================================================")
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
                                if response_telegram == random.choice(loading_text):
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
                                print("\n:masuk ke riwayat\n:")
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

