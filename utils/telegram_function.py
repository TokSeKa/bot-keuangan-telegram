import requests
import zoneinfo
from utils.database import select_transaksi

def isPinnedMessage(item, type_chat): # Mengembalikan True jika ada kunci 'pinned_message', False jika tidak ada
    return bool(item.get(type_chat, {}).get('pinned_message'))

def jawabanTelegramInsert(response_insert):
    response_waktu_balasan = response_insert['tanggal'].astimezone(zoneinfo.ZoneInfo("Asia/Jakarta")).strftime("%d %B %Y, %H:%M WIB")
    return f"""Telah tercatat!
Nama: {response_insert['nama']}
Nominal: Rp.{response_insert['nominal']}
Kategori: {response_insert['kategori']}
Waktu: {response_waktu_balasan} 
Tipe: {response_insert['tipe']}"""    

def konteksChatUserTelegram(type_chat, tanggal_input, text_user, chat_id=None, tanggal_edit=None):
    if type_chat == "edited_message": #Edited
        konteks_transaksi_edit = ""
        transaksi_lama = select_transaksi(tanggal_input, chat_id)
        for tl in transaksi_lama:
            konteks_transaksi_edit = konteks_transaksi_edit + f"""Nama: {tl['nama']}\nNominal: Rp.{tl['nominal']}\nKategori: {tl['kategori']}\nWaktu: {tl['tanggal']}\nTipe: {tl['tipe']}\nnext transaction\n"""
        
        print("\nINI ADALAH HASIL SELECT:")
        print(transaksi_lama) #DEBUG
        tipe_konteks_chat = "User melakukan edit pesan dan Ini adalah transaksi lama user berdasarkan timestamp user:\n" + konteks_transaksi_edit + f"\nIni adalah Pesan lama yang di edit User dengan tanggal input {tanggal_input}, dan tanggal edit {tanggal_edit}."
    elif type_chat == "message":
        # KALAU REPLY PESAN BEDA
        
        tipe_konteks_chat = f"Ini adalah Pesan baru dari User dengan tanggal input {tanggal_input}."
    return tipe_konteks_chat+"\nBerikut pesan user: "+ text_user # Ambil teks user / user tidak mengirimkan text
        
def getUpdatesTelegramBerkala (url_telegram, update_id=None):
    if update_id:
        return requests.get(url = url_telegram+"/getUpdates", params={"timeout":300, "offset":update_id+1})
    else:
        return requests.get(url = url_telegram+"/getUpdates", params={"timeout":300})

          