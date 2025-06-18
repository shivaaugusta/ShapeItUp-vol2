# --- Streamlit App Experiment 2 (Final) ---
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# --- Autentikasi Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
client = gspread.authorize(creds)
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_2")

# --- App UI ---
st.title("🧪 Eksperimen 2: Evaluasi Palet Bentuk Visualisasi")
st.info("Pilih kategori (bentuk) yang memiliki rata-rata nilai Y tertinggi dalam scatterplot berikut. Bentuk diambil dari palet tool visualisasi populer.")

if "current_key" not in st.session_state or st.session_state.current_key != current_key:
    st.session_state.current_key = current_key
    st.session_state.x_data = [np.random.uniform(0, 1.5, 20) for _ in range(n_categories)]
    st.session_state.y_data = [np.random.normal(loc=np.random.uniform(0.3, 1.2), scale=0.1, size=20) for _ in range(n_categories)]
    st.session_state.selected_shapes = np.random.choice(shape_files, size=n_categories, replace=False)

x_data = st.session_state.x_data
y_data = st.session_state.y_data
selected_shapes = st.session_state.selected_shapes

# --- Pilihan Palet & Jumlah Kategori ---
available_palets = ["D3", "Tableau", "Excel", "Matlab", "R"]
selected_palet = st.selectbox("🎨 Pilih palet bentuk (simulasi tool):", available_palets)
n_categories = st.selectbox("🔢 Pilih jumlah kategori:", list(range(2, 11)))  # 2–10

current_key = (selected_palet, n_categories)

# --- Load shape files dari folder palet ---
palet_path = f"Shapes-{selected_palet}"
try:
    shape_files = sorted([f for f in os.listdir(palet_path) if f.endswith(".png")])
except FileNotFoundError:
    st.error(f"Folder '{palet_path}' tidak ditemukan.")
    st.stop()

# Acak N bentuk unik dari palet
if len(shape_files) < n_categories:
    st.error("Jumlah bentuk dalam palet tidak cukup.")
    st.stop()

if "selected_shapes" not in st.session_state or st.session_state.get("current_key") != (selected_palet, n_categories):
    st.session_state.selected_shapes = np.random.choice(shape_files, size=n_categories, replace=False)
selected_shapes = st.session_state.selected_shapes

# --- Generate Data Titik Scatter ---
if "scatter_data" not in st.session_state or st.session_state.get("current_key") != (selected_palet, n_categories):
    x_data = [np.random.uniform(0, 1.5, 20) for _ in range(n_categories)]
    y_data = [np.random.normal(loc=np.random.uniform(0.3, 1.2), scale=0.1, size=20) for _ in range(n_categories)]

    st.session_state.scatter_data = (x_data, y_data)
    st.session_state.current_key = (selected_palet, n_categories, "locked")

x_data, y_data = st.session_state.scatter_data

# --- Plot scatter dengan bentuk ---
fig, ax = plt.subplots()
for i in range(n_categories):
    shape_path = os.path.join(palet_path, selected_shapes[i])
    img = Image.open(shape_path).convert("RGBA").resize((20, 20))
    im = OffsetImage(img, zoom=1.0)
    for x, y in zip(x_data[i], y_data[i]):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax.add_artist(ab)
    ax.scatter([], [], label=f"Kategori {i+1}")  # dummy legend

ax.set_xlim(-0.1, 1.6)
ax.set_ylim(-0.1, 1.6)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
st.pyplot(fig)

# --- Pilihan Jawaban ---
selected_label = st.selectbox("📍 Pilih kategori dengan rata-rata Y tertinggi:", [f"Kategori {i+1}" for i in range(n_categories)])
selected_index = int(selected_label.split()[-1]) - 1
true_idx = int(np.argmax([np.mean(y) for y in y_data]))

# --- Submit & Simpan ke Spreadsheet ---
if st.button("🚀 Submit Jawaban"):
    is_correct = (selected_index == true_idx)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    response = [
        timestamp,
        selected_palet,
        n_categories,
        selected_label,
        f"Kategori {true_idx+1}",
        "Benar" if is_correct else "Salah",
        ", ".join(selected_shapes)
    ]

    try:
        worksheet.append_row(response)
        if is_correct:
            st.success(f"✅ Jawaban benar! Kategori {true_idx+1} memiliki Y tertinggi.")
        else:
            st.error(f"❌ Jawaban salah. Yang benar adalah Kategori {true_idx+1}.")
    except Exception as e:
        st.error(f"Gagal menyimpan ke Google Sheets: {e}")
