from google import genai
from pydantic import BaseModel, Field
from typing import Literal, Optional

import os
from dotenv import load_dotenv
load_dotenv()

from utils.skema_fungsi import insert_transaksi_declaration, jawaban_telegram_penolakan_declaration, search_transaksi_multi_declaration

gemini_api = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api)

pilihan_model = [ 
    "gemini-3.5-flash-lite", # 500 RPD
    "gemini-3.1-flash-lite", # 500 RPD
    "gemini-3-flash", # 20 RPD
    "gemini-3.5-flash", # 20 RPD
    "gemini-3.6-flash", # 20 RPD
    "gemini-2.5-flash", # 20 RPD
    "gemini-2.5-flash-lite" # 20 RPD
]

# Fungsi mengirimkan ke gemini, nantinya text nya di balut dengan promt
def send_chat_llm(input_user):
    for model in pilihan_model:
        try:
            interaction  = client.interactions.create(
                    model=model,
                    input=input_user,
                    tools=[insert_transaksi_declaration, jawaban_telegram_penolakan_declaration, search_transaksi_multi_declaration],
                    generation_config={"tool_choice": "any"},
                )
            return interaction.steps
        except Exception as e:
            # Filter khusus untuk Rate Limit (Status Code 429)
            if getattr(e, "status_code", None) == 429:
                continue
            raise
    else:
        raise Exception("Semua model tersedi sudah mencapai limit harian!")