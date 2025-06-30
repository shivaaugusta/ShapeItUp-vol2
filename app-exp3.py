# --- Streamlit App: Eksperimen 3 - Preferensi Bentuk ---
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
from PIL import Image

# --- Autentikasi Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_3")

# --- App Title ---
st.title("🧠 Eksperimen 3: Preferensi Bentuk Visualisasi")
st.write("Silakan pilih bentuk-bentuk di bawah ini berdasarkan preferensi Anda. Mulailah dari yang paling disukai (Ranking 1) hingga yang paling tidak disukai (Ranking 10).")

# --- Load Shapes ---
SHAPE_FOLDER = "Shapes-All"
shape_files = sorted([f for f in os.listdir(SHAPE_FOLDER) if f.endswith(".png")])

if len(shape_files) != 10:
    st.error("Eksperimen ini membutuhkan tepat 10 bentuk di folder 'Shapes-Preference'.")
    st.stop()

shape_options = [f.replace(".png", "") for f in shape_files]

# --- Tampilkan Semua Gambar Bentuk ---
st.subheader("🔍 Pratinjau Bentuk")
cols = st.columns(5)
for i, shape in enumerate(shape_files):
    with cols[i % 5]:
        st.image(os.path.join(SHAPE_FOLDER, shape), caption=shape.replace(".png", ""), width=80)

# --- Input Ranking dari 1–10 ---
st.subheader("📊 Urutkan Berdasarkan Preferensi")

rankings = []
used = set()
for i in range(10):
    choice = st.selectbox(f"Ranking {i+1}", options=["-- Pilih --"] + shape_options, key=f"rank{i}")
    rankings.append(choice)

# --- Validasi ---
submit = st.button("🚀 Submit Preferensi")
if submit:
    if "-- Pilih --" in rankings:
        st.warning("⚠️ Mohon isi semua ranking dari 1 sampai 10.")
    elif len(set(rankings)) < 10:
        st.warning("⚠️ Setiap bentuk harus dipilih satu kali. Tidak boleh duplikat.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        username = st.text_input("🧑‍💻 Masukkan nama / ID partisipan", key="user_id")

        if not username:
            st.warning("Harap isi nama atau ID terlebih dahulu.")
        else:
            response = [timestamp, username] + rankings
            try:
                worksheet.append_row(response)
                st.success("✅ Jawaban Anda berhasil disimpan. Terima kasih!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Gagal menyimpan ke spreadsheet: {e}")
