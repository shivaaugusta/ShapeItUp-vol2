# --- Streamlit App Experiment 4 (Shape and Correlation, Reproduction) ---
import streamlit as st
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Setup Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")

# --- Load all shape files ---
SHAPE_FOLDER = "Shapes-All"
if not os.path.exists(SHAPE_FOLDER):
    st.error("❌ Folder 'Shapes-All' tidak ditemukan.")
    st.stop()

shape_files = sorted([f for f in os.listdir(SHAPE_FOLDER) if f.endswith(".png")])

# --- Preferensi Awal (Pilih 3 Bentuk Favorit) ---
if "step" not in st.session_state:
    st.session_state.step = 0

if st.session_state.step == 0:
    st.title("🧡 Eksperimen 4 - Pilih Bentuk Favorit")
    st.info("Silakan pilih 3 bentuk yang menurut Anda paling menarik atau nyaman digunakan dalam visualisasi.")

    cols = st.columns(6)
    selected_shapes = st.session_state.get("favorite_shapes", set())

    for i, shape_file in enumerate(shape_files):
        col = cols[i % 6]
        path = os.path.join(SHAPE_FOLDER, shape_file)
        col.image(path, width=60)
        if col.checkbox(shape_file, key=f"fav_{i}"):
            selected_shapes.add(shape_file)
        else:
            selected_shapes.discard(shape_file)

    st.session_state.favorite_shapes = selected_shapes

    if len(selected_shapes) != 3:
        st.warning("⚠️ Harap pilih tepat 3 bentuk.")
    else:
        if st.button("➡️ Lanjut ke Eksperimen Korelasi"):
            st.session_state.step = 1
            st.rerun()

# --- Eksperimen Korelasi (Scatterplot Ganda) ---
elif st.session_state.step == 1:
    st.title("📈 Eksperimen 4 - Perbandingan Korelasi")
    st.info("Dua scatterplot ditampilkan. Pilih yang menurut Anda memiliki hubungan (korelasi) Y terhadap X paling kuat.")

    def generate_scatter(mean_corr):
        x = np.random.normal(0, 1, 100)
        y = mean_corr * x + np.random.normal(0, 1 - mean_corr, 100)
        return x, y

    corr1 = round(random.uniform(0.1, 0.9), 2)
    corr2 = round(random.uniform(0.1, 0.9), 2)
    while abs(corr1 - corr2) < 0.2:
        corr2 = round(random.uniform(0.1, 0.9), 2)

    idx_max = 0 if corr1 > corr2 else 1

    xy1 = generate_scatter(corr1)
    xy2 = generate_scatter(corr2)

    fig1, ax1 = plt.subplots()
    ax1.scatter(xy1[0], xy1[1], alpha=0.6)
    ax1.set_title("Scatterplot A")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")

    fig2, ax2 = plt.subplots()
    ax2.scatter(xy2[0], xy2[1], alpha=0.6)
    ax2.set_title("Scatterplot B")
    ax2.set_xlabel("X")
    ax2.set_ylabel("Y")

    col1, col2 = st.columns(2)
    col1.pyplot(fig1)
    col2.pyplot(fig2)

    answer = st.radio("📌 Scatterplot mana yang memiliki korelasi Y terhadap X paling kuat?", ["A", "B"])

    if st.button("🚀 Submit Jawaban"):
        benar = (answer == ["A", "B"][idx_max])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, corr1, corr2, answer, ["A", "B"][idx_max], "Benar" if benar else "Salah"]
        try:
            worksheet.append_row(row)
            if benar:
                st.success("✅ Jawaban Anda benar!")
            else:
                st.error("❌ Jawaban Anda salah.")
        except Exception as e:
            st.warning(f"Gagal menyimpan data: {e}")
