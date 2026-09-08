import os
import json
import random
import requests
from time import sleep
from datetime import datetime, timezone
from dotenv import load_dotenv

from utils.gemini_conn import send_chat_llm
from utils.database import (
    insert_transaksi, search_transaksi_multi, insert_riwayat_percakapan, 
    edit_transaksi_by_id, delete_transaksi_by_id
)
from utils.telegram_function import (
    jawabanTelegramInsert, getUpdatesTelegramBerkala, konteksChatUserTelegram, 
    isPinnedMessage, jawaban_telegram, jawabanTelegramEdit, jawabanTelegramSearch,
    jawabanTelegramDelete, isAnyFile, getMediaTelegram, isHaveManyFileMessage
)

load_dotenv()
telegram_bot_api = os.getenv("TELEGRAM_BOT_API_KEY")
url_telegram = f"https://api.telegram.org/bot{telegram_bot_api}"

update_id = None
loading_text = [
    "Tunggu sebentar ya...", "Beri aku waktu sejenak...", "Sedang membuka catatanmu...", 
    "Mencari jawaban yang pas...", "Sebentar, lagi disiapkan...", "Sabar ya, hampir selesai...", 
    "Sedang memastikan semuanya beres...", "Tunggu ya, lagi aku urus...", 
    "Sebentar ya! lagi ku proses!", "bentar yah :3", "okeh! sebentar boss!", 
    "sabar~ lagi diproses!", "santai, aku kerjain!", "jangan buru-buru, aku kerjain kok!",
    "sabar bos! on the way!", "huft huft huft!", "eh, kerja?, oke bentar!", 
    "5 men-, eh~ canda~, bentar ya!", "hmmm, bentar... ini menarik...", 
    "kalau kamu gak buru buru bisa tinggalin aku kok, aku lagi proses~", 
    "aku lagi proses~ nanti ku chat ya~", "yeay~ kerja! OTW!", 
    "kamu nyuruh aku kerja? baiklah...", "kerja! kerja! kerja!", "hosh..hosh..hosh.. bentar ya!", 
    "sat sit sut, aku siap bantu! mohon ditunggu!", "haittt! shap! otw kerjain requestmu!", 
    "dua tiga, aku kerja~", "OTW (gak 5 menit kok!)", "trust me, its working behind~", 
    "eh eh? bentar ya~ aku kerjain~", "Hoammmm... iyaaaa bentar yaaaa", "Okeh, sebentar bos..."
]

while True:
    try:
        response = getUpdatesTelegramBerkala(url_telegram=url_telegram, update_id=update_id)
    except requests.RequestException:
        sleep(10)
        continue

    if response.status_code != 200:
        sleep(30)
        continue
    
    try:        
        data_result = response.json().get("result", [])
        
        # cek setiap item yang di fetch dari telegram
        for index, item in enumerate(data_result):
            update_id = item.get("update_id") # TODO: Webhook harusnya gak perlu update id begini, nanti cek fast API
            media_group_id = None
            caption = None
            list_input = []
            
            if "message" in item:
                type_chat = "message" 
                if isPinnedMessage(item, type_chat):
                    continue
                tanggal_input = datetime.fromtimestamp(item.get(type_chat).get('date'), tz=timezone.utc)
            elif "edited_message" in item:
                type_chat = "edited_message"
                tanggal_input = datetime.fromtimestamp(item.get(type_chat).get('edit_date'), tz=timezone.utc)
            else:
                continue
                
            chat_id = item.get(type_chat).get("chat").get("id")

            if isAnyFile(item=item, type_chat=type_chat):
                uploaded_file = getMediaTelegram(item=item, type_chat=type_chat, url_telegram=url_telegram)
                if uploaded_file is not None: 
                    if isinstance(uploaded_file, str):
                        requests.get(url=f"{url_telegram}/sendMessage", params={"chat_id": chat_id, "text": uploaded_file}) 
                    else:
                        list_input.append(uploaded_file)
                        
                caption = item.get(type_chat).get('caption')
                # TODO: Nanti ubah asyc bakal cek lalu masuk db/array global, tapi sementara ini dulu pengelolaan banyak media.
                if isHaveManyFileMessage(item=item, type_chat=type_chat):
                    if media_group_id is None: 
                        media_group_id = item.get(type_chat).get('media_group_id')
                        
                    if index + 1 < len(data_result):
                        item_selanjutnya = data_result[index + 1]
                        if isAnyFile(item_selanjutnya, type_chat):
                            continue 
            
            text_user = konteksChatUserTelegram(item=item, chat_id=chat_id, caption=caption)
            list_input.append({"type": "text", "text": text_user})
            
            
            kumpulan_hasil_fungsi = []
            response_chat = requests.get(url=f"{url_telegram}/sendMessage", params={"chat_id": chat_id, "text": random.choice(loading_text)})
            response_telegram = []
            
            butuh_gemini_lagi = True
            while butuh_gemini_lagi:
                butuh_gemini_lagi = False
                try:
                    if kumpulan_hasil_fungsi:
                        interaction = send_chat_llm(input_user=kumpulan_hasil_fungsi,interaction_id=interaction.id)
                        kumpulan_hasil_fungsi = []
                    else:
                        interaction = send_chat_llm(input_user=list_input)
                except Exception:
                    requests.get(url=f"{url_telegram}/sendMessage", params={"chat_id": chat_id, "text": "Maaf, AI sedang diluar jangkauan! silakan coba lagi nanti!"}) 
                    continue
                # Mengakses data penggunaan token dari response DEBUG
                print("\n=====================================================")
                print("Token Input:", interaction.usage.total_input_tokens)
                print("Token Output:", interaction.usage.total_output_tokens)
                print("Total keseluruhan token:", interaction.usage.total_tokens)
                print("\n=====================================================")
                
                # --- TAMBAHKAN BAGIAN INI ---
                daftar_fungsi = [step.name for step in interaction.steps if step.type == "function_call"]
                print(f"[DEBUG] Gemini memanggil {len(daftar_fungsi)} fungsi sekaligus: {daftar_fungsi}\n")
                # ----------------------------
                
                for step in interaction.steps:
                    if step.type == "function_call":
                        nama_fungsi = step.name
                        argumen = step.arguments
                        
                        if nama_fungsi == "llm_mendapatkan_konteks":
                            butuh_gemini_lagi = True
                            
                        elif nama_fungsi == "jawaban_telegram":
                            response_telegram.append(jawaban_telegram(**argumen))
                        
                        elif nama_fungsi == "insert_transaksi":
                            try:
                                response_insert = insert_transaksi(tanggal=tanggal_input, chat_id=chat_id, **argumen)
                                kumpulan_hasil_fungsi.append({
                                    "type": "function_result",
                                    "name": nama_fungsi,
                                    "call_id": step.id,
                                    "result": [{"type": "text", "text": json.dumps(response_insert, default=str)}]
                                })
                                teks_balasan = jawabanTelegramInsert(response_insert)
                                response_telegram.append(teks_balasan)
                            except Exception:
                                requests.get(url=f"{url_telegram}/sendMessage", params={"chat_id": chat_id, "text": "Maaf, Database sedang diluar jangkauan!"}) 
                                continue
                                
                        elif nama_fungsi == "edit_transaksi_by_id":
                            try:
                                data_sebelum, data_setelah = edit_transaksi_by_id(chat_id=chat_id, **argumen)
                                kumpulan_hasil_fungsi.append({
                                    "type": "function_result",
                                    "name": nama_fungsi,
                                    "call_id": step.id,
                                    "result": [
                                        {"type": "text", "text_data_sebelum": json.dumps(data_sebelum, default=str)}, 
                                        {"type": "text", "text_data_sesudah": json.dumps(data_setelah, default=str)}
                                    ]
                                })
                                teks_balasan = jawabanTelegramEdit(data_sebelum, data_setelah)
                                response_telegram.append(teks_balasan)
                            except Exception:
                                requests.get(url=f"{url_telegram}/sendMessage", params={"chat_id": chat_id, "text": "Maaf, Database sedang diluar jangkauan!"}) 
                                continue
                                
                        elif nama_fungsi == "delete_transaksi_by_id":
                            try:
                                response_delete = delete_transaksi_by_id(chat_id=chat_id, **argumen)
                                kumpulan_hasil_fungsi.append({
                                    "type": "function_result",
                                    "name": nama_fungsi,
                                    "call_id": step.id,
                                    "result": [{"type": "text", "text_data_sesudah": json.dumps(response_delete, default=str)}]
                                })
                                text_balasan = jawabanTelegramDelete(response_delete)
                                response_telegram.append(text_balasan)
                            except Exception:
                                requests.get(url=f"{url_telegram}/sendMessage", params={"chat_id": chat_id, "text": "Maaf, Database sedang diluar jangkauan!"}) 
                                continue
                                
                        elif nama_fungsi == "search_transaksi_multi":
                            try:
                                butuh_gemini_lagi = True
                                hasil_transaksi = search_transaksi_multi(chat_id=chat_id, **argumen)
                                kumpulan_hasil_fungsi.append({
                                    "type": "function_result",
                                    "name": nama_fungsi,
                                    "call_id": step.id,
                                    "result": [{"type": "text", "text": json.dumps(hasil_transaksi, default=str)}]
                                })
                                text_balasan = jawabanTelegramSearch(response_search=hasil_transaksi)
                            except Exception:
                                requests.get(url=f"{url_telegram}/sendMessage", params={"chat_id": chat_id, "text": "Maaf, Database sedang diluar jangkauan!"}) 
                                continue
            # Cek apakah ada teks yang berhasil
            if response_telegram:
                hasil_akhir_teks_telegram = "\n\n".join(response_telegram)   
                response_chat = requests.get(url=f"{url_telegram}/sendMessage", params={"chat_id": chat_id, "text": hasil_akhir_teks_telegram}) 
                if response_chat.status_code == 200: 
                    insert_riwayat_percakapan(chat_id=chat_id, identitas="Bot", tanggal=tanggal_input, pesan=hasil_akhir_teks_telegram, catatan=None, conn=None)
                else:
                    sleep(10)
                    break
    
    except Exception as e:
        print(e)
        sleep(10)
        continue