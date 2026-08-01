import psycopg
from dotenv import load_dotenv
import os
from psycopg.rows import dict_row

load_dotenv()

password_postgresql = os.getenv("PASSWORD_POSTGRESQL")
nama_database = os.getenv("NAMA_DATABASE")
user_database = os.getenv("USER_DATABASE")

def insert_transaksi(nama, nominal, catatan, kategori, tanggal, tipe, chat_id):
    with psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "INSERT INTO transaksi (nama, nominal, catatan, kategori, tanggal, tipe, chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;",
                (nama, nominal, catatan, kategori, tanggal, tipe, chat_id))
            return cur.fetchone()