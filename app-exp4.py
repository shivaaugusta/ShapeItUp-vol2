# --- Eksperimen 4: Pilih Korelasi Tinggi ---
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os
import random
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

# --- Folder shapes ---
SHAPE_FOLDER = "Shapes-All"
shape_files = sorted([f for f in os.listdir(SHAPE_FOLDER) if f.endswith(".png")])

# --- Session Init ---
if "exp4_index" not in st.session_state:
    st.session_state.exp4_index = 0
    st.session_state.total_exp4 = 57
    st.session_state.exp4_answers = []

index = st.session_state.exp4_index
mode = "latihan" if index < 3 else "eksperimen"
st.title("🎯 Eksperimen 4: Berdasarkan Bentuk")
st.subheader(f"Eksperimen #{index + 1}")

# --- Generate Soal ---
if f"x_corr_{index}" not in st.session_state:
    shape_a, shape_b = random.sample(shape_files, 2)
    path_a = os.path.join(SHAPE_FOLDER, shape_a)
    path_b = os.path.join(SHAPE_FOLDER, shape_b)

    # Scatterplot A (high correlation)
    mean = np.random.uniform(0.2, 1.2, 2)
    cov = [[0.02, 0.018], [0.018, 0.02]]  # high correlation
    data_a = np.random.multivariate_normal(mean, cov, 30)

    # Scatterplot B (low correlation)
    cov = [[0.02, 0.0], [0.0, 0.02]]  # no correlation
    data_b = np.random.multivariate_normal(mean, cov, 30)

    # Randomize positions
    if random.random() < 0.5:
        left_data, right_data = data_a, data_b
        left_label, right_label = "A", "B"
        correct = "A"
    else:
        left_data, right_data = data_b, data_a
        left_label, right_label = "A", "B"
        correct = "B"

    st.session_state[f"shapes_{index}"] = (shape_a, shape_b)
    st.session_state[f"x_corr_{index}"] = (left_data, right_data)
    st.session_state[f"correct_{index}"] = correct

# --- Plot Scatter ---
shape_a, shape_b = st.session_state[f"shapes_{index}"]
data_left, data_right = st.session_state[f"x_corr_{index}"]
correct = st.session_state[f"correct_{index}"]

fig, axs = plt.subplots(1, 2, figsize=(8, 4))
for ax, data, shape_file, title in zip(axs, [data_left, data_right], [shape_a, shape_b], ["Plot A", "Plot B"]):
    img = Image.open(os.path.join(SHAPE_FOLDER, shape_file)).convert("RGBA").resize((15, 15))
    im = OffsetImage(img, zoom=1)
    for x, y in data:
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax.add_artist(ab)
    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, 1.5)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
st.pyplot(fig)

# --- Pilihan Jawaban ---
st.write("\n")
selected = st.radio("💡 Pilih plot dengan korelasi lebih tinggi:", ["A", "B"])

# --- Submit Jawaban ---
if st.button("🚀 Submit"):
    benar = selected == correct
    st.success("✅ Jawaban berhasil disimpan.")

    # Simpan ke spreadsheet
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        timestamp,
        index + 1,
        shape_a,
        shape_b,
        selected,
        correct,
        "Benar" if benar else "Salah"
    ]
    try:
        worksheet.append_row(row)
    except Exception as e:
        st.warning(f"Gagal menyimpan: {e}")

    st.session_state.exp4_index += 1
    st.rerun()

# --- Akhir ---
if st.session_state.exp4_index == st.session_state.total_exp4:
    st.success("🎉 Semua soal selesai! Terima kasih telah mengikuti eksperimen.")
    st.balloons()
    st.stop()
