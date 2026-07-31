import requests
import os
from dotenv import load_dotenv
from google import genai

# Memuat seluruh variabel .env 
load_dotenv()
telegram_bot_api = os.getenv("TELEGRAM_BOT_API_KEY")
gemini_api = os.getenv("GEMINI_API_KEY")
url_telegram = f"https://api.telegram.org/bot{telegram_bot_api}"
update_id = None

client = genai.Client(api_key=gemini_api)
while True:
    # Mengirimkan request GET ke api telegram Bot dengan API yang sudah di muat update chat
    if update_id:
        response = requests.get(url = url_telegram+"/getUpdates", params={"timeout":300, "offset":update_id+1})
    else:
        response = requests.get(url = url_telegram+"/getUpdates", params={"timeout":300})
        
    if response.status_code == 200: # Jika response 200 atau success
        for item in response.json().get("result"): # Untuk setiap pesan
            if "message" in item:
                type_chat = item.get("message")
            elif "edited_message" in item:
                type_chat = item.get("edited_message")
            else:
                continue # sementara belum tahu
            
            chat_id = type_chat.get('chat').get("id") # Ambil id chat user
            text_user = type_chat.get('text', "User tidak mengirimkan text")

            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=text_user
            )
            response_gemini = interaction.output_text
            response_chat = requests.get(url = url_telegram+'/sendMessage', params={"chat_id": chat_id, "text":response_gemini}) # kirimkan pesan kepada user     
            print(response_chat.status_code)
            if response_chat.status_code == 200:
                update_id = item.get("update_id") # Ambil update_id terakhir
            else: break
        