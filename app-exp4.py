# --- Streamlit App Experiment 4 (Shape and Correlation) ---
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

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")

# --- Folder Sumber ---
SHAPE_FOLDER = "Shapes-All"

# --- Kumpulkan Shape ---
def get_shapes():
    return sorted([f for f in os.listdir(SHAPE_FOLDER) if f.endswith(".png")])

SHAPE_POOL = get_shapes()

# --- Inisialisasi State ---
if "task_index" not in st.session_state:
    st.session_state.task_index = 0
    st.session_state.correct = 0
    st.session_state.total_tasks = 54

index = st.session_state.task_index
mode = "latihan" if index < 3 else "eksperimen"

st.title("🔍 Eksperimen 4: Persepsi Korelasi Berdasarkan Bentuk")
st.subheader(f"{'Latihan' if mode == 'latihan' else 'Eksperimen'} #{index + 1 if mode == 'latihan' else index - 2 + 1}")

# --- Buat Soal Jika Belum Ada ---
if f"trial_data_{index}" not in st.session_state:
    shape_pair = random.sample(SHAPE_POOL, 2)

    def generate(corr):
        x = np.random.uniform(0.0, 1.5, 50)
        noise = np.random.normal(0, 1 - corr, 50)
        y = x * corr + noise
        return x, y

    corr_A = np.random.uniform(0.6, 0.9)
    corr_B = np.random.uniform(0.0, 0.4)
    xA, yA = generate(corr_A)
    xB, yB = generate(corr_B)

    st.session_state[f"trial_data_{index}"] = {
        "shapes": shape_pair,
        "xA": xA, "yA": yA,
        "xB": xB, "yB": yB,
        "corr_A": corr_A,
        "corr_B": corr_B,
        "correct": "A" if corr_A > corr_B else "B"
    }

# --- Load Data ---
data = st.session_state[f"trial_data_{index}"]

# --- Tampilkan Scatterplot ---
col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots()
    img1 = Image.open(os.path.join(SHAPE_FOLDER, data["shapes"][0])).convert("RGBA").resize((20, 20))
    im1 = OffsetImage(img1, zoom=1.0)
    for x, y in zip(data["xA"], data["yA"]):
        ab = AnnotationBbox(im1, (x, y), frameon=False)
        ax1.add_artist(ab)
    ax1.set_title("Plot A")
    ax1.set_xlim(-0.1, 1.6)
    ax1.set_ylim(-0.1, 1.6)
    ax1.grid(True)
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots()
    img2 = Image.open(os.path.join(SHAPE_FOLDER, data["shapes"][1])).convert("RGBA").resize((20, 20))
    im2 = OffsetImage(img2, zoom=1.0)
    for x, y in zip(data["xB"], data["yB"]):
        ab = AnnotationBbox(im2, (x, y), frameon=False)
        ax2.add_artist(ab)
    ax2.set_title("Plot B")
    ax2.set_xlim(-0.1, 1.6)
    ax2.set_ylim(-0.1, 1.6)
    ax2.grid(True)
    st.pyplot(fig2)

# --- Input Pilihan ---
selected = st.radio("🧠 Pilih plot dengan korelasi lebih tinggi:", ["A", "B"])

# --- Submit ---
if st.button("🚀 Submit Jawaban"):
    benar = selected == data["correct"]
    if benar:
        st.session_state.correct += 1
        st.success("✅ Jawaban benar!")
    else:
        st.error(f"❌ Salah. Jawaban benar adalah: {data['correct']}")

    if mode == "eksperimen":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
            timestamp,
            index - 2 + 1,
            data["shapes"][0],
            data["shapes"][1],
            data["corr_A"],
            data["corr_B"],
            selected,
            data["correct"],
            "Benar" if benar else "Salah"
        ]
        try:
            worksheet.append_row(row)
        except Exception as e:
            st.warning(f"Gagal simpan: {e}")

    st.session_state.task_index += 1
    st.rerun()

# --- Selesai ---
if st.session_state.task_index == st.session_state.total_tasks:
    st.success(f"🎉 Eksperimen selesai! Skor akhir Anda: {st.session_state.correct} dari {st.session_state.total_tasks - 3}.")
    st.balloons()
    st.stop()
