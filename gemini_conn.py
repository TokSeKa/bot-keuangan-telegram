from google import genai
from pydantic import BaseModel, Field
from typing import Literal, Optional

import os
from dotenv import load_dotenv
load_dotenv()

gemini_api = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api)

pilihan_model = [ #hanya untuk testing
    # --- Gemini 3 Series ---
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro",
    "gemini-3.1-flash-lite",
    "gemini-3-flash",

    # --- Gemini 2.5 Series ---
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

# Structured outpu
class Transaksi(BaseModel):
    nama: str = Field(description="Nama aktifitas atau objek transaksi")
    nominal: int = Field(description="Jumlah nominal akitifitas transaksi, Sesuaikan dengan konteks aktifitas, kurs rupiah biasanya memakai ribuan rupiah hingga jutaan rupiah, sesuaikan dengan value dari aktifitas yang dimaksud, contoh 34 dalam konteks makanan kemungkinan besaar 34000 .Kurs dalam Rupiah, jika secara spesifik memakai kurs asing maka konversikan secara perkiraan.")
    catatan: Optional[str] = Field(description="Catatan kaki dari user.")
    kategori: Literal["Lainnya", "Makanan", "Minuman", "Pakaian", "Alat mandi", "Tagihan Rumah", "Transportasi", "Telepon", "Sosial", "Perbaikan", "Kesehatan", "Olahraga", "Hiburan", "Pendidikan"] = Field(description="Kategori aktivitas yang disebut user")
    tipe: Literal["Pengeluaran", "Pemasukan"] = Field(description="Tipe aktifitas berupa ingin melakukan transaksi Pengeluaran atau Pemasukan")
    fungsi: Literal["Pencatatan", "Perubahan", "Penghapusan", "Pencarian"] = Field(description="Jenis fungsi yang perlu dipakai dalam aktifitas ini.")
    response: str = Field(description="Respon Terhadap permintaan user yang dipakai untuk menjawab chat user")

# Fungsi mengirimkan ke gemini, nantinya text nya di balut dengan promt
def send_chat_llm(input_user, model="gemini-3.5-flash"):
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