from google import genai

import os
from dotenv import load_dotenv
load_dotenv()

from utils.skema_fungsi import insert_transaksi_declaration, jawaban_telegram_declaration, search_transaksi_multi_declaration, llm_mendapatkan_konteks_declaration, edit_transaksi_by_id_declaration, delete_transaksi_by_id_declaration

tools_skema = [insert_transaksi_declaration, jawaban_telegram_declaration, search_transaksi_multi_declaration, llm_mendapatkan_konteks_declaration, edit_transaksi_by_id_declaration, delete_transaksi_by_id_declaration]
gemini_api = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api)

pilihan_model = [ 
    "gemini-3.1-flash-lite", # 500 RPD
    "gemini-3.5-flash-lite", # 500 RPD
    "gemini-3-flash", # 20 RPD
    "gemini-3.5-flash", # 20 RPD
    "gemini-3.6-flash", # 20 RPD
    "gemini-2.5-flash", # 20 RPD
    "gemini-2.5-flash-lite" # 20 RPD
]

daftar_fungsi_penutup=["llm_mendapatkan_konteks", "proses_llm_selesai", "jawaban_telegram"]

tools_tier1 = [
    insert_transaksi_declaration,
    jawaban_telegram_declaration,
    search_transaksi_multi_declaration,
    llm_mendapatkan_konteks_declaration
]

tools_tier2 = [
    edit_transaksi_by_id_declaration,
    delete_transaksi_by_id_declaration,
    jawaban_telegram_declaration
]

aturan_routing = """KONTEKS WAKTU: Waktu user UTC+7. Database memakai UTC+0. Konversi kurangi 7 jam sebelum memasukkan ke parameter fungsi.
TAMPILAN DATA: Tampilkan SEMUA data satu per satu, JANGAN dirangkum.

Jika tugas belum selesai akhiri pemanggillan fungsi dengan memanggil TEPAT SATU fungsi penanda berikut:
- llm_mendapatkan_konteks : panggil BERSAMAAN dengan fungsi database (misal search) jika kamu perlu melihat hasilnya di giliran selanjutnya.
- jawaban_telegram        : panggil jika kamu perlu mengirim teks langsung ke user (obrolan, penolakan, klarifikasi, atau notifikasi manual).
Jika tugas telah selesai di ronde ini, maka tidak perlu memangil kedua fungsi sebelumnya."""

# Fungsi mengirimkan ke gemini, nantinya text nya di balut dengan promt
def send_chat_llm(input_user, interaction_id=None):
    for model in pilihan_model:
        try:
            parameter_kirim = {
                "model": model,
                "input": input_user,
                "tools": tools_skema,
                "system_instruction": aturan_routing,
                "generation_config": {"tool_choice": "any"}
            }
            if interaction_id is not None:
                parameter_kirim["previous_interaction_id"] = interaction_id
                
            interaction = client.interactions.create(**parameter_kirim)
            return interaction
            
        except Exception as e:
            if getattr(e, "status_code", None) == 429 or "429" in str(e):
                continue
            raise
    else:
        raise Exception("Semua model tersedia sudah mencapai limit harian!")
    
def get_uploaded_file_api(file):
    return client.files.upload(file=file)