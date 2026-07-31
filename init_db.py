import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

password_postgresql = os.getenv("PASSWORD_POSTGRESQL")
nama_database = os.getenv("NAMA_DATABASE")
user_database = os.getenv("USER_DATABASE")

# Connect to an existing database
with psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql) as conn:

    # Open a cursor to perform database operations
    with conn.cursor() as cur:

        # Execute a command: this creates a new table
        cur.execute("""
            CREATE TYPE pilihan_kategori AS ENUM ('Lainnya', 'Makanan', 'Minuman', 'Pakaian', 'Alat mandi', 'Tagihan Rumah', 'Transportasi', 'Telepon', 'Sosial', 'Perbaikan', 'Kesehatan', 'Olahraga', 'Hiburan', 'Pendidikan');
            CREATE TYPE pilihan_tipe AS ENUM('Pengeluaran', 'Pemasukan');     
            CREATE TABLE transaksi (
                    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
                    nama VARCHAR(64) NOT NULL,
                    nominal INTEGER NOT NULL,
                    catatan VARCHAR(255),
                    kategori pilihan_kategori NOT NULL,
                    tanggal TIMESTAMPTZ NOT NULL,
                    tipe pilihan_tipe NOT NULL,
                    chat_id VARCHAR(32)
                    );
            """)
        conn.commit()