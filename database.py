import psycopg
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

load_dotenv()

password_postgresql = os.getenv("PASSWORD_POSTGRESQL")
nama_database = os.getenv("NAMA_DATABASE")
user_database = os.getenv("USER_DATABASE")

def insert_transaksi(nama, nominal, catatan, kategori, tanggal, tipe, chat_id):
    with psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO transaksi (nama, nominal, catatan, kategori, tanggal, tipe, chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;",
                (nama, nominal, catatan, kategori, tanggal, tipe, chat_id))
            return cur.fetchone()

# tanggal_input = datetime.fromtimestamp(1785474101, tz=timezone.utc)              
# print(insert_transaksi("Nasi sss", 25000, None, "Makanan", tanggal_input, "Pengeluaran", "5767851505"))


# # Connect to an existing database
# with psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql) as conn:

#     # Open a cursor to perform database operations
#     with conn.cursor() as cur:
#         tanggal_input = datetime.fromtimestamp(1785474101, tz=timezone.utc)
#         # Pass data to fill a query placeholders and let Psycopg perform
#         # the correct conversion (no SQL injections!)
#         def insertTransaksi(nama, nominal, catatan, kategori, tanggal, tipe, chat_id):
#             cur.execute(
#                 "INSERT INTO transaksi (nama, nominal, catatan, kategori, tanggal, tipe, chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#                 (nama, nominal, catatan, kategori, tanggal, tipe, chat_id))
            
#         insertTransaksi("Nasi Bebek", 25000, None, "Makanan", tanggal_input, "Pengeluaran", "5767851505")
#         # Query the database and obtain data as Python objects.
#         cur.execute("SELECT * FROM test")
#         print(cur.fetchone())
#         # will print (1, 100, "abc'def")

#         # You can use `cur.executemany()` to perform an operation in batch
#         cur.executemany(
#             "INSERT INTO test (num) values (%s)",
#             [(33,), (66,), (99,)])

#         # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
#         # of several records, or even iterate on the cursor
#         cur.execute("SELECT id, num FROM test order by num")
#         for record in cur:
#             print(record)

#         # Make the changes to the database persistent
#         conn.commit()