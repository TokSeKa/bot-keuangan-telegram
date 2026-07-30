import requests
import os
from dotenv import load_dotenv

# Memuat seluruh variabel .env 
load_dotenv()
telegram_bot_api = os.getenv("TELEGRAM_BOT_API_KEY")
url_telegram = f"https://api.telegram.org/bot{telegram_bot_api}"

# Mengirimkan request GET ke api telegram Bot dengan API yang sudah di muat update chat
response = requests.get(url = url_telegram+"/getUpdates")
message_to_chat = "Hai, kamu berhasil chat"
update_id = None

if response.status_code == 200: # Jika response 200 atau success
    for item in response.json().get("result"): # Untuk setiap pesan
        chat_id = item.get("message").get('chat').get("id") # Ambil id chat user
        response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":message_to_chat}) # kirimkan pesan kepada user     
        if response_chat.status_code == 200:
            update_id = item.get("update_id") # Ambil update_id terakhir
        else:
            break
    if update_id:
        requests.get(url = url_telegram+"/getUpdates", params={"offset":update_id+1}) # update_id confirm    
        