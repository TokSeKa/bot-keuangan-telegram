from google import genai
from pydantic import BaseModel, Field
from typing import Literal, Optional

import os
from dotenv import load_dotenv
load_dotenv()

from utils.skema_fungsi import insert_transaksi_declaration, jawaban_telegram_declaration, search_transaksi_multi_declaration, proses_llm_selesai_declaration, llm_mendapatkan_konteks_declaration
tools_skema = [insert_transaksi_declaration, jawaban_telegram_declaration, search_transaksi_multi_declaration, proses_llm_selesai_declaration, llm_mendapatkan_konteks_declaration]
gemini_api = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api)

pilihan_model = [ 
    "gemini-3.5-flash-lite", # 500 RPD
    "gemini-3.1-flash-lite", # 500 RPD
    "gemini-3-flash", # 20 RPD
    "gemini-3.5-flash", # 20 RPD
    "gemini-3.6-flash", # 20 RPD
    "gemini-2.5-flash", # 20 RPD
    "gemini-2.5-flash-lite" # 20 RPD
]

daftar_fungsi_penutup=["llm_mendapatkan_konteks", "proses_llm_selesai", "jawaban_telegram"]

aturan_routing = f"""KONTEKS WAKTU (PENTING):
User berada di zona waktu Indonesia (UTC+07:00), namun sistem database menggunakan standar UTC+00:00. Jika user menyebutkan referensi waktu (seperti "hari ini", "kemarin", atau "jam 10 pagi"), anggap waktu tersebut sebagai UTC+07:00. Kamu WAJIB mengonversinya (mengurangi 7 jam) menjadi UTC+00:00 sebelum memasukkannya ke dalam parameter fungsi database.

ATURAN WAJIB (ROUTING):
Pada setiap giliranmu merespons, kamu WAJIB mengakhiri giliran dengan memanggil TEPAT SALAH SATU dari {len(daftar_fungsi_penutup)} fungsi penanda berikut:
1. Panggil '{daftar_fungsi_penutup[0]}' JIKA kamu sedang memanggil fungsi database (seperti pencarian) dan kamu butuh melihat balasan datanya pada giliran model selanjutnya. (Fungsi ini HARUS dipanggil BERSAMAAN/paralel dengan fungsi databasenya).
2. Panggil '{daftar_fungsi_penutup[1]}' JIKA permintaan user tuntas dieksekusi (misal: kamu memanggil fungsi insert/hapus) DAN kamu TIDAK perlu mengirimkan pesan ke Telegram user. (PENTING: Fungsi ini HARUS dipanggil BERSAMAAN/paralel dengan fungsi insert/hapus tersebut di dalam satu giliran yang sama).
3. Panggil '{daftar_fungsi_penutup[2]}' JIKA kamu perlu mengirimkan teks ke Telegram user (misal: menolak permintaan, menjawab obrolan biasa, atau sekadar memberi tahu bahwa tugas pencatatan sudah selesai).

INGAT: Jangan pernah memanggil lebih dari satu fungsi penanda di atas dalam giliran yang sama. Pilih salah satu yang paling sesuai dengan status akhir tindakanmu."""
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