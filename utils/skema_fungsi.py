prompt_insert = {
    "nama": "Nama sebagai identitas transaksi yang terjadi.",
    "nominal": (
        "Jumlah nominal aktivitas transaksi, sesuaikan dengan konteks aktivitas.\n"
        "Rules:\n"
        "1. Konteks transaksi dalam rupiah, kurs rupiah biasanya memakai ribuan rupiah hingga jutaan rupiah, sesuaikan dengan value dari aktivitas yang dimaksud, contoh 34 dalam konteks makanan kemungkinan besar 34000.\n"
        "2. DILARANG MENGARANG ANGKA YANG TIDAK DISEBUTKAN!\n"
        "3. JIKA NOMINAL TIDAK JELAS SAAT DIBUTUHKAN, TOLAK DAN MINTA USER MENGKLARIFIKASI ANGKA TERSEBUT.\n"
        "4. Nominal 0 tidak sah kecuali user secara spesifik meminta ditulis 0.\n"
        "5. Kurs dalam Rupiah, jika secara spesifik memakai kurs asing maka konversikan secara perkiraan."
    ),
    "catatan": (
        "Catatan tambahan dari pesan user, isi jika diperlukan, misalkan konteks "
        "dari nama transaksi saja tidak cukup atau user secara spesifik minta "
        "ada catatan di transaksi tersebut."
    ),
    "kategori": (
        "Kategori transaksi yang terjadi. Jika tidak yakin atau tidak ada "
        "pada pilihan kategori, masukkan ke kategori Lainnya."
    ),
    "tipe": (
        "Tipe transaksi yang dilakukan. Normalnya adalah pemasukan, sesuaikan "
        "dengan konteks; jika ada nuansa mendapatkan uang atau secara spesifik "
        "user memberikan perintah mencatat pemasukan, maka pilih Pemasukan."
    ),
}


insert_transaksi_declaration = {
    "type": "function",
    "name": "insert_transaksi",
    "description": "Melakukan input transaksi kedalam Database. jika terdapat lebih dari satu transaksi, maka panggil satu persatu fungsi ini.",
    "parameters": {
        "type": "object",
        "properties": {
            "nama": {"type": "string", "description": prompt_insert["nama"]},
            "nominal": {"type": "integer", "description": prompt_insert["nominal"]},
            "catatan": {"type": "string", "description": prompt_insert["catatan"]},
            "kategori": {"type": "string", "enum": ["Lainnya", "Makanan", "Minuman", "Pakaian", "Alat mandi", "Tagihan Rumah", "Transportasi", "Telepon", "Sosial", "Perbaikan", "Kesehatan", "Olahraga", "Hiburan", "Pendidikan"], "description": prompt_insert["kategori"]},
            "tipe": {"type": "string", "enum": ["Pengeluaran", "Pemasukan"], "description": prompt_insert["tipe"]},
        },
        "required": ["nama", "nominal", "kategori", "tipe"],
    },
}

prompt_jawaban_telegram_penolakan = """Output Fungsi dipakai untuk menentukan aksi apa yang akan dilakukan selanjutnya. 
Rules:
1. Penolakan: pakai Penolakan hanya ketika teks dari user tidak dapat diindetifikasi keinginannya. Ketika fungsi penolakan dilakukan, maka responsemu akan dikirim langsung ke user.
Contoh: 
a. Membeli tanpa menyebut nominal. 
b. Menuliskan hal sembarangan.
c. Memberikan pertanyaan yang tidak relevan dengan konteks keuangan ini.
d. Jika user tampak tidak tahu apa guna kamu, jelaskan bahwa kamu adalah Bot yang berguna untuk membantu keuangan user via chat telegram.
Berikan response yang informatif dan sesuai alasan kamu memilih penolakan kepada user jika fungsi ini dipilih.
"""

jawaban_telegram_penolakan_declaration = {
    "type": "function",
    "name": "jawaban_telegram_penolakan",
    "description": "Memberikan balasan kepada user terhadap chat yang diberikan untuk kasus fungsi yang tidak terkait atas perubahan database.",
    "parameters": {
        "type": "object",
        "properties": {
            "response": {"type": "string", "description": prompt_jawaban_telegram_penolakan},
        },
        "required": ["response"],
    },
}