# --- Streamlit App Experiment 4 ---
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
sheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_4")

# --- Folder sumber ---
SHAPE_FOLDER = "Shapes-All"
SHAPE_FILES = [f for f in os.listdir(SHAPE_FOLDER) if f.endswith(".png")]

# --- Session State Init ---
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.total = 54

# --- Header ---
st.title("📊 Eksperimen 4: Korelasi Berdasarkan Bentuk")
st.markdown(f"### Soal #{st.session_state.step + 1} dari {st.session_state.total}")

# --- Generate Data ---
def generate_scatter_data(corr):
    x = np.random.uniform(0, 1.5, 30)
    noise = np.random.normal(0, 0.1, 30)
    if corr:
        y = x + noise
    else:
        y = np.random.uniform(0, 1.5, 30)
    return x, y

# --- Generate Shapes ---
def sample_shapes(n):
    return random.sample(SHAPE_FILES, n)

# --- Scatterplot Builder ---
def build_plot(ax, shapes, xs, ys):
    for shape_file, x_data, y_data in zip(shapes, xs, ys):
        img_path = os.path.join(SHAPE_FOLDER, shape_file)
        img = Image.open(img_path).convert("RGBA").resize((20, 20))
        im = OffsetImage(img, zoom=1.0)
        for x, y in zip(x_data, y_data):
            ab = AnnotationBbox(im, (x, y), frameon=False)
            ax.add_artist(ab)
    ax.set_xlim(-0.1, 1.6)
    ax.set_ylim(-0.1, 1.6)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle="--", alpha=0.5)

# --- Soal Baru ---
if f"data_{st.session_state.step}" not in st.session_state:
    corr_high = generate_scatter_data(True)
    corr_low = generate_scatter_data(False)

    shapes_high = sample_shapes(1)
    shapes_low = sample_shapes(1)

    if random.random() < 0.5:
        order = "AB"
        st.session_state[f"data_{st.session_state.step}"] = (corr_high, shapes_high, corr_low, shapes_low, "A")
    else:
        order = "BA"
        st.session_state[f"data_{st.session_state.step}"] = (corr_low, shapes_low, corr_high, shapes_high, "B")

# --- Load Data ---
data = st.session_state[f"data_{st.session_state.step}"]
fig, axs = plt.subplots(1, 2, figsize=(10, 4))

build_plot(axs[0], data[1], [data[0][0]], [data[0][1]])
axs[0].set_title("Plot A")

build_plot(axs[1], data[3], [data[2][0]], [data[2][1]])
axs[1].set_title("Plot B")

st.pyplot(fig)

# --- Pilihan ---
choice = st.radio("💡 Pilih plot dengan korelasi lebih tinggi:", ["A", "B"])

if st.button("🚀 Submit Jawaban"):
    correct = data[4]
    is_correct = (choice == correct)
    if is_correct:
        st.session_state.score += 1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, st.session_state.step + 1, choice, correct, "Benar" if is_correct else "Salah"]
    try:
        sheet.append_row(row)
    except Exception as e:
        st.warning(f"Gagal menyimpan ke spreadsheet: {e}")

    st.session_state.step += 1
    st.rerun()

# --- Selesai ---
if st.session_state.step == st.session_state.total:
    st.success(f"🎉 Eksperimen selesai! Skor akhir Anda: {st.session_state.score} dari {st.session_state.total}.")
    st.balloons()
    st.stop()
