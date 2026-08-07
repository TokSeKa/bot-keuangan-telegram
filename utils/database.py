import psycopg
from dotenv import load_dotenv
import os
from psycopg.rows import dict_row
from contextlib import nullcontext

load_dotenv()

password_postgresql = os.getenv("PASSWORD_POSTGRESQL")
nama_database = os.getenv("NAMA_DATABASE")
user_database = os.getenv("USER_DATABASE")

# Menginputkan transaksi ke database 
def insert_transaksi(nama, nominal, kategori, tanggal, tipe, chat_id, catatan=None, conn=None):
    if conn:
        ctx = nullcontext(conn) # Biar bisa passing conn dari luar
    else:
        ctx = psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql)
    with ctx as conn:
        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        "INSERT INTO transaksi (nama, nominal, catatan, kategori, tanggal, tipe, chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;",
                        (nama, nominal, catatan, kategori, tanggal, tipe, chat_id))
                    return cur.fetchone()   
        except psycopg.Error as e:
            print(f"Error occurred, transaction rolled back: {e}")
            
# Mencari transaksi ke database berdasarkan timestamp + id chat user
# Output harapan: Memberikan konteks kepada LLM
def select_transaksi_by_tanggal_and_chat_id(tanggal, chat_id, conn=None):
    sql = "SELECT * FROM transaksi WHERE tanggal = %s AND chat_id = %s"
    if conn:
        ctx = nullcontext(conn) # Biar bisa passing conn dari luar
    else:
        ctx = psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql)
    with ctx as conn:
        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(sql,(tanggal, str(chat_id)))
                    return cur.fetchall()
        except psycopg.Error as e:
            print(f"Error occurred, transaction rolled back: {e}")
            
# Mencari transaksi makai fungsi %like% di SQL, mengembalikan seluruh data untuk nantinya ditampilkan menjadi tombol
# Mencari transaksi makai fungsi %like% di SQL, mengembalikan seluruh data untuk nantinya ditampilkan menjadi tombol
def search_transaksi_multi(chat_id=None, nama=None, kategori=None, tipe=None, catatan=None, tanggal_awal=None, tanggal_akhir=None, nominal=None, batas_nominal_bawah=None, batas_nominal_atas=None, conn=None):
    sql = "SELECT * FROM transaksi"
    kondisi = []
    parameter = []
    
    # 1. Cek variabelnya satu per satu
    if chat_id is not None:
        kondisi.append("chat_id = %s")
        parameter.append(str(chat_id))
    if nama is not None:
        kondisi.append("nama ILIKE %s")
        parameter.append(f"%{nama}%")
    if kategori is not None:
        kondisi.append("kategori = %s")
        parameter.append(kategori)
    if tipe is not None:
        kondisi.append("tipe = %s")
        parameter.append(tipe)
    if catatan is not None:
        kondisi.append("catatan ILIKE %s")
        parameter.append(f"%{catatan}%")
    if tanggal_awal is not None:
        kondisi.append("tanggal >= %s")
        parameter.append(tanggal_awal)
    if tanggal_akhir is not None:
        kondisi.append("tanggal <= %s")
        parameter.append(tanggal_akhir)
    if nominal is not None:
        kondisi.append("nominal = %s")
        parameter.append(nominal)
    if batas_nominal_bawah is not None:
        kondisi.append("nominal >= %s")
        parameter.append(batas_nominal_bawah)
    if batas_nominal_atas is not None:
        kondisi.append("nominal <= %s")
        parameter.append(batas_nominal_atas)
    if kondisi:
        sql += " WHERE " + " AND ".join(kondisi)
        
    sql += " ORDER BY tanggal DESC LIMIT 5" 
    
    print("INI SQL NYA: " + sql)
    print("INI PARAMETER NYA: " + str(parameter))
        
    if conn:
        ctx = nullcontext(conn) # Biar bisa passing conn dari luar
    else:
        ctx = psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql)
    with ctx as conn:
        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(sql, parameter)
                    return cur.fetchall()
        except psycopg.Error as e:
            print(f"Error occurred, transaction rolled back: {e}")