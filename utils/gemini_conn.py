from google import genai
from pydantic import BaseModel, Field
from typing import Literal, Optional

import os
from dotenv import load_dotenv
load_dotenv()

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

prompt_nominal = """Jumlah nominal akitifitas transaksi, Sesuaikan dengan konteks aktifitas. 
Rules: 
1. Konteks transaksi dalam rupiah, kurs rupiah biasanya memakai ribuan rupiah hingga jutaan rupiah, sesuaikan dengan value dari aktifitas yang dimaksud, contoh 34 dalam konteks makanan kemungkinan besaar 34000. 
2. DILARANG MENGARANG ANGKA YANG TIDAK DISEBUTKAN! 
3. JIKA NOMINAL TIDAK JELAS DISAAT DIBUTUHKAN, TOLAK DAN MINTA USER MENGKLARIFIKASIKAN ANGKANYA. 
4. Nominal 0 tidak sah kecuali user dengan spesifik meminta ditulis 0. 
5. Kurs dalam Rupiah, jika secara spesifik memakai kurs asing maka konversikan secara perkiraan."""

prompt_fungsi = """Output Fungsi dipakai untuk menentukan aksi apa yang akan dilakukan selanjutnya. 
Rules:
1. Penolakan: pakai Penolakan hanya ketika teks dari user tidak dapat diindetifikasi keinginannya. Ketika fungsi penolakan dilakukan, maka responsemu akan dikirim langsung ke user.
Contoh: 
a. Membeli tanpa menyebut nominal. 
b. Menuliskan hal sembarangan.
c. Memberikan pertanyaan yang tidak relevan dengan konteks keuangan ini.
Berikan response yang informatif dan sesuai alasan kamu memilih penolakan kepada user jika fungsi ini dipilih.

2. Perubahan: 
1. Pakai Perubahan jika user mengedit pesan sebelumnya dan terdapat transaksi sebelumnya sebagai konteks.
2. atau, terdapat keinginan user untuk mengubah transaksi yang pernah dilakukan dengan konteks waktu.
"""

prompt_response = """ Ini adalah area output kamu untuk memberikan response kepada chat user.
Rules:
1. Jika fungsi yang kamu pilih adalah penolakan, maka berikan response yang informatif dan sesuai alasan kamu memilih penolakan kepada user jika fungsi ini dipilih.
2. Hanya memberikan response jika fungsi terpilih adalah penolakan.
3. Jika user tampak tidak tahu apa guna kamu, jelaskan bahwa kamu adalah Bot yang berguna untuk membantu keuangan user via chat telegram.
"""

# Structured outpu
class Transaksi(BaseModel):
    nama: str = Field(description="Nama aktifitas atau objek transaksi")
    nominal: int = Field(description=prompt_nominal)
    catatan: Optional[str] = Field(description="Catatan kaki dari user.")
    kategori: Literal["Lainnya", "Makanan", "Minuman", "Pakaian", "Alat mandi", "Tagihan Rumah", "Transportasi", "Telepon", "Sosial", "Perbaikan", "Kesehatan", "Olahraga", "Hiburan", "Pendidikan"] = Field(description="Kategori aktivitas yang disebut user")
    tipe: Literal["Pengeluaran", "Pemasukan"] = Field(description="Tipe aktifitas berupa ingin melakukan transaksi Pengeluaran atau Pemasukan")
    fungsi: Literal["Pencatatan", "Perubahan", "Penghapusan", "Pencarian", "Penolakan"] = Field(description=prompt_fungsi)
    response: Optional[str] = Field(description=prompt_response)

# Fungsi mengirimkan ke gemini, nantinya text nya di balut dengan promt
def send_chat_llm(input_user):
    for model in pilihan_model:
        try:
            interaction  = client.interactions.create(
                    model=model,
                    input=input_user,
                    response_format={
                        "type": "text",
                        "mime_type": "application/json",
                        "schema": Transaksi.model_json_schema()
                    },
                )
            return Transaksi.model_validate_json(interaction.output_text)
        except Exception as e:
            # Filter khusus untuk Rate Limit (Status Code 429)
            if getattr(e, "status_code", None) == 429:
                continue
            raise
    else:
        raise Exception("Semua model tersedi sudah mencapai limit harian!")