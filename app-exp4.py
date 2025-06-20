# --- Streamlit App Experiment 4 (Korelasi Pairwise Scatterplot) ---
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

# --- Folder shape ---
SHAPE_FOLDER = "Shapes-All"

# --- Mapping label visual ---
LABEL_MAP = {
    "circle-filled": "circle", "dot": "dot", "plus-filled": "plus",
    "diamond-filled": "diamond", "star-filled": "star",
    "triangle-filled": "triangle", "y-filled": "y", "square-filled": "square",
    "cross-open": "cross", "minus-open": "minus", "arrow-horizontal-open": "arrow",
    "square-x-open": "square-x", "eightline-star-open": "star",
    "triangle-unfilled": "triangle", "diamond-unfilled": "diamond", "triangle-right-unfilled": "triangle",
    "triangle-left-unfilled": "triangle", "downward-triangle-unfilled": "triangle", "diamond-plus-open": "diamond"
}

# --- Load shapes ---
def load_shapes():
    shapes = []
    for fname in sorted(os.listdir(SHAPE_FOLDER)):
        if fname.endswith(".png"):
            raw = os.path.splitext(fname)[0]
            label = LABEL_MAP.get(raw, raw)
            shapes.append((label, os.path.join(SHAPE_FOLDER, fname)))
    return shapes

SHAPES = load_shapes()

# --- Halaman judul ---
st.title("🔍 Eksperimen 4: Korelasi Berdasarkan Bentuk")
st.markdown("Pilih **scatterplot** yang menurutmu **paling jelas menunjukkan korelasi antar kategori**.")

# --- Inisialisasi ---
if "task_index_exp4" not in st.session_state:
    st.session_state.task_index_exp4 = 1
    st.session_state.total_tasks_exp4 = 10  # Ubah sesuai jumlah

# --- Fungsi untuk generate satu scatterplot ---
def generate_scatterplot(shape_paths):
    n = len(shape_paths)
    base_r = np.random.uniform(0.6, 0.95)  # base correlation
    data = []
    for i in range(n):
        mean_x = np.random.uniform(0.4, 1.0)
        mean_y = mean_x * base_r + np.random.normal(0, 0.1)
        x = np.random.normal(mean_x, 0.1, 20)
        y = mean_y + np.random.normal(0, 0.1, 20)
        data.append((x, y))
    return data

# --- Buat plot dari data dan shapes ---
def plot_scatter(shape_paths, data):
    fig, ax = plt.subplots()
    for i, (x, y) in enumerate(data):
        img = Image.open(shape_paths[i]).convert("RGBA").resize((20, 20))
        im = OffsetImage(img, zoom=1.0)
        for xi, yi in zip(x, y):
            ab = AnnotationBbox(im, (xi, yi), frameon=False)
            ax.add_artist(ab)
    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, 1.5)
    ax.axis('off')
    return fig

# --- Pilih 2 kombinasi shape acak ---
shapes_A = random.sample(SHAPES, 3)
shapes_B = random.sample(SHAPES, 3)

labels_A, paths_A = zip(*shapes_A)
labels_B, paths_B = zip(*shapes_B)

plot_A = generate_scatterplot(paths_A)
plot_B = generate_scatterplot(paths_B)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### A")
    st.pyplot(plot_scatter(paths_A, plot_A))

with col2:
    st.markdown("### B")
    st.pyplot(plot_scatter(paths_B, plot_B))

# --- Pilihan user ---
selected = st.radio("📝 Pilih scatterplot yang paling jelas korelasinya:", ["A", "B"])

# --- Submit ---
if st.button("🚀 Submit Jawaban"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, st.session_state.task_index_exp4, selected,
           ", ".join(labels_A), ", ".join(labels_B),
           ", ".join([os.path.basename(p) for p in paths_A]),
           ", ".join([os.path.basename(p) for p in paths_B])]
    try:
        worksheet.append_row(row)
        st.success("Jawaban tersimpan.")
    except Exception as e:
        st.warning(f"Gagal menyimpan: {e}")

    st.session_state.task_index_exp4 += 1
    st.rerun()

# --- Akhiran ---
if st.session_state.task_index_exp4 > st.session_state.total_tasks_exp4:
    st.success("🎉 Terima kasih! Eksperimen selesai.")
    st.balloons()
    st.stop()
