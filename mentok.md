### 29 Jul 
- mentok: bingung baca docs python-telegram-bot. sebab: kejauhan, itu library, bukan API mentahnya. solusi: pakai core.telegram.org/bots/api langsung.
- mentok: getUpdates kosong terus. sebab: belum pernah chat bot-nya sejak Februari. solusi: kirim pesan dulu, baru ada isinya.
- mentok: Loop hasil response agar tidak perlu memakai index 0 sempat error. sebab: ternyata yang diloop dictionary, beda cara for loopnya, harus memakai 2 key. solusi: memakai 2 key dalam loop sesuai aturan for loop dictionaru
- mentok: error ketika mau get user id. sebab: salah masuk field ketika membaca struktur json. solusi: membaca ulang struktur map jsonnya dan mengambil sesuai path yang benar.
- mentok: sempat bingung cara mengirim pesan ke telegram via bot. sebab: belum ada ilmu dari dokumentasi. solusi: membaca dokumentasi dan menemukan sendMessage beserta parameternya, dipakai dalam konteks get.