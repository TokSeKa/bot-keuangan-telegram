import psycopg
from dotenv import load_dotenv
import os
from psycopg.rows import dict_row
from contextlib import nullcontext

load_dotenv()

password_postgresql = os.getenv("PASSWORD_POSTGRESQL")
nama_database = os.getenv("NAMA_DATABASE")
user_database = os.getenv("USER_DATABASE")

# DB riwayat_percakapan

# Menginputkan riwayat percakapan;
def insert_riwayat_percakapan(chat_id, identitas, tanggal, pesan, catatan=None, conn=None):
    if conn:
        ctx = nullcontext(conn) # Biar bisa passing conn dari luar
    else:
        ctx = psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql)
    with ctx as conn:
        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(
                        "INSERT INTO riwayat_percakapan (chat_id, identitas, tanggal, pesan, catatan) VALUES (%s, %s, %s, %s, %s) RETURNING *;",
                        (chat_id, identitas, tanggal, pesan, catatan))
                    return cur.fetchone()   
        except psycopg.Error as e:
            print(f"Error occurred, transaction rolled back: {e}")

def get_riwayat_percakapan(chat_id, conn=None):
    sql_1 = "SELECT id FROM riwayat_percakapan WHERE chat_id = %s AND identitas = 'User' ORDER BY tanggal DESC LIMIT 1 OFFSET 2;"
    sql_2 = "SELECT * FROM riwayat_percakapan WHERE chat_id = %s AND id >= %s ORDER BY tanggal DESC;"
    sql_3 = "SELECT id FROM riwayat_percakapan WHERE chat_id = %s AND identitas = 'User' ORDER BY tanggal ASC LIMIT 1;"
    if conn:
        ctx = nullcontext(conn) # Biar bisa passing conn dari luar
    else:
        ctx = psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql)
    with ctx as conn:
        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(sql_1,[str(chat_id)])
                    hasil = cur.fetchone()
                    if hasil is not None:
                        parameter_id=hasil["id"]
                    else:
                        cur.execute(sql_3,[str(chat_id)])
                        hasil = cur.fetchone()
                        if hasil is not None:
                            parameter_id=hasil["id"]
                        else: 
                            return None
                    cur.execute(sql_2,[str(chat_id), parameter_id])
                    return cur.fetchall()
        except psycopg.Error as e:
            print(f"Error occurred, transaction rolled back: {e}")

# DB TRANSAKSI

# Menginputkan transaksi ke database 
def insert_transaksi(daftar_transaksi, chat_id, tanggal, conn=None):
    if conn:
        ctx = nullcontext(conn) # Biar bisa passing conn dari luar
    else:
        ctx = psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql)
    with ctx as conn:
        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    hasil_insert_semua = []
                    for trx in daftar_transaksi:
                        nama = trx.get('nama')
                        nominal = trx.get('nominal')
                        kategori = trx.get('kategori')
                        tipe = trx.get('tipe')
                        catatan = trx.get('catatan')
                        cur.execute(
                            "INSERT INTO transaksi (nama, nominal, catatan, kategori, tanggal, tipe, chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;",
                            (nama, nominal, catatan, kategori, tanggal, tipe, chat_id)
                        )
                        hasil_insert_semua.append(cur.fetchone())
                return hasil_insert_semua
        except psycopg.Error as e:
            print(f"Error occurred, transaction rolled back: {e}")
            return None
        
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
        
    sql += " ORDER BY tanggal ASC LIMIT 50" 
    
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
            
# Menginputkan transaksi ke database 
def edit_transaksi_by_id(chat_id, id_target, nama=None, nominal=None, catatan=None, kategori=None, tanggal=None, tipe=None,  conn=None):
    sql_cek_id_cocok = "SELECT * FROM transaksi WHERE id = %s AND chat_id = %s;"
    sql_update = "UPDATE transaksi SET nama = COALESCE(%s, nama), nominal = COALESCE(%s, nominal), catatan = COALESCE(%s, catatan), kategori = COALESCE(%s, kategori), tanggal = COALESCE(%s, tanggal), tipe = COALESCE(%s, tipe) WHERE id = %s AND chat_id = %s RETURNING *;"
    if conn:
        ctx = nullcontext(conn) # Biar bisa passing conn dari luar
    else:
        ctx = psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql)
    with ctx as conn:
        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    # ngecek apakah id yang mau diedit milik user
                    cur.execute(sql_cek_id_cocok,[id_target, str(chat_id)])
                    data_lama = cur.fetchone()
                    if data_lama is not None:
                        cur.execute(sql_update, (nama, nominal, catatan, kategori, tanggal, tipe, id_target, str(chat_id)))
                        data_baru = cur.fetchone()
                        return data_lama, data_baru
                    else:
                        return {'error': "ID transaksi bukan milik user!"}# ini harus dicari padanan intinya ID transaksi nya bukan milik user. 
        except psycopg.Error as e:
            print(f"Error occurred, transaction rolled back: {e}")
          
def delete_transaksi_by_id(chat_id, id_target, conn=None):
    sql_delete = "DELETE FROM transaksi WHERE id = %s AND chat_id = %s RETURNING *;"
    if conn:
        ctx = nullcontext(conn) # Biar bisa passing conn dari luar
    else:
        ctx = psycopg.connect(dbname=nama_database, user=user_database, password=password_postgresql)
    with ctx as conn:
        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(sql_delete, (id_target, str(chat_id)))
                    data_delete = cur.fetchone()
                    if data_delete is not None:
                        return data_delete
                    else:
                        return {'error': "ID transaksi bukan milik user! ATAU ID Transaksi tidak ketemu"}# ini harus dicari padanan intinya ID transaksi nya bukan milik user. 
        except psycopg.Error as e:
            print(f"Error occurred, transaction rolled back: {e}")
          