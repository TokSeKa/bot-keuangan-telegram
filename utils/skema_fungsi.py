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


prompt_search_transaksi_multi = {
    "nama": "Identitas transaksi. Pencarian menggunakan SQL: LIKE %nama%. Gunakan kata kunci paling relevan dari input user. Jika user tidak secara spesifik mencari nama transaksi tertentu, jangan gunakan field ini.",
    
    "kategori": "Kategori transaksi (menyesuaikan enum). Jika user tidak secara spesifik mencari kategori tertentu, jangan gunakan field ini.",
    
    "tipe": "Tipe transaksi (menyesuaikan enum). Jika user tidak secara spesifik mencari tipe tertentu, jangan gunakan field ini. Hanya gunakan pilihan Pengeluaran atau Pemasukan. Tipe tidak bisa jenis lain.",
    
    "catatan": "Catatan tambahan transaksi (opsional, bisa jadi kosong di database). Pencarian menggunakan SQL: LIKE %catatan%. Gunakan kata kunci paling relevan. Jika user tidak secara spesifik mencari isi catatan tertentu, jangan gunakan field ini.",
    
    "tanggal_awal": "Batas waktu awal transaksi. Keluarkan HANYA format: YYYY-MM-DD HH:MM:SS+00:00 (Contoh: 2026-08-06 14:16:33+00:00). Sistem akan mencari transaksi yang lebih baru dari tanggal ini. Contoh kasus: Jika user bertanya '(kemarin aku beli apa aja ya?)' pada saat waktu saat ini adalah 2026-08-06 14:16:33+00:00, maka kurangi 24 jam dan isi field ini dengan 2026-08-05 14:16:33+00:00. Dapat digabungkan dengan tanggal_akhir untuk mencari rentang waktu. Jangan pakai huruf T pemisah tanggal dan waktu.",
    
    "tanggal_akhir": "Batas waktu akhir transaksi. Keluarkan HANYA format: YYYY-MM-DD HH:MM:SS+00:00. Sistem akan mencari transaksi yang lebih tua/lama dari tanggal ini. Contoh kasus: Jika user bertanya '(sebelum jam 12 hari ini aku beli apa aja ya?)' pada 2026-08-06 14:16:33+00:00, sesuaikan jamnya dan isi field ini dengan 2026-08-06 12:00:00+00:00. Dapat digabungkan dengan tanggal_awal untuk mencari rentang waktu. Jangan pakai huruf T pemisah tanggal dan waktu.",
    
    "nominal": "Nominal spesifik (eksak) transaksi. Hanya gunakan field ini jika user secara spesifik menyebutkan angka atau harga transaksi yang dicari.",
    
    "batas_nominal_bawah": "Batas minimum nominal pencarian. Sistem akan mencari transaksi dengan nominal di atas angka ini. Dapat digabungkan dengan batas_nominal_atas untuk mencari rentang nominal tertentu.",
    
    "batas_nominal_atas": "Batas maksimum nominal pencarian. Sistem akan mencari transaksi dengan nominal di bawah angka ini. Dapat digabungkan dengan batas_nominal_bawah untuk mencari rentang nominal tertentu."
}

# def search_transaksi_multi(nama=None, kategori=None, tipe=None, catatan=None, chat_id=None, tanggal_awal=None, tanggal_akhir=None, nominal=None, batas_nominal_bawah=None, batas_nominal_atas=None, conn=None):
search_transaksi_multi_declaration = {
    "type": "function",
    "name": "search_transaksi_multi",
    "description": "Melakukan pencarian query SQL ke database postgre. Pakai fungsi ini ketika diminta mencari sebuah data tertentu atau membutuhkan konteks data ini agar bisa melakukan fungsi berikutnya.",
    "parameters": {
        "type": "object",
        "properties": {
            "nama": {"type": "string", "description": prompt_search_transaksi_multi["nama"]},
            "kategori": {"type": "string", "enum": ["Lainnya", "Makanan", "Minuman", "Pakaian", "Alat mandi", "Tagihan Rumah", "Transportasi", "Telepon",   "Sosial", "Perbaikan", "Kesehatan", "Olahraga", "Hiburan", "Pendidikan"], "description": prompt_search_transaksi_multi["kategori"]},
            "tipe": {"type": "string", "enum": ["Pengeluaran", "Pemasukan"], "description": prompt_search_transaksi_multi["tipe"]},
            "catatan": {"type": "string", "description": prompt_search_transaksi_multi["catatan"]},
            "tanggal_awal": {"type": "string", "description": prompt_search_transaksi_multi["tanggal_awal"]},
            "tanggal_akhir": {"type": "string", "description": prompt_search_transaksi_multi["tanggal_akhir"]},
            "nominal": {"type": "integer", "description": prompt_search_transaksi_multi["nominal"]},
            "batas_nominal_bawah": {"type": "integer", "description": prompt_search_transaksi_multi["batas_nominal_bawah"]},
            "batas_nominal_atas": {"type": "integer", "description": prompt_search_transaksi_multi["batas_nominal_atas"]},
        },
        "required": [],
    },
}