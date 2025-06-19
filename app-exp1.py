# --- Streamlit App Experiment 1 (Latihan + Eksperimen) ---
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
worksheet = client.open_by_key("1aZ0LjvdZs1WHGphqb_nYrvPma8xEG9mxfM-O1_fsi3g").worksheet("Eksperimen_1")

# --- App Title ---
st.title("🧪 Eksperimen 1: Estimasi Kategori Berdasarkan Bentuk")
st.caption("Pilih kategori (bentuk) dengan rata-rata Y tertinggi dari scatterplot di bawah.")

# --- Gabungkan semua shape dari 5 folder ---
ROOT_FOLDERS = ["Shapes-D3", "Shapes-Tableau", "Shapes-Excel", "Shapes-Matlab", "Shapes-R"]
def collect_all_shapes():
    all_shapes = []
    for folder in ROOT_FOLDERS:
        try:
            files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".png")]
            all_shapes.extend(files)
        except FileNotFoundError:
            st.warning(f"Folder '{folder}' tidak ditemukan. Lewati.")
    return sorted(list(set(all_shapes)))  # remove duplicates

SHAPE_POOL = collect_all_shapes()

if len(SHAPE_POOL) < 10:
    st.error("Jumlah total shape terlalu sedikit. Pastikan minimal 10 bentuk tersedia.")
    st.stop()

# --- Inisialisasi session state ---
if "task_index" not in st.session_state:
    st.session_state.task_index = 0
    st.session_state.correct = 0
    st.session_state.total_tasks = 53  # 3 latihan + 50 eksperimen

index = st.session_state.task_index
mode = "latihan" if index < 3 else "eksperimen"

if mode == "latihan":
    st.subheader(f"🧪 Latihan #{index + 1}")
else:
    st.subheader(f"📊 Eksperimen #{index - 2} dari 50")

# --- Setup per task (random shapes & data) ---
if f"x_data_{index}" not in st.session_state:
    N = random.randint(2, 10)
    chosen_shapes = random.sample(SHAPE_POOL, N)

    means = np.random.uniform(0.3, 1.0, N)
    target_idx = random.randint(0, N - 1)
    means[target_idx] += 0.3  # target shape lebih tinggi

    x_data = [np.random.uniform(0, 1.5, 20) for _ in range(N)]
    y_data = [np.random.normal(loc=mean, scale=0.05, size=20) for mean in means]
    shape_labels = [os.path.splitext(os.path.basename(s))[0] for s in chosen_shapes]

    st.session_state[f"x_data_{index}"] = x_data
    st.session_state[f"y_data_{index}"] = y_data
    st.session_state[f"chosen_shapes_{index}"] = chosen_shapes
    st.session_state[f"shape_labels_{index}"] = shape_labels
    st.session_state[f"target_idx_{index}"] = target_idx

# --- Load dari session_state ---
x_data = st.session_state[f"x_data_{index}"]
y_data = st.session_state[f"y_data_{index}"]
chosen_shapes = st.session_state[f"chosen_shapes_{index}"]
shape_labels = st.session_state[f"shape_labels_{index}"]
target_idx = st.session_state[f"target_idx_{index}"]

# --- Plot scatterplot ---
fig, ax = plt.subplots()
fig.patch.set_alpha(0.0)
ax.set_facecolor("white")  # atau transparent, jika kamu pakai latar khusus

for i in range(len(chosen_shapes)):
    shape_path = chosen_shapes[i]
    label = shape_labels[i]
    if not os.path.exists(shape_path):
        st.warning(f"❌ File tidak ditemukan: {shape_path}")
        continue
    img = Image.open(shape_path).convert("RGBA")
    img = img.resize((20, 20))
    im = OffsetImage(img, zoom=1.0, alpha=True)  # <= ini penting
    for x, y in zip(x_data[i], y_data[i]):
        ab = AnnotationBbox(im, (x, y), frameon=False)
        ax.add_artist(ab)
    ax.scatter([], [], label=f"Kategori {i+1} ({label})")

ax.set_xlim(-0.1, 1.6)
ax.set_ylim(-0.1, 1.6)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
st.pyplot(fig)

# --- Pilih dan submit jawaban ---
selected_label = st.selectbox("📍 Pilih kategori dengan rata-rata Y tertinggi:",
                              [f"Kategori {i+1} ({label})" for i, label in enumerate(shape_labels)])
selected_index = int(selected_label.split()[1]) - 1
true_index = target_idx

if st.button("🚀 Submit Jawaban"):
    benar = selected_index == true_index
    if benar:
        st.session_state.correct += 1
        st.success("✅ Jawaban benar!")
    else:
        st.error(f"❌ Jawaban salah. Yang benar adalah Kategori {true_index+1} ({shape_labels[true_index]})")

    if mode == "latihan" and not benar:
        st.warning("⚠️ Jawaban latihan harus benar untuk lanjut.")
        st.stop()

    if mode == "eksperimen":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = [
            timestamp,
            index - 2 + 1,
            len(chosen_shapes),
            shape_labels[selected_index],
            shape_labels[true_index],
            "Benar" if benar else "Salah",
            ", ".join([os.path.basename(f) for f in chosen_shapes])
        ]
        try:
            worksheet.append_row(response)
        except Exception as e:
            st.warning(f"Gagal simpan ke Google Sheets: {e}")

    st.session_state.task_index += 1
    st.rerun()

# --- Akhir eksperimen ---
if st.session_state.task_index >= st.session_state.total_tasks:
    st.success(f"🎉 Semua selesai! Skor akhir eksperimen Anda: {st.session_state.correct} dari 50 soal.")
    st.balloons()
