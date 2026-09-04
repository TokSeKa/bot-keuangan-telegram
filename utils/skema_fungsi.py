insert_transaksi_declaration = {
    "type": "function",
    "name": "insert_transaksi",
    "description": "Menyimpan satu atau banyak transaksi baru sekaligus.",
    "parameters": {
        "type": "object",
        "properties": {
            "daftar_transaksi": {
                "type": "array",
                "description": "Daftar transaksi yang akan disimpan.",
                "items": {
                    "type": "object",
                    "properties": {
                        "nama": {
                            "type": "string", 
                            "description": "Nama transaksi."
                        },
                        "nominal": {
                            "type": "integer",
                            "description": "Nominal dalam Rupiah. Asumsikan angka kecil sbg ribuan (34 ke 34000). Minta klarifikasi jika tidak disebutkan. Nominal 0 tidak sah kecuali diminta."
                        },
                        "catatan": {
                            "type": "string", 
                            "description": "Catatan tambahan (opsional)."
                        },
                        "kategori": {
                            "type": "string",
                            "enum": [
                                "Lainnya", "Makanan", "Minuman", "Pakaian", 
                                "Alat mandi", "Tagihan Rumah", "Transportasi", 
                                "Telepon", "Sosial", "Perbaikan", "Kesehatan", 
                                "Olahraga", "Hiburan", "Pendidikan"
                            ], 
                            "description": "Kategori transaksi. Default 'Lainnya' jika tidak yakin."
                        },
                        "tipe": {
                            "type": "string",
                            "enum": ["Pengeluaran", "Pemasukan"],
                            "description": "Tipe transaksi. Sesuaikan konteks; jika user mendapat uang pilih Pemasukan."
                        }
                    },
                    "required": ["nama", "nominal", "kategori", "tipe"]
                }
            }
        },
        "required": ["daftar_transaksi"]
    }
}

edit_transaksi_by_id_declaration = {
    "type": "function",
    "name": "edit_transaksi_by_id",
    "description": "Mengubah transaksi berdasarkan ID. Hanya isi parameter yang ingin diubah. Jika >1, panggil paralel.",
    "parameters": {
        "type": "object",
        "properties": {
            "id_target": {
                "type": "integer",
                "description": "ID transaksi yang akan diubah."
            },
            "nama": {
                "type": "string",
                "description": "Nama baru (opsional)."
            },
            "nominal": {
                "type": "integer",
                "description": "Nominal baru dalam Rupiah (opsional)."
            },
            "catatan": {
                "type": "string",
                "description": "Catatan baru (opsional)."
            },
            "kategori": {
                "type": "string",
                "enum": [
                    "Lainnya", "Makanan", "Minuman", "Pakaian",
                    "Alat mandi", "Tagihan Rumah", "Transportasi",
                    "Telepon", "Sosial", "Perbaikan", "Kesehatan",
                    "Olahraga", "Hiburan", "Pendidikan"
                ],
                "description": "Kategori baru (opsional)."
            },
            "tanggal": {
                "type": "string",
                "description": "Format: YYYY-MM-DD HH:MM:SS+00:00 (opsional)."
            },
            "tipe": {
                "type": "string",
                "enum": ["Pengeluaran", "Pemasukan"],
                "description": "Tipe baru (opsional)."
            }
        },
        "required": ["id_target"]
    }
}

delete_transaksi_by_id_declaration = {
    "type": "function",
    "name": "delete_transaksi_by_id",
    "description": "Menghapus transaksi berdasarkan ID. Jika >1, panggil paralel.",
    "parameters": {
        "type": "object",
        "properties": {
            "id_target": {
                "type": "integer", 
                "description": "ID transaksi yang akan dihapus."
            }
        },
        "required": ["id_target"]
    }
}

search_transaksi_multi_declaration = {
    "type": "function",
    "name": "search_transaksi_multi",
    "description": "Mencari transaksi dengan filter opsional. Semua parameter opsional. Format tanggal: 'YYYY-MM-DD HH:MM:SS+00:00'.",
    "parameters": {
        "type": "object",
        "properties": {
            "nama": {
                "type": "string", 
                "description": "Cari nama transaksi (LIKE %nama%)."
            },
            "kategori": {
                "type": "string", 
                "enum": [
                    "Lainnya", "Makanan", "Minuman", "Pakaian", 
                    "Alat mandi", "Tagihan Rumah", "Transportasi", 
                    "Telepon", "Sosial", "Perbaikan", "Kesehatan", 
                    "Olahraga", "Hiburan", "Pendidikan"
                ], 
                "description": "Filter kategori."
            },
            "tipe": {
                "type": "string", 
                "enum": ["Pengeluaran", "Pemasukan"], 
                "description": "Filter tipe."
            },
            "catatan": {
                "type": "string", 
                "description": "Cari di catatan (LIKE %catatan%)."
            },
            "tanggal_awal": {
                "type": "string",
                "description": "Batas awal transaksi. Format: YYYY-MM-DD HH:MM:SS+00:00."
            },
            "tanggal_akhir": {
                "type": "string",
                "description": "Batas akhir transaksi. Format: YYYY-MM-DD HH:MM:SS+00:00."
            },
            "nominal": {
                "type": "integer", 
                "description": "Nominal eksak."
            },
            "batas_nominal_bawah": {
                "type": "integer", 
                "description": "Minimal nominal."
            },
            "batas_nominal_atas": {
                "type": "integer", 
                "description": "Maksimal nominal."
            }
        },
        "required": []
    }
}

jawaban_telegram_declaration = {
    "type": "function",
    "name": "jawaban_telegram",
    "description": "Kirim teks langsung ke user. Gunakan sesuai aturan penutup di system instruction.",
    "parameters": {
        "type": "object",
        "properties": {
            "response": {
                "type": "string", 
                "description": "Pesan yang akan dikirim ke user."
            }
        },
        "required": ["response"]
    }
}

proses_llm_selesai_declaration = {
    "type": "function",
    "name": "proses_llm_selesai",
    "description": "Penanda bahwa seluruh aksi telah selesai. Tidak mengirim pesan ke user.",
    "parameters": {
        "type": "object", 
        "properties": {}, 
        "required": []
    }
}

llm_mendapatkan_konteks_declaration = {
    "type": "function",
    "name": "llm_mendapatkan_konteks",
    "description": "Penanda bahwa kamu butuh hasil fungsi saat ini untuk diproses di giliran selanjutnya.",
    "parameters": {
        "type": "object", 
        "properties": {}, 
        "required": []
    }
}