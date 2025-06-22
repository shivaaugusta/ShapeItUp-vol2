# --- Streamlit App Experiment 4: Correlation Judgement with Randomized Position ---
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

# --- Setup Spreadsheet ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")

# --- Setup Shape Folder ---
SHAPE_FOLDER = "Shapes-All"
SHAPE_POOL = [f for f in os.listdir(SHAPE_FOLDER) if f.endswith(".png")]

if len(SHAPE_POOL) < 10:
    st.error("❌ Tidak cukup bentuk dalam folder Shapes-All.")
    st.stop()

# --- State Init ---
if "exp4_index" not in st.session_state:
    st.session_state.exp4_index = 1
    st.session_state.total_trials = 30  # bisa diganti jumlah soal

index = st.session_state.exp4_index

st.title("📊 Berdasarkan Bentuk")
st.subheader(f"Eksperimen #{index}")

# --- Generate Soal Baru ---
if f"scatter_left_{index}" not in st.session_state:
    N = random.randint(2, 5)
    chosen_shapes = random.sample(SHAPE_POOL, N)

    # --- Data Plot A (korelasi tinggi) ---
    x_a = np.random.uniform(0, 1.5, 20)
    noise = np.random.normal(0, 0.05, 20)
    y_a = x_a + noise
    shape_a = random.choice(chosen_shapes)

    # --- Data Plot B (acak / korelasi rendah) ---
    x_b = np.random.uniform(0, 1.5, 20)
    y_b = np.random.uniform(0, 1.5, 20)
    shape_b = random.choice(chosen_shapes)

    # --- Acak Posisi A/B ---
    if random.choice([True, False]):
        st.session_state[f"scatter_left_{index}"] = (x_a, y_a, shape_a)
        st.session_state[f"scatter_right_{index}"] = (x_b, y_b, shape_b)
        st.session_state[f"correct_{index}"] = "A"
    else:
        st.session_state[f"scatter_left_{index}"] = (x_b, y_b, shape_b)
        st.session_state[f"scatter_right_{index}"] = (x_a, y_a, shape_a)
        st.session_state[f"correct_{index}"] = "B"

# --- Ambil State ---
x_l, y_l, shape_l = st.session_state[f"scatter_left_{index}"]
x_r, y_r, shape_r = st.session_state[f"scatter_right_{index}"]
correct = st.session_state[f"correct_{index}"]

# --- Visualisasi ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Plot A**")
    fig_a, ax_a = plt.subplots()
    img = Image.open(os.path.join(SHAPE_FOLDER, shape_l)).convert("RGBA").resize((20, 20))
    im = OffsetImage(img, zoom=1.0)
    for x, y in zip(x_l, y_l):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax_a.add_artist(ab)
    ax_a.set_xlim(0, 1.6)
    ax_a.set_ylim(0, 1.6)
    ax_a.set_xlabel("X")
    ax_a.set_ylabel("Y")
    st.pyplot(fig_a)

with col2:
    st.markdown("**Plot B**")
    fig_b, ax_b = plt.subplots()
    img = Image.open(os.path.join(SHAPE_FOLDER, shape_r)).convert("RGBA").resize((20, 20))
    im = OffsetImage(img, zoom=1.0)
    for x, y in zip(x_r, y_r):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax_b.add_artist(ab)
    ax_b.set_xlim(0, 1.6)
    ax_b.set_ylim(0, 1.6)
    ax_b.set_xlabel("X")
    ax_b.set_ylabel("Y")
    st.pyplot(fig_b)

# --- Input Jawaban ---
st.markdown("### 💡 Pilih plot dengan korelasi lebih tinggi:")
selected = st.radio("", ["A", "B"])

# --- Submit ---
if st.button("🚀 Submit"):
    benar = selected == correct
    st.success("✅ Jawaban berhasil disimpan.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, index, selected, correct, "Benar" if benar else "Salah", shape_l, shape_r]

    try:
        sheet.append_row(row)
    except Exception as e:
        st.warning(f"Gagal simpan: {e}")

    st.session_state.exp4_index += 1
    st.rerun()

# --- Akhir ---
if st.session_state.exp4_index > st.session_state.total_trials:
    st.success("🎉 Eksperimen selesai! Terima kasih telah berpartisipasi.")
    st.stop()
