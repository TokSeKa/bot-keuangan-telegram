import psycopg
from dotenv import load_dotenv
import os
from psycopg.rows import dict_row
from contextlib import nullcontext

load_dotenv()

password_postgresql = os.getenv("PASSWORD_POSTGRESQL")
nama_database = os.getenv("NAMA_DATABASE")
user_database = os.getenv("USER_DATABASE")

# def insert_transaksi(nama, nominal, catatan, kategori, tanggal, tipe, chat_id):
#     with psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql) as conn:
#         try:
#             with conn.transaction():
#                 with conn.cursor(row_factory=dict_row) as cur:
#                     cur.execute(
#                         "INSERT INTO transaksi (nama, nominal, catatan, kategori, tanggal, tipe, chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;",
#                         (nama, nominal, catatan, kategori, tanggal, tipe, chat_id))
#                     return cur.fetchone()
#         except psycopg.Error as e:
#             print(f"Error occurred, transaction rolled back: {e}")
           
# Menginputkan transaksi ke database 
def insert_transaksi(nama, nominal, catatan, kategori, tanggal, tipe, chat_id, conn=None):
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
def select_transaksi(tanggal, chat_id, conn=None):
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