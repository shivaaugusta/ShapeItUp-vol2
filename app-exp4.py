# --- Streamlit App Experiment 4: Korelasi Berdasarkan Bentuk ---
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
from scipy.stats import pearsonr

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")

# --- Konfigurasi dasar ---
SHAPE_FOLDER = "Shapes-All"  # folder gabungan dari semua bentuk eksperimen 3

# --- Ambil semua bentuk yang tersedia ---
SHAPE_POOL = sorted([f for f in os.listdir(SHAPE_FOLDER) if f.endswith(".png")])

if len(SHAPE_POOL) < 10:
    st.error("❌ Jumlah bentuk terlalu sedikit. Tambahkan bentuk ke folder Shapes-All.")
    st.stop()

# --- Inisialisasi state ---
if "task_index_exp4" not in st.session_state:
    st.session_state.task_index_exp4 = 0
    st.session_state.correct_exp4 = 0
    st.session_state.total_exp4 = 50

idx = st.session_state.task_index_exp4
st.title("🔍 Eksperimen 4: Evaluasi Korelasi Berdasarkan Bentuk")
st.subheader(f"Soal #{idx + 1} dari {st.session_state.total_exp4}")

# --- Pilih jumlah kategori (misal 2, 4, 6) ---
n_categories = random.choice([2, 4, 6])
selected_shapes = random.sample(SHAPE_POOL, n_categories)

# --- Generate 2 set scatterplot: satu berkorelasi tinggi, satu rendah ---
def generate_correlated_data(n_categories, high_corr=True):
    x_data = []
    y_data = []
    for _ in range(n_categories):
        x = np.random.normal(0, 1, 20)
        if high_corr:
            y = x * np.random.uniform(0.7, 1.0) + np.random.normal(0, 0.2, 20)
        else:
            y = np.random.normal(0, 1, 20)
        x_data.append(x)
        y_data.append(y)
    return x_data, y_data

left_is_high = random.choice([True, False])
left_x, left_y = generate_correlated_data(n_categories, high_corr=left_is_high)
right_x, right_y = generate_correlated_data(n_categories, high_corr=not left_is_high)

# --- Tampilkan 2 scatterplot berdampingan ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Diagram Kiri**")
    fig, ax = plt.subplots()
    for i in range(n_categories):
        shape_path = os.path.join(SHAPE_FOLDER, selected_shapes[i])
        img = Image.open(shape_path).convert("RGBA").resize((20, 20))
        im = OffsetImage(img, zoom=1.0)
        for x, y in zip(left_x[i], left_y[i]):
            ab = AnnotationBbox(im, (x, y), frameon=False)
            ax.add_artist(ab)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')
    st.pyplot(fig)

with col2:
    st.markdown("**Diagram Kanan**")
    fig, ax = plt.subplots()
    for i in range(n_categories):
        shape_path = os.path.join(SHAPE_FOLDER, selected_shapes[i])
        img = Image.open(shape_path).convert("RGBA").resize((20, 20))
        im = OffsetImage(img, zoom=1.0)
        for x, y in zip(right_x[i], right_y[i]):
            ab = AnnotationBbox(im, (x, y), frameon=False)
            ax.add_artist(ab)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')
    st.pyplot(fig)

# --- Input jawaban ---
choice = st.radio("📌 Diagram mana yang memiliki korelasi antar kategori lebih tinggi?", ["Kiri", "Kanan"])

if st.button("🚀 Submit Jawaban"):
    correct = (choice == "Kiri" and left_is_high) or (choice == "Kanan" and not left_is_high)

    if correct:
        st.session_state.correct_exp4 += 1
        st.success("✅ Jawaban benar!")
    else:
        st.error("❌ Jawaban salah.")

    # Hitung pearson avg correlation sebagai validasi korelasi
    def avg_corr(x, y):
        return np.mean([abs(pearsonr(x[i], y[i])[0]) for i in range(n_categories)])

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        idx + 1,
        n_categories,
        ", ".join(selected_shapes),
        "Kiri" if left_is_high else "Kanan",
        choice,
        "Benar" if correct else "Salah",
        round(avg_corr(left_x, left_y), 3),
        round(avg_corr(right_x, right_y), 3)
    ]

    try:
        worksheet.append_row(row)
    except Exception as e:
        st.warning(f"Gagal menyimpan: {e}")

    st.session_state.task_index_exp4 += 1
    st.rerun()

# --- Akhiran ---
if st.session_state.task_index_exp4 == st.session_state.total_exp4:
    st.success(f"🎉 Eksperimen selesai! Skor akhir Anda: {st.session_state.correct_exp4} dari 50.")
    st.balloons()
    st.stop()
