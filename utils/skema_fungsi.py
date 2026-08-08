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
    "description": "Menyimpan data transaksi baru ke dalam database. JIKA user meminta memasukkan lebih dari satu transaksi, PANGGIL fungsi ini secara paralel (berulang) sesuai jumlah transaksinya.\n"
                   "PENTING: Sistem di backend sudah diatur untuk otomatis mengirimkan pesan konfirmasi 'Berhasil Input' dengan format khusus kepada user setelah fungsi ini dijalankan. OLEH KARENA ITU, JANGAN memanggil 'balas_pesan_telegram' untuk memberikan konfirmasi keberhasilan.\n"
                   "Tutup giliranmu dengan memanggil fungsi 'proses_llm_selesai' (jika sudah tidak ada aksi lain yang harus ditunggu).",
    "parameters": {
        "type": "object",
        "properties": {
            "nama": {"type": "string", "description": prompt_insert["nama"]},
            "nominal": {"type": "integer", "description": prompt_insert["nominal"]},
            "catatan": {"type": "string", "description": prompt_insert["catatan"]},
            "kategori": {
                "type": "string", 
                "enum": ["Lainnya", "Makanan", "Minuman", "Pakaian", "Alat mandi", "Tagihan Rumah", "Transportasi", "Telepon", "Sosial", "Perbaikan", "Kesehatan", "Olahraga", "Hiburan", "Pendidikan"], 
                "description": prompt_insert["kategori"]
            },
            "tipe": {
                "type": "string", 
                "enum": ["Pengeluaran", "Pemasukan"], 
                "description": prompt_insert["tipe"]
            },
        },
        "required": ["nama", "nominal", "kategori", "tipe"],
    },
}

prompt_edit_transaksi_by_id = {
    "id_target": "id_target sebagai target  utama dan tunggal identitas transaksi. Transaksi hanya akan dicari menggunakan ID sehingga kamu perlu melakukan search dahulu ",
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
    "tanggal": (
        "Waktu transaksi."
        "Keluarkan HANYA format: YYYY-MM-DD HH:MM:SS+00:00 (Contoh: 2026-08-06 14:16:33+00:00)." 
        "Jangan pakai huruf T pemisah tanggal dan waktu."),
    "tipe": (
        "Tipe transaksi yang dilakukan. Normalnya adalah pemasukan, sesuaikan "
        "dengan konteks; jika ada nuansa mendapatkan uang atau secara spesifik "
        "user memberikan perintah mencatat pemasukan, maka pilih Pemasukan."
    ),
}

edit_transaksi_by_id_declaration = {
    "type": "function",
    "name": "edit_transaksi_by_id",
    "description":  "Mengubah isi data transaksi yang ada didalam database. JIKA user meminta mengubah lebih dari satu transaksi, PANGGIL fungsi ini secara paralel (berulang) sesuai jumlah transaksinya.\n"
                    "Hanya panggil ini ketika kamu berhasil mendapatkan ID Transaksi yang user maksud. Karena perubahan data transaksi dilakukan satu transaksi dan menggunakan ID Transaksi.\n"
                    "Hanya berikan parameter untuk mengubah data terhadap bagian yang memang spesifik diminta user untuk di ubah, JANGAN mengubah field yang tidak perlu di ubah!.\n"
                    "PENTING: Sistem di backend sudah diatur untuk otomatis mengirimkan pesan konfirmasi 'Berhasil edit' dengan format khusus kepada user setelah fungsi ini dijalankan. OLEH KARENA ITU, JANGAN memanggil 'balas_pesan_telegram' untuk memberikan konfirmasi keberhasilan.\n"
                    "Tutup giliranmu dengan memanggil fungsi 'proses_llm_selesai' (jika sudah tidak ada aksi lain yang harus ditunggu).",
    "parameters": {
        "type": "object",
        "properties": {
            "id_target": {"type": "integer", "description": prompt_edit_transaksi_by_id["id_target"]},
            "nama": {"type": "string", "description": prompt_edit_transaksi_by_id["nama"]},
            "nominal": {"type": "integer", "description": prompt_edit_transaksi_by_id["nominal"]},
            "catatan": {"type": "string", "description": prompt_edit_transaksi_by_id["catatan"]},
            "kategori": {
                "type": "string", 
                "enum": ["Lainnya", "Makanan", "Minuman", "Pakaian", "Alat mandi", "Tagihan Rumah", "Transportasi", "Telepon", "Sosial", "Perbaikan", "Kesehatan", "Olahraga", "Hiburan", "Pendidikan"], 
                "description": prompt_edit_transaksi_by_id["kategori"]
            },
            "tanggal": {"type": "string", "description": prompt_edit_transaksi_by_id["tanggal"]},
            "tipe": {
                "type": "string", 
                "enum": ["Pengeluaran", "Pemasukan"], 
                "description": prompt_edit_transaksi_by_id["tipe"]
            },
        },
        "required": ["id_target"],
    },
}

# Deklarasi Hapus transaksi
delete_transaksi_by_id_declaration = {
    "type": "function",
    "name": "delete_transaksi_by_id",
    "description":  "Menghapus data transaksi yang ada didalam database. JIKA user meminta menghapus lebih dari satu transaksi, PANGGIL fungsi ini secara paralel (berulang) sesuai jumlah transaksinya.\n"
                    "Hanya panggil ini ketika kamu berhasil mendapatkan ID Transaksi yang user maksud. Karena penghapusan data transaksi dilakukan satu transaksi dan menggunakan ID Transaksi.\n"
                    "PENTING: Sistem di backend sudah diatur untuk otomatis mengirimkan pesan konfirmasi 'Berhasil hapus' dengan format khusus kepada user setelah fungsi ini dijalankan. OLEH KARENA ITU, JANGAN memanggil 'balas_pesan_telegram' untuk memberikan konfirmasi keberhasilan.\n"
                    "Tutup giliranmu dengan memanggil fungsi 'proses_llm_selesai' (jika sudah tidak ada aksi lain yang harus ditunggu).",
    "parameters": {
        "type": "object",
        "properties": {
            "id_target": {"type": "integer", "description": prompt_edit_transaksi_by_id["id_target"]} # Sama aja sih dengan edit deskripsinya.
        },
        "required": ["id_target"],
    },
}


prompt_jawaban_telegram = """Isi pesan teks yang akan dikirimkan langsung kepada user.
ATURAN PENGISIAN PESAN:
1. Jawaban General: Gunakan untuk menjawab obrolan biasa atau merespons pertanyaan umum dengan informatif.
2. Penolakan & Klarifikasi: Gunakan jika instruksi user tidak dapat diproses. Berikan balasan yang menjelaskan alasannya dengan sopan.
   Contoh kasus penolakan/klarifikasi:
   a. User bermaksud mencatat transaksi (misal: "beli makan") tapi tidak menyebutkan nominal/harganya. Minta user melengkapi nominalnya.
   b. User menuliskan hal sembarangan atau tidak jelas.
   c. User menanyakan hal yang sama sekali tidak relevan dengan konteks keuangan/pencatatan.
   d. Jika user tampak tidak tahu fungsimu, jelaskan bahwa kamu adalah Bot Telegram yang berguna untuk membantu mencatat keuangan.
Pastikan bahasa balasanmu natural, santai, dan tidak kaku."""

# Masukkan ke dalam deklarasi fungsi
jawaban_telegram_declaration = {
    "type": "function",
    "name": "jawaban_telegram",
    "description": "Fungsi untuk mengirimkan balasan teks langsung kepada user. Panggil fungsi ini jika permintaan user BUKAN untuk mengubah/mencari data di database, MELAINKAN sekadar butuh balasan obrolan biasa, menjawab pertanyaan, atau memberikan penolakan/klarifikasi. Memanggil fungsi ini akan sekaligus mengakhiri perulangan (loop) pemanggilan model.",
    "parameters": {
        "type": "object",
        "properties": {
            "response": {
                "type": "string", 
                "description": prompt_jawaban_telegram
            },
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
    "description": "Melakukan pencarian query SQL ke database postgre. Pakai fungsi ini ketika diminta mencari sebuah data tertentu atau membutuhkan konteks data ini agar bisa melakukan fungsi berikutnya. PENTING: Jika kamu memutuskan untuk memanggil fungsi pencarian ini, kamu WAJIB memanggil fungsi llm_mendapatkan_konteks secara bersamaan (paralel) di giliran ini juga.",
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
# Fungsi menyelesaikan 
proses_llm_selesai_declaration = {
    "type": "function",
    "name": "proses_llm_selesai",
    "description": "Fungsi penanda bahwa seluruh permintaan user telah SELESAI dieksekusi dan tidak butuh langkah lanjutan.\n"
                   "ATURAN PEMANGGILAN:\n"
                   "- PANGGIL fungsi ini jika tindakanmu saat ini sudah menuntaskan tujuan akhir user (misal: berhasil menambah data, atau selesai mencari data yang akan ditampilkan sistem).\n"
                   "- PENTING: Fungsi ini bersifat 'diam' dan TIDAK mengirimkan pesan teks apa pun ke Telegram user. Panggil HANYA JIKA sistem sudah memiliki balasan bawaan otomatis (seperti memunculkan tombol menu/hasil pencarian) sehingga kamu tidak perlu merangkai kata-kata balasan sendiri.\n"
                   "- JANGAN panggil fungsi ini jika kamu masih butuh balasan data dari sistem untuk menentukan langkah selanjutnya. (Gunakan 'llm_mendapatkan_konteks' untuk kasus ini).\n"
                   "- JANGAN panggil fungsi ini jika kamu perlu mengirim pesan teks ke user. (Gunakan 'balas_pesan_telegram' untuk kasus ini).\n"
                   "CONTOH KASUS JANGAN PANGGIL: User meminta 'hapus transaksi A'. Kamu belum tahu ID-nya, sehingga memanggil fungsi pencarian dulu. Karena kamu harus menunggu hasil pencarian itu sebelum bisa menghapus, JANGAN panggil fungsi ini.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

# Fungsi menyelesaikan 
llm_mendapatkan_konteks_declaration = {
    "type": "function",
    "name": "llm_mendapatkan_konteks",
    "description": "Fungsi penanda bahwa kamu butuh 'operan bola' (estafet) ke pemanggilan model berikutnya untuk memproses data yang kamu minta saat ini.\n"
                   "ATURAN PEMANGGILAN:\n"
                   "- PANGGIL fungsi ini JIKA pemanggilan fungsimu (misalnya fungsi search) saat ini ditujukan HANYA untuk mencari data, dan kamu WAJIB menunggu sistem mengembalikan hasil datanya kepadamu di giliran (turn) model selanjutnya untuk mengeksekusi tujuan akhir user (seperti update atau delete).\n"
                   "- EFEK PEMANGGILAN: Ketika fungsi ini dipanggil, giliran (turn) kamu saat ini akan LANGSUNG BERHENTI dan di-passing ke model berikutnya. Sistem akan menimpa variabel dalam perulangan (loop). OLEH KARENA ITU, JANGAN memanggil fungsi aksi akhir (seperti update/delete) berbarengan dengan fungsi ini! Cukup panggil fungsi pencari data (search) dan fungsi ini saja. Biarkan aksi lanjutannya dieksekusi pada giliran berikutnya.\n"
                   "- JANGAN panggil fungsi ini JIKA tindakanmu saat ini sudah merupakan langkah final yang langsung menyelesaikan permintaan user, tanpa perlu membaca balikan data lagi. Gunakan fungsi 'proses_llm_selesai' sebagai gantinya.\n"
                   "CONTOH KASUS PANGGIL: User meminta 'hapus transaksi A'. Kamu belum tahu ID-nya, jadi kamu memanggil fungsi search. Panggil fungsi search tersebut BERSAMAAN dengan memanggil fungsi ini. JANGAN panggil fungsi hapus di giliran ini! Biarkan giliran model selanjutnya yang membaca hasil pencarianmu dan melakukan penghapusan.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}