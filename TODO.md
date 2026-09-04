# TODO 3 SEPT:
- Ubah insert menjadi jamak, fungsinya dan skemanya menerima jamak. begitu juga fungsi lain.

# TODO keresahan:
- konteks gambar tidak bisa masuk seagai history, mungkin solusinya bikin history append ulang semua inputnya daripada kasih teks mentah mentah; dijadikan input normal biar append;
- keknya harus bikin fungsi untuk cek apakah ada file dari tingkatan apapun;
- dan kalau ada media apapun, maka bisa auto append ke input; jadi biarlah konteksnya gemuk, 
- (feedback dari kelly) kasih saldo, kasih tampilan yang cute/semi formal, jangan kaku kali; emoticon kalau minat (kaga); tampilan warna warni; loading text ganti yg lebih warming; intinya, lebih bersahabat, dan mulai bagusin front end, sesuatu yg mmg blm dilakuin;

# TODO Hosting + multi user:
Perlu dibikin set up biar bisa hosting + pembayaran;
- idealnya memakai webhook untuk nerima chat user;
- idealnya kode bagian nerima banyak input media sekaligus di rombak dan di cek ulang gmn alurnya, karena medianya akan beresiko di olah berbeda promt ketika asingkronus
- idelanya kode jadi asyc dan di migrasi makai fast api aja
- idealnya postgresql nya juga pooling, banyak workker, maybe 10? kurang lebih segitu.
- idealnya hosting backend maybe di fastapihosting atau apalah, lupa linknya, intinya hosting dari mereka sendiri, lumayan untuk testing awal.
- idealnya kode bagian telegramnya lebih modular drpd saat ini, tapi gpp untuk awal2, nanti harus rapikan tapi.
- idealnya hosting postgre mungkin di supabase aja untuk free
- idealnya pembayaran midtransnya kupake aja untuk botku
- odealnya ada tabel baru: user, kategori kustom user, pilihan mau pake history chat atau enggak, batas token untuk user (karena kalau enterpreise kemungkinan besar bakal repot kalau no limit)
- idealnya aku belajar tombol tombol dan dsb untuk bagian konfigurasi user, biar mereka bisa tentuin gaya mereka sendiri
- idealnya aku kasih free trial, atau free use, kek maybe 1 transaksi atau 2 per hari untuk satu user, hanya bisa CRUDS teks tentunya.
- idealnya aku bikin sebuah fungsi untuk menampilkan data tanpa perlu bantuan bot yang bisa dipanggil pakai command, dan fungsi2 lain juga untuk jaga2 user mau hemat token?
- idealnya aku nawarin untuk di export data semuanya ke user dalam bentuk xlxx atau teks aja bebas sih; untuk user free sih sengaja doang, biar mereka kecantol.
- [ ] Docker + deploy
- Penanganan error jaringan supaya bot tidak mati sendiri
- Pengukuran akurasi parsing

# TODO Masalah promting;
promting ternyata signifikan untuk beberapa cost, target perubahan biar lebih hemat token:
1. Perampingan beberapa promt, targetnya yang awalnya promtnya super boros dan bertele tele bisa menjadi sangat singkat.
2. Pemisahan antara 2 jenis fungsi, beberapa fungsi itu tidak akan pernah dipanggil di tahap awal kayak edit dan delete; jadi, daripada repot repot naruh semua fungsi di awal, kasih pemilihan di kode, sehingga model tier 1 hanya akan dikasih tahu apa yang diperlukan, di tier kedua baru model dikasih tahu cara makai fungsinya itupun karena mereka udah dapaat data dari model sebelumnya;
3. rampingkan beberapa konfigurasi, sehingga kek nama variabel hanya perlu di 1 teks drpd tersebar di berbagai fungsi;
4. turunkan / kasih pemilihan untuk beberapa riwayat percakapan, lalu beberapa riwayat gak usah dicatat. misal, mungkin:
* hanya kasih history percakapan span waktu 15 menit max. atau bahkan 10;
* hanya memberikan chat 5-10 chat terakhir max;
* output bot, gak perlu di masukkan ke history, cukup user aja dan output non data (kek percakapan aja gpp, kalau kek inser berthasil dsb gak perlu)
* atau, untuk kasus yang sangat singkat, interaction id dibawah 3 menit maybe atau 5 menit disimpan, lalu bisa dipakai ketika user chat dgn cepat;
5. bikin beberapa fungsi tambahan yang menggantikan kebutuhan user untuk menampilkan data, karena, ternyata menamppilkan data (terutama data basar) sangat boros token output;
* fungsi penampilan_data_baris_chat(parameter sama kek fungsi select): fungsi yang rankap sekalian sama select (atau makai select?) lalu menampilkannya dalam teks terstruktur;
* fungsi yang sama, tapi beberapa pilihan visual, kayak:
- grafik batang, garis, pie chart dsb; pake aja semacam, fungsi2 penampil; seaborn maybe atau matplotlib; 

# TODO 10 Agustus
- refactor fungsi redundant, bagian ambil file
- Ubah jadi nerima semua jenis file yang diperlukan fungsinya.
- ubah jadi photo aja beda

# TODO keresahan:
- konteks gambar tidak bisa masuk seagai history, mungkin solusinya bikin history append ulang semua inputnya daripada kasih teks mentah mentah; dijadikan input normal biar append;
- keknya harus bikin fungsi untuk cek apakah ada file dari tingkatan apapun;
- dan kalau ada media apapun, maka bisa auto append ke input; jadi biarlah konteksnya gemuk, 


# TODO 10 Agustus
- refactor fungsi redundant, bagian ambil file
- Ubah jadi nerima semua jenis file yang diperlukan fungsinya.
- ubah jadi photo aja beda

# TODO 8 Agustus
- Nambah fungsi edit di database.py, nambah skema biar LLM bisa pakai, pastikan loopnya dinamis tapi aman.
- delete juga kebetulan sama, jadinya selesaikan
- ternyata keburu semua CRUDS, saatya Input foto/struk
- ternyata dokumen juga bisa gambar, sekalian cek dokumen/gambar/ banyak media sekali upload;

## TODO 7 Agustus
- Ubah Loop LLM sehingga punya pemanggil diri sendiri lagi, pemanggilan selesai;

## TODO 6 Agustus
- Ubah struture output menjadi calling function, target awal bisa insert langsung
- Jika user edit message, maka dilakukan update

## TODO
- [*] PostgreSQL: install, rancang skema BERDASARKAN apa yang Gemini benar-benar hasilkan
- [*] Simpan transaksi hasil parsing ke database
- [*] Baca, edit, hapus transaksi
- [*] Gemini keluarkan JSON terstruktur (nominal, kategori, tipe, deskripsi) — bukan teks bebas
- [*] Validasi JSON punya field yang diharapkan sebelum dipakai; tolak kalau tidak lolos
- [*] Balas ke Telegram dengan konfirmasi yang disusun dari data hasil parsing
      Tes: kirim "beli kopi 20rb" → balasan menunjukkan 20000, makanan, pengeluaran