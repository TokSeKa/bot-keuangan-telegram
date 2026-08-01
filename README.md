# bot-keuangan-telegram
Aplikasi keuangan terintegrasikan LLM untuk mengurus keuangan pribadi via chat telegram.

## Kenapa ini dibuat?
Penggunaan aplikasi pencatat keuangan meminta user untuk secara aktif menuliskan transaksi pribadinya secara manual dengan pola yang rigid dan rentan pencatatan yang berantakan dan membutuhkan keinginan mental yang tinggi. Produk ini ingin mengurangi friksi yang diperlukan pengguna dalam menulis keuangan personal dengan cara membuat pencatatan sebebas mungkin. 

## Screenshot Telegram
- coming soon

## Alur sistem ini:
1. Pengguna mengirimkan pesan ke bot Telegram
2. LLM akan menerima pesan pengguna dan melakukan interpretasi terhadap pesan
3. Pydantic akan mengvalidasi respon dari LLM dan dan akan dilakukan fungsi tertentu berbasis query SQL
4. PostgreSQL akan menerima Query yang tervalidasi dan memberikan output berupa hasilnya.
5. Hasilnya akan diterima psycopg dan diteruskan ke Telegram untuk merespon user sehingga berbasis database

## Keputusan teknis dan alasannya:
* SQL Mentah bukan ORM : Fleksibilitas dan media untuk penulis mendalami Query tanpa bergantung kepada library siap pakai.
* Structured output, bukan JSON lewat instruksi prompt : Menjaga konsistensi output dari model sesuai dengan best practice LLM Gemini
* Ack update_id setelah berhasil kirim: at-least-once, duplikat lebih baik daripada data hilang
* Saldo dihitung saat dibaca, tidak disimpan : karena ada fitur ubah dan hapus untuk skala kecil lebih mudah hanya menampilkan ketika diminta dan dihtung ulang
* Balasan disusun dari RETURNING *, bukan dari teks Gemini : supaya user melihat yang benar-benar tersimpan
* Parsing di luar fungsi database, parameter biasa : supaya jalur input lain tidak perlu memalsukan bentuk JSON Gemini
* Koneksi per panggilan, bukan pool : sesuai volumenya, dan menghindari koneksi mati diam-diam

## Stack
Python, GeminiApi, PostgreSQL, TelegramBotAPI, psycopg3

## Coming soon
* Perubahan data
* Penghapusan data
* Pencarian data
* Chat dengan media non text
* dll

## Setelah mengimport project ini lakukan:
* pip install -r requirements.txt
* Buat database Postgre. Jalankan "py init_db.py" untuk struktur table yang dipakai.
* Ubah ".env.example" menjadi ".env"; Isi dengan value yang diperlukan;
* Jalankan "py main.py"